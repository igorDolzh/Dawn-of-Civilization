# Cultivation and restocking: spreading a crop, a herd or a shoal you already keep onto ground
# or water that will take it.
#
# Not the invention of a resource, the spread of one. You may only sow what you already have
# connected, so this is the same diffusion the mod already models when a civilization group meets
# another (Resources.spreadCivGroupResources) - the potato reaching Europe rather than Europe
# discovering the potato. Without that rule a bronze age European could conjure maize.
#
# One build per element rather than one per resource. Civ4 builds are fixed actions, so a
# "plant corn", "plant wheat" and so on would put a row of mostly greyed-out buttons on the
# worker; instead the ground and the empire's own resources decide between them, which also
# makes the rule visible rather than hiding it behind disabled options. Cultivate is the
# worker's, on grass and plains; Restock is the work boat's, on coast and ocean.
#
# Deferred to BeginGameTurn for the reason Terraforming is: improvementBuilt fires from inside
# CvPlot::setImprovementType, and clearing the marker from there re-enters the function that is
# still running.

from Core import *
from Events import handler, ERROR_LOG

import Resources


### CONSTANTS ###

# What can be cultivated, in the order it is preferred. Every land resource the game treats as
# food: BONUSCLASS_GRAIN and BONUSCLASS_LIVESTOCK, plus the rest of what carries +1 health, which
# is how Civ4 marks something as eaten rather than smelted or worn.
#
# The order matters more than it looks. When nothing suits the ground the first entry the empire
# holds is planted regardless, so this runs from the staples outward: grains, then orchard crops,
# then herds, then the specialities. A tile that could take corn should not come out as salt
# because salt happened to be listed first.
lCultivable = [
	iCorn, iRice, iWheat, iMillet, iPotato,
	iCitrus, iDates, iOlives, iBanana, iSugar,
	iCow, iSheep, iPig,
	iDeer, iCamel, iSalt,
]

# What can be restocked. There is no bonus class for the sea, so unlike the land list this one is
# a judgement: the marine resources that reproduce, and can therefore be seeded and left to breed.
# Pearls belong here - pearl culture is a real and old industry - and amber does not, being fossil
# resin that washes ashore rather than anything that can be stocked.
lStockable = [iFish, iClam, iCrab, iWhales, iPearls]

# which improvement draws on which list
dWorks = {
	iCultivation: lCultivable,
	iRestocking: lStockable,
}


### TRACE ###

def trace(message):
	"""Write to Logs\\Errors.log.

	Every gate here is silent: an improvement id that does not match, a resource the empire does
	not have, a plot canHaveBonus rejects. Each one ends with nothing on the tile and nothing on
	screen, which is indistinguishable from the handler never running at all.
	"""
	try:
		fileLog(ERROR_LOG, "cultivation: %s\n" % message)
	except:
		pass


### BEGIN IMPROVEMENT BUILT ###

@handler("improvementBuilt")
def onCultivation(iImprovement, x, y):
	"""Record the works; what grew is decided next turn.

	Nothing may touch the plot here. This fires from inside CvPlot::setImprovementType
	(CvPlot.cpp:6389) and clearing the marker would re-enter it on the plot it is halfway through
	updating - the defect that made reclamation take the whole process down.
	"""
	trace("built improvement %d at (%d, %d); cultivation=%d restocking=%d" % (
		iImprovement, x, y, iCultivation, iRestocking))

	if iImprovement in dWorks:
		data.lCultivationQueue.append((x, y, iImprovement))
		trace("queued (%d, %d); queue now %d" % (x, y, len(data.lCultivationQueue)))


@handler("BeginGameTurn")
def processCultivation(iGameTurn):
	"""Decide what grew on each cultivated or restocked tile."""
	queue = data.lCultivationQueue
	data.lCultivationQueue = []

	if queue:
		trace("processing %d queued works" % len(queue))

	for x, y, iImprovement in queue:
		target = plot(x, y)

		# the marker can be gone by now: pillaged, or the tile captured and rebuilt
		if target.getImprovementType() != iImprovement:
			trace("(%d, %d) marker gone: expected %d, found %d" % (
				x, y, iImprovement, target.getImprovementType()))
			continue

		cultivate(target, dWorks[iImprovement])


def cultivate(target, lChoices):
	"""Put a resource on the plot, if the owner keeps one that will live there."""
	iOwner = target.getOwner()
	x, y = location(target)

	# the works are over either way, so the marker goes before anything else can fail
	target.setImprovementType(-1)

	if iOwner < 0:
		return

	trace("(%d, %d) owner=%d terrain=%d feature=%d hills=%s bonus=%d" % (
		x, y, iOwner, target.getTerrainType(), target.getFeatureType(),
		target.isHills(), target.getBonusType(-1)))

	iBonus = choose(target, iOwner, lChoices)
	trace("(%d, %d) chose %d" % (x, y, iBonus))

	if iBonus < 0:
		message(iOwner, 'TXT_KEY_CULTIVATION_BARREN',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iRed, location=target)
		return

	# Resources.createResource rather than setBonusType: it keeps the bonus variety art, repairs
	# an improvement the new resource invalidates, and notifies the owner the same way every other
	# resource appearing on the map does
	Resources.createResource(x, y, iBonus, createTextKey='TXT_KEY_CULTIVATION_GREW')


