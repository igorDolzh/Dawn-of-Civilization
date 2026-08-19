# Terraforming: converting land into sea and sea into land.
#
# Civ4 builds can only place improvements, so each direction is driven by a marker
# improvement whose construction triggers the conversion here.
#
# CvPlot::setPlotType calls erase() on any water transition, which kills every unit on
# the plot, kills any city on it, and strips the bonus, improvement, route, feature and
# rivers. Everything below exists to make that destruction predictable.
#
# The areas are the hard part, and this file used to be wrong about them twice.
#
# It first said nothing here calls CyMap::recalculateAreas, and left the decision to setPlotType's
# bRecalculate argument. That was true and useless: setPlotType makes the call itself, at
# CvPlot.cpp:5804, whenever the change joins two areas or the neighbours cross more than two area
# boundaries. It does so holding CvArea pointers in locals taken at :5716 and :5742, which
# recalculateAreas has just destroyed. Declining to make a call is not the same as it not happening.
#
# It then refused those conversions instead, which kept the game alive at the cost of the only
# works worth doing - a strait filled to join two islands, a channel cut so a navy can pass.
#
# What it does now is take the rebuild away from the DLL and do it here: setPlotType with
# bRecalculate false, so the DLL never holds an area pointer at all, then CyMap::recalculateAreas
# from Python, on a BeginGameTurn, with no conversion frame on the stack. That this is safe rests
# on one fact - nothing in the game caches an area. CvCity::area, CvUnit::area and
# CvSelectionGroup::area all resolve through plot()->area() on every call, so once the plots are
# re-assigned, every city, unit and stack is correct again by construction.
#
# It is also more correct than what it replaced. A fill that cuts an ocean in two now produces two
# areas, which is the truth, instead of one area that no longer connects.

from Core import *
from RFCUtils import *
from Events import handler, ERROR_LOG


### CONSTANTS ###

# how far from the site the water-connectivity check will look. An unbounded fill would visit
# the whole ocean on a 150x80 map every reclamation; a window is enough because only a narrow
# neck can be severed by a single plot. Water beyond it is treated as unreachable, so raising
# this makes reclamation more permissive, not less.
iConnectivityRadius = 4


