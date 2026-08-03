# Terraforming: converting land into sea and sea into land.
#
# Civ4 builds can only place improvements, so each direction is driven by a marker
# improvement whose construction triggers the conversion here.
#
# CvPlot::setPlotType calls erase() on any water transition, which kills every unit on
# the plot, kills any city on it, and strips the bonus, improvement, route, feature and
# rivers. Everything below exists to make that destruction predictable.

from Core import *
from RFCUtils import *
from Events import handler


### CONSTANTS ###

# how far the water-connectivity flood fill will look before assuming open ocean;
# an unbounded fill would visit the entire ocean on a 150x80 map every reclamation
iConnectivitySearchLimit = 400


### BEGIN IMPROVEMENT BUILT ###

@handler("improvementBuilt")
def onTerraformingWorks(iImprovement, x, y):
	if iImprovement == iFloodWorks:
		flood(plot(x, y))
	elif iImprovement == iReclamation:
		reclaim(plot(x, y))


### LAND -> SEA ###

def flood(target):
	"""Convert a land plot into sea, moving the working party clear first."""
	if target.isWater():
		return

	# the sea has to be able to reach the site
	if not isAdjacentToWater(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_NOT_COASTAL')
		return

	# erase() would destroy a city outright, and flooding beside one silently guts its yields
	if isAdjacentToCity(target) or city(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_BLOCKED_BY_CITY')
		return

	iOwner = target.getOwner()
	name = describe(target)

	evacuate(target)

	# everything still standing here is destroyed by erase() inside setPlotType
	target.setPlotType(PlotTypes.PLOT_OCEAN, True, True)
	map.recalculateAreas()

	announce(iOwner, 'TXT_KEY_TERRAFORMING_FLOODED', name, target)


def evacuate(target):
	"""Move surviving units off the plot before it becomes water.

	Land units are relocated to an adjacent land plot; anything with nowhere to go is
	left to erase(). The unit that performed the build is consumed either way for
	BUILD_RECLAMATION, but BUILD_FLOOD leaves its worker standing on the tile.
	"""
	refuge = plots.ring(target, radius=1).where(lambda p: not p.isWater() and not p.isPeak()).first()
	if refuge is None:
		return

	x, y = location(refuge)
	for unit in units.at(target).land():
		unit.setXY(x, y)


### SEA -> LAND ###

def reclaim(target):
	"""Convert a sea plot into land, refusing if it would strand ships or landlock a city."""
	if not target.isWater():
		return

	# only coastal water can be filled: raising land in open ocean has nothing to build from
	if not isAdjacentToLand(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_NOT_COASTAL')
		return

	landlocked = firstCityLosingCoast(target)
	if landlocked:
		abandon(target, 'TXT_KEY_TERRAFORMING_WOULD_LANDLOCK', landlocked.getName())
		return

	if wouldSeverWater(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_WOULD_STRAND')
		return

	iOwner = target.getOwner()
	name = describe(target)
	iTerrain = surroundingTerrain(target)

	target.setPlotType(PlotTypes.PLOT_LAND, True, True)

	# setPlotType applies the global LAND_TERRAIN default; match the neighbours instead
	if iTerrain >= 0:
		target.setTerrainType(iTerrain, True, True)

	map.recalculateAreas()

	announce(iOwner, 'TXT_KEY_TERRAFORMING_RECLAIMED', name, target)


def surroundingTerrain(target):
	"""The most common terrain among adjacent land plots, so reclaimed desert stays desert."""
	terrains = [p.getTerrainType() for p in plots.ring(target, radius=1) if not p.isWater()]
	terrains = [t for t in terrains if t >= 0]
	if not terrains:
		return -1

	# max()'s key argument arrived in Python 2.5 and Civ4 embeds 2.4, so compare (count, terrain)
	# tuples instead. Ties break on the terrain id, which is at least deterministic.
	return max([(terrains.count(t), t) for t in set(terrains)])[1]


def firstCityLosingCoast(target):
	"""A city that would be cut off from the sea if this plot became land."""
	for p in plots.ring(target, radius=1):
		nearby = city(p)
		if not nearby or nearby.isNone():
			continue
		if not plots.ring(p, radius=1).where(lambda q: q.isWater() and location(q) != location(target)).any():
			return nearby
	return None


def wouldSeverWater(target):
	"""True if filling this plot would split the surrounding water into separate pools.

	Ships in a sealed pocket are stranded permanently, which the AI never recovers from.
	"""
	neighbours = [p for p in plots.ring(target, radius=1) if p.isWater()]
	if len(neighbours) < 2:
		return False

	reached = floodFill(neighbours[0], target)

	# if the search hit its limit we are in open ocean, which cannot be severed by one plot
	if reached is None:
		return False

	return any(location(p) not in reached for p in neighbours[1:])


def floodFill(start, excluded):
	"""Locations of water reachable from start without crossing `excluded`.

	Returns None if the search exceeds iConnectivitySearchLimit, meaning open water.
	"""
	tExcluded = location(excluded)
	seen = set([location(start)])
	queue = [start]

	while queue:
		if len(seen) > iConnectivitySearchLimit:
			return None

		current = queue.pop()
		for p in plots.ring(current, radius=1):
			t = location(p)
			if t == tExcluded or t in seen or not p.isWater():
				continue
			seen.add(t)
			queue.append(p)

	return seen


### SHARED ###

def isAdjacentToWater(target):
	return plots.ring(target, radius=1).where(lambda p: p.isWater()).any()


def isAdjacentToLand(target):
	return plots.ring(target, radius=1).where(lambda p: not p.isWater()).any()


def isAdjacentToCity(target):
	return plots.ring(target, radius=1).where(lambda p: p.isCity()).any()


def abandon(target, key, *format):
	"""Cancel the works: remove the marker and tell the owner why."""
	iOwner = target.getOwner()
	target.setImprovementType(-1)
	if iOwner >= 0:
		message(iOwner, key, *format, **dict(
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iRed, location=target))


def announce(iOwner, key, name, target):
	if iOwner >= 0:
		message(iOwner, key, name,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iYellow, location=target)


def describe(target):
	"""A place name for the message: the nearest city, or the plot's own coordinates."""
	nearby = closestCity(target)
	if nearby and not nearby.isNone():
		return nearby.getName()
	x, y = location(target)
	return "(%d, %d)" % (x, y)
