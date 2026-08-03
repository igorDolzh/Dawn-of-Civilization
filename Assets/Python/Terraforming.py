# Terraforming: converting land into sea and sea into land.
#
# Civ4 builds can only place improvements, so each direction is driven by a marker
# improvement whose construction triggers the conversion here.
#
# CvPlot::setPlotType calls erase() on any water transition, which kills every unit on
# the plot, kills any city on it, and strips the bonus, improvement, route, feature and
# rivers. Everything below exists to make that destruction predictable.
#
# Nothing here calls CyMap::recalculateAreas. setPlotType's bRecalculate argument already
# covers it: the DLL inspects the neighbours, decides whether the change merges or splits
# landmasses, and rebuilds the areas itself only when it must. recalculateAreas is brutal -
# it points every plot at FFreeList::INVALID_INDEX, destroys every CvArea, and rebuilds from
# nothing - and CvPlot::setPlotType dereferences pLoopPlot->area() without a null check
# (CvPlot.cpp:5723 and :5746). The only other callers in the mod are RegionMap, CvWBDesc and
# MapParser, all of which run at map load, with no cities or units holding area references.

from Core import *
from RFCUtils import *
from Events import handler, ERROR_LOG


### CONSTANTS ###

# how far the water-connectivity flood fill will look before assuming open ocean;
# an unbounded fill would visit the entire ocean on a 150x80 map every reclamation
iConnectivitySearchLimit = 400


### BEGIN IMPROVEMENT BUILT ###

lTerraformingWorks = [iFloodWorks, iReclamation, iShoalingWorks]


@handler("improvementBuilt")
def onTerraformingWorks(iImprovement, x, y):
	"""Record the works. Deliberately does not carry them out.

	This fires from inside CvPlot::setImprovementType (CvPlot.cpp:6389), which has not finished
	running, and the unit that completed the build is still live further up the DLL's stack.
	Converting the plot here reaches erase(), which kills every unit standing on it - that unit
	included - and then the DLL carries on through freed memory. BUILD_RECLAMATION and
	BUILD_SHOALING declare bKill, so the DLL kills the work boat itself once the event returns:
	the second kill lands on a unit Python already destroyed and the process exits silently, with
	no Python traceback because nothing Python did was wrong by the time it crashed.

	Refusing is no safer than converting. abandon() calls setImprovementType, and so does erase();
	either way setImprovementType re-enters itself on the plot it is halfway through updating.

	So nothing touches the plot until BeginGameTurn, by which point the DLL holds no reference to
	it and the build that started this has fully unwound.
	"""
	if iImprovement in lTerraformingWorks:
		data.lTerraformingQueue.append((x, y, iImprovement))


@handler("BeginGameTurn")
def processTerraformingWorks(iGameTurn):
	"""Carry out the works queued since the last turn."""
	queue = data.lTerraformingQueue
	data.lTerraformingQueue = []

	for x, y, iImprovement in queue:
		target = plot(x, y)

		# the marker can be gone by now: pillaged, or the tile captured and rebuilt
		if target.getImprovementType() != iImprovement:
			continue

		if iImprovement == iFloodWorks:
			flood(target)
		elif iImprovement == iReclamation:
			reclaim(target)
		elif iImprovement == iShoalingWorks:
			shoal(target)


### LAND -> SEA ###

def flood(target):
	"""Convert a land plot into sea, moving the working party clear first."""
	if target.isWater():
		return

	# the sea has to reach the site squarely: diagonal water is not enough to join it to the ocean
	if not isCardinallyAdjacentToWater(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_NOT_CARDINAL')
		return

	# erase() would destroy a city outright, and flooding beside one silently guts its yields
	if isAdjacentToCity(target) or city(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_BLOCKED_BY_CITY')
		return

	iOwner = target.getOwner()
	name = describe(target)

	evacuate(target)

	# everything still standing here is destroyed by erase() inside setPlotType
	trace('flood', target, 'setPlotType')
	target.setPlotType(PlotTypes.PLOT_OCEAN, True, True)
	trace('flood', target, 'done')

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

	# Core.move, not setXY: CyUnit::setXY takes (x, y, bGroup, bUpdate, bShow) and calling it with
	# two arguments raises ArgumentError from Boost.Python. move() supplies them and skips units
	# that are already there.
	for unit in units.at(target).land():
		move(unit, refuge)


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

	trace('reclaim', target, 'setPlotType')
	target.setPlotType(PlotTypes.PLOT_LAND, True, True)

	# setPlotType applies the global LAND_TERRAIN default; match the neighbours instead
	if iTerrain >= 0:
		trace('reclaim', target, 'setTerrainType %d' % iTerrain)
		target.setTerrainType(iTerrain, True, True)

	trace('reclaim', target, 'done')

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


### DEEP OCEAN -> SHALLOW COAST ###

def shoal(target):
	"""Raise the seabed of a deep ocean plot until it becomes coast.

	The gentlest of the three. Both terrains are water, so this never calls setPlotType and
	therefore never reaches erase(): no unit is destroyed, no bonus, route or improvement is
	stripped, and no city can be harmed. Only what the tile is changes.

	What it buys is real even so - coast is workable by a city, carries a harbour's trade
	connection, and lets coastal ships pass where they could not before.
	"""
	if not target.isWater():
		return

	if target.getTerrainType() != iOcean:
		return

	# a seabed is raised from somewhere: there has to be shallower ground already adjacent
	if not isAdjacentToShallows(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_NOT_SHALLOW')
		return

	iOwner = target.getOwner()
	name = describe(target)

	# the other two have their marker stripped by erase(); this one has to clear its own, or the
	# works sit on the finished coast forever. Removing it fires improvementDestroyed, not
	# improvementBuilt, so this does not come back through onTerraformingWorks.
	target.setImprovementType(-1)
	target.setTerrainType(iCoast, True, True)

	announce(iOwner, 'TXT_KEY_TERRAFORMING_SHOALED', name, target)


### SHARED ###

def trace(operation, target, step):
	"""Breadcrumb through the steps that can end the process without raising.

	setPlotType runs a great deal of C++ - erase(), plot groups, area bookkeeping - and when that
	dies it takes the process with it, leaving no Python exception and so no traceback. The only
	evidence of how far the conversion got is what reached disk beforehand, so each step is
	written before it is attempted. fileLog writes through on every call.
	"""
	try:
		x, y = location(target)
		fileLog(ERROR_LOG, "terraforming: %s (%d, %d) %s\n" % (operation, x, y, step))
	except:
		pass

def isAdjacentToShallows(target):
	"""Whether anything next to this plot is land or already shallow water."""
	return plots.ring(target, radius=1).where(
		lambda p: not p.isWater() or p.getTerrainType() != iOcean).any()


def isCardinallyAdjacentToWater(target):
	"""Whether the plot due north, south, east or west of this one is water.

	Not the same question as "is there water next to it", and the difference decides whether the
	flooded tile is part of the sea or a puddle.

	CvPlot::setPlotType puts a new water plot into a neighbouring water area, and to find one it
	searches the four cardinal directions only - CvPlot.cpp:5715, under a comment conceding the
	point: "XXX might want to change this if we allow diagonal water movement". Land is searched
	in all eight (:5740), so reclaim() does not have this problem.

	Find nothing and it does not give up; it calls CvMap::addArea and hands the tile a private
	one-plot ocean (:5817-5823). The result looks like sea and behaves like a moat: no ship can
	enter it, because Civ4 pathfinding never crosses an area boundary.
	"""
	x, y = location(target)
	cardinal = [wrap(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
	return plots.of(cardinal).where(lambda p: p.isWater()).any()


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