# Whether a conversion that joins two landmasses, or two seas, is carried out or refused.
#
# On, these are the interesting works: filling the strait between two islands to make one, or
# cutting a channel that lets a navy pass between two oceans. Both require every area on the map to
# be rebuilt, which is the one operation in this file that can end the process - see convert() for
# why it is survivable when done from here and not survivable where the DLL does it.
#
# Set to False and such works are abandoned with a message instead. That is the conservative
# behaviour and it costs a work boat; this is the one setting in the file worth reaching for if
# terraforming ever starts taking the game down again.
bAllowMerging = True


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

	# open sea has to reach the site squarely, or the new tile is a puddle rather than a bay
	if not isCardinallyAdjacentToSea(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_NOT_CARDINAL')
		return

	# only the city's own tile is refused: erase() inside setPlotType calls pCity->kill() and the
	# city is gone, with no warning and nothing to undo it. Flooding a neighbouring tile is a
	# different matter entirely - the city merely works water where it worked land, and since
	# CvCity::isCoastal defers to plot()->isCoastalLand() and is evaluated live, an inland city
	# with the sea brought up to its edge becomes coastal and can build a harbour.
	if city(target):
		abandon(target, 'TXT_KEY_TERRAFORMING_BLOCKED_BY_CITY')
		return

	# the same from the other side: a channel joining two separate bodies of water
	bMerging = wouldRecalculateAreas(target, True)

	if bMerging and not bAllowMerging:
		abandon(target, 'TXT_KEY_TERRAFORMING_WOULD_REBUILD')
		return

	iOwner = target.getOwner()
	name = describe(target)

	evacuate(target)

	# everything still standing here is destroyed by erase() inside setPlotType
	convert(target, PlotTypes.PLOT_OCEAN, bMerging, 'flood')

	# a flooded tile is only useful if it joined the sea. isLake is a property of the area it was
	# put into, so this is the one check that says whether a ship can actually get here
	trace('flood', target, 'done: area %d, %d tiles, lake=%s' % (
		target.getArea(), map.getArea(target.getArea()).getNumTiles(), target.isLake()))

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
	"""Convert a sea plot into land, refusing only if it would landlock a city."""
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

	# Two different ways this fill changes the shape of the world: it can join two landmasses into
	# one, or cut one ocean into two. Both used to be refused, and severing was refused for a reason
	# that no longer holds - the danger was never the split itself, it was that the DLL does not
	# re-examine water when a plot becomes land, so both halves keep one area id and every navy
	# believes it can sail between them.
	#
	# Rebuilding the areas answers that properly instead of avoiding it. The two halves come back as
	# two areas, which is the truth, and no ship plans a route that does not exist.
	bRebuild = wouldSeverWater(target) or wouldRecalculateAreas(target, False)

	if bRebuild and not bAllowMerging:
		abandon(target, 'TXT_KEY_TERRAFORMING_WOULD_REBUILD')
		return

	iOwner = target.getOwner()
	name = describe(target)
	iTerrain = surroundingTerrain(target)

	convert(target, PlotTypes.PLOT_LAND, bRebuild, 'reclaim')

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
	"""True unless the water around this plot provably stays joined without it.

	Filling a strait splits one ocean in two, and nothing notices. The plot became land, so
	CvPlot::setPlotType only re-examines land areas (CvPlot.cpp:5740); the water is never looked
	at again and both halves keep one area id. Civ4 treats the area as its cheap "can a ship get
	there" test, so every navy then believes the far side is reachable, runs an A* over the whole
	ocean, and fails - every unit, every turn, until the game is unplayable.

	So this fails closed. If connectivity cannot be proved within iConnectivityRadius the answer
	is "it might sever" and the works are refused. Refusing a legal fill costs a work boat;
	allowing an illegal one costs the game.
	"""
	neighbours = [p for p in plots.ring(target, radius=1) if p.isWater()]
	if len(neighbours) < 2:
		return False

	reached = floodFill(neighbours[0], target)

	return any(location(p) not in reached for p in neighbours[1:])


def floodFill(start, excluded):
	"""Locations of water reachable from start without crossing `excluded`.

	Bounded to a window around the excluded plot rather than by a global budget. A plot can only
	sever water by being a cut vertex, which means a narrow neck, and necks are narrow by
	definition - so if the neighbours rejoin at all they rejoin close by. Water outside the
	window is not searched and so does not count as reached, which is what makes the caller
	conservative rather than optimistic.
	"""
	tExcluded = location(excluded)
	ex, ey = tExcluded
	seen = set([location(start)])
	queue = [start]

	while queue:
		current = queue.pop()
		for p in plots.ring(current, radius=1):
			t = location(p)
			if t == tExcluded or t in seen or not p.isWater():
				continue
			if plotDistance(t[0], t[1], ex, ey) > iConnectivityRadius:
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


def convert(target, iPlotType, bMerging, operation):
	"""Change the plot, rebuilding the map's areas afterwards when the change joins two of them.

	setPlotType rebuilds them itself when it must, and that is the one thing it must not do. It
	takes CvArea pointers into locals at CvPlot.cpp:5716 and :5742 and then calls recalculateAreas
	at :5804, which destroys every area those pointers refer to. What follows is not a Python error
	and leaves no traceback.

	Passing bRecalculate=False skips that entire block, so the DLL never takes an area pointer at
	all, and the rebuild is done from here instead: at Python top level, on a BeginGameTurn, with no
	conversion frame anywhere on the stack.

	That this is safe from here and not from there rests on one fact worth stating plainly, because
	the whole feature depends on it. Nothing caches an area. CvCity::area, CvUnit::area and
	CvSelectionGroup::area all resolve through plot()->area() on every call - CvCity.cpp:6575,
	CvUnit.cpp:10927, CvSelectionGroup.cpp:3259 - so the moment the plots are re-assigned, every
	city, unit and stack on the map is correct again by construction. The only references that
	cannot survive are the ones the DLL holds in local variables across its own call, and this way
	it holds none.

	Between the two calls the plot is land carrying a water area, or the reverse. Nothing runs in
	that gap.
	"""
	if not bMerging:
		target.setPlotType(iPlotType, True, True)
		return

	trace(operation, target, 'setPlotType, deferring the area rebuild')
	target.setPlotType(iPlotType, False, True)

	trace(operation, target, 'recalculateAreas')
	map.recalculateAreas()
	trace(operation, target, 'areas rebuilt')


### THE AREA TRAP ###

# Neighbour offsets in DIRECTION_NORTH..DIRECTION_NORTHWEST order, matching aiPlotDirectionX and
# aiPlotDirectionY in CvGlobals.cpp:262. The order is not decoration: the transition count below
# walks the neighbours in exactly this sequence, and a different one gives a different answer.
lDirections = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


def neighbourAreas(target):
	"""Area id of each of the eight neighbours in direction order, None where the map ends."""
	x, y = location(target)
	areas = []

	for dx, dy in lDirections:
		iY = y + dy

		# plotDirection returns NULL past the poles. Core.wrap clamps y instead, which would report
		# the edge row twice and give a different count from the one the DLL arrives at.
		if iY < 0 or iY >= iWorldY:
			areas.append(None)
			continue

		areas.append(plot((x + dx) % iWorldX, iY).getArea())

	return areas


def wouldRecalculateAreas(target, bWater):
	"""Whether setPlotType would rebuild every area on the map to make this change.

	This is the crash. Not a Python error and not something this module does - the DLL does it
	itself, at CvPlot.cpp:5804, in the middle of the conversion:

	    if (bRecalculateAreas) { GC.getMapINLINE().recalculateAreas(); }

	recalculateAreas points every plot at FFreeList::INVALID_INDEX, destroys every CvArea and
	rebuilds from nothing, while cities, units and plot groups all hold area references taken
	before it ran. The header of this file already explains why that cannot be survived; what it
	did not know is that declining to call it is not enough, because setPlotType reaches it without
	being asked.

	So the condition is predicted here instead, exactly as CvPlot.cpp:5709-5804 computes it. Either
	branch is enough for the DLL:

	  - the new plot touches more than one area of the element it is becoming. For a reclamation
	    that means two separate landmasses, which is precisely what filling the strait between two
	    islands does; for a flood, two cardinally adjacent bodies of water.
	  - walking the eight neighbours in direction order crosses more than two area boundaries, which
	    a broken coastline manages easily.

	Fails closed, like wouldSeverWater above it and for the same reason. Refusing a fill costs a
	work boat. Allowing this one costs the game, every time the save is loaded, because the queue
	that carries it is saved with everything else.
	"""
	areas = neighbourAreas(target)

	matching = set()

	if bWater:
		# cardinal only, because that is all setPlotType looks at for water, under a comment
		# conceding the point: diagonal water movement is not allowed
		lConsidered = [areas[0], areas[2], areas[4], areas[6]]
	else:
		lConsidered = areas

	for iArea in lConsidered:
		if iArea is None:
			continue

		if map.getArea(iArea).isWater() == bWater:
			matching.add(iArea)

	if len(matching) > 1:
		return True

	# the transition count, started from the last direction exactly as the DLL starts it
	iCount = 0
	iLast = areas[-1]

	for iArea in areas:
		if iArea != iLast:
			iCount += 1

		iLast = iArea

	return iCount > 2


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


def isCardinallyAdjacentToSea(target):
	"""Whether the plot due north, south, east or west of this one is open sea.

	Two conditions, and the flooded tile is navigable only if both hold.

	Cardinal, because CvPlot::setPlotType puts a new water plot into a neighbouring water area and
	searches the four cardinal directions only to find one - CvPlot.cpp:5715, under a comment
	conceding the point: "XXX might want to change this if we allow diagonal water movement".
	Land is searched in all eight (:5740), so reclaim() does not have this problem. Find nothing
	and it does not give up: it calls CvMap::addArea and hands the tile a private one-plot ocean
	(:5817-5823), which no ship can enter because Civ4 never paths across an area boundary.

	Sea rather than merely water, because the tile inherits whichever area it joins. A water body
	of LAKE_MAX_AREA_SIZE tiles or fewer - nine, by GlobalDefines - is a lake, and CvArea::isLake
	is a property of the area, not of the plot. Flood next to a pond and the tile joins the pond,
	the pond is still a pond, and ocean-going ships are barred from all of it.

	Plots.sea() is exactly water that is not a lake.
	"""
	x, y = location(target)
	cardinal = [wrap(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
	return plots.of(cardinal).sea().any()


def isAdjacentToLand(target):
	return plots.ring(target, radius=1).where(lambda p: not p.isWater()).any()


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