def choose(target, iOwner, lChoices):
	"""The best thing the owner already keeps that this ground or water will support, or -1.

	canHaveBonus is the DLL's own test and covers everything that matters: a bonus already on the
	plot, peaks, hills, the terrain and feature the bonus needs, and latitude. Reimplementing any
	of that in Python would only be a second opinion that could disagree with the first.

	Two passes. The ground gets first say: if anything the empire keeps would grow here on its
	own, that is what is planted, so a grassland becomes corn rather than whatever happens to head
	the list. Only when nothing fits does the ground stop being consulted.

	That second pass is the loose part, and it is deliberate. canHaveBonus enforces the rules that
	decide where a resource appears when the world is generated - terrain, feature, hills,
	latitude - and those describe where a thing arises unaided, not where people can establish it.
	An empire holding only pigs, which want grassland, could otherwise cultivate almost nowhere.

	What survives is the rule that matters: you can only spread what you already have. Without it
	there would be nothing to choose between seven resources and every tile would come out corn.
	"""
	held = holdings(iOwner)
	available = []
	dCount = {}

	for iBonus in lChoices:
		iConnected = player(iOwner).getNumAvailableBonuses(iBonus)
		iHeld = held.get(iBonus, 0)

		trace("  candidate %-3d connected=%-3d held=%-3d natural=%s" % (
			iBonus, iConnected, iHeld, target.canHaveBonus(iBonus, True)))

		if iConnected > 0 or iHeld > 0:
			available.append(iBonus)
			dCount[iBonus] = iConnected + iHeld

	if not available:
		return -1

	fitting = [iBonus for iBonus in available if target.canHaveBonus(iBonus, True)]

	if fitting:
		return rarest(fitting, dCount)

	# Nothing belongs here naturally, so plant it anyway. The one thing not overridden is a
	# resource already on the tile: createResource would replace it without a word, and losing
	# the gold under your feet to a herd of pigs is not a trade anyone asked for.
	if target.getBonusType(-1) >= 0:
		trace("  tile already carries %d, leaving it alone" % target.getBonusType(-1))
		return -1

	iBonus = rarest(available, dCount)
	trace("  nothing fits naturally, planting %d anyway" % iBonus)
	return iBonus


def rarest(lBonuses, dCount):
	"""Whichever of these the empire has least of.

	Order used to decide this, and order is self-reinforcing: plant one wheat and the empire now
	holds wheat, and wheat sits third in the list, so it beat everything after it on every tile
	from then on. The first success chose every cultivation that followed, which is why a player
	reported finding nothing but wheat.

	Counting instead makes each planting argue against the next one of its kind, so a cultivated
	resource becomes less attractive precisely because it succeeded. Ties break on list order,
	which keeps the result deterministic - it must not depend on dictionary iteration, and it must
	not draw from the synced random number generator either.
	"""
	iBest = -1
	iFewest = -1

	for iBonus in lBonuses:
		iCount = dCount.get(iBonus, 0)

		if iBest < 0 or iCount < iFewest:
			iBest, iFewest = iBonus, iCount

	return iBest


def holdings(iOwner):
	"""How many tiles of each resource stand on land this player's cities can reach.

	Counted rather than merely listed, because the count is what stops one resource taking over:
	each planting makes the next of its kind less likely.

	getNumAvailableBonuses is the strict test: it counts the capital's plot group, so a resource
	has to be improved and joined to the capital by road or coast before it registers at all. That
	is the right rule for deciding what you can build with. It is the wrong rule for deciding what
	your farmers know how to grow - a province that has kept sheep for a century does not forget
	them because a road was pillaged, or because the herd sits in a colony across the sea.

	City radii rather than the whole territory: it is a few hundred plots instead of twelve
	thousand, and a resource outside every city's reach is one nobody could improve or use anyway.
	"""
	dBonuses = {}
	seen = set()

	for city in cities.owner(iOwner):
		for i in range(21):
			p = city.getCityIndexPlot(i)

			# getCityIndexPlot returns a null plot where the radius runs off the map
			if not p or p.isNone():
				continue

			tile = location(p)

			# city radii overlap, and a tile counted twice would look twice as common
			if tile in seen:
				continue

			seen.add(tile)
			iBonus = p.getBonusType(-1)

			if iBonus >= 0 and p.getOwner() == iOwner:
				dBonuses[iBonus] = dBonuses.get(iBonus, 0) + 1

	return dBonuses
