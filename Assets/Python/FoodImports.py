# Food imports: from the railway age, cities buy the food their own land cannot grow.
#
# Before this, every city fed itself from its worked tiles in every era - a 20th century
# metropolis lived under the same rule as a bronze age village. Once bulk transport exists, a
# city running a local deficit covers it from the treasury instead.
#
# When the money runs out the city starves, but the people are not simply deleted: they move to
# a viable city, reusing the destination search in Migration.py.
#
# Known limitations, both from paying with changeFood() rather than raising the city's yield.
# CvCity::foodDifference sums worked tiles and cannot see the credit, so anything reading it
# directly still believes an import-fed city is starving. Python callers must use
# effectiveFoodDifference() below instead; the two that mattered - Migration's scorers - already
# do. The two that cannot be reached from Python:
#
#   - the city bar (CvGameTextMgr.cpp:5279) shows a permanent starvation warning and a
#     turns-to-starve count that never arrives.
#   - the AI city governor (CvCityAI.cpp:7563) weights food tiles 2048x while it believes a city
#     is starving, so an AI city tends to reassign citizens onto food and grow its way out of
#     import dependence rather than stay in it.
#
# Both are cosmetic or self-correcting, and fixing either means editing the DLL.

from Core import *
from Events import handler

import Migration


### CONSTANTS ###

# bulk grain by rail is what let London, Chicago and Berlin outgrow their hinterland
iFoodImportTech = iRailroad

# gold per unit of food, before the city-size surcharge and game speed scaling
iGoldPerFood = 3

# larger cities pay more per unit: +1 gold per this many citizens
iSizeSurcharge = 10

# an empire will never spend more than this share of its treasury on food in one turn, so
# feeding cities can never bankrupt a player - least of all the AI, which does not budget
iTreasuryShare = 25


### BEGIN PLAYER TURN ###

@handler("BeginPlayerTurn")
def importFood(iGameTurn, iPlayer):
	"""Cover food deficits with gold, before the cities grow.

	This must run before CvPlayer::doTurn processes cities. beginPlayerTurn fires at
	CvPlayer.cpp:3008 and cities are handled at :3048, so paying here offsets exactly the
	deficit that doGrowth is about to subtract, and no starvation occurs.
	"""
	if is_minor(iPlayer):
		return

	if not team(iPlayer).isHasTech(iFoodImportTech):
		return

	iBudget = budget(iPlayer)

	for city in cities.owner(iPlayer).where(isImportDependent):
		iDeficit = -city.foodDifference(False)
		iCost = cost(city, iDeficit)

		if iCost <= iBudget:
			player(iPlayer).changeGold(-iCost)
			city.changeFood(iDeficit)
			iBudget -= iCost
			notifyDependence(city)
		else:
			famine(city)


def isImportDependent(city):
	"""A city running a local deficit that something could actually reach."""
	if city.foodDifference(False) >= 0:
		return False

	return canImport(city)


def canImport(city):
	"""Whether food could physically reach this city, ignoring whether it can be paid for."""
	iOwner = city.getOwner()

	if is_minor(iOwner):
		return False

	if not team(iOwner).isHasTech(iFoodImportTech):
		return False

	return city.isConnectedToCapital(iOwner)


def effectiveFoodDifference(city):
	"""Food difference as the city actually experiences it, net of purchased imports.

	foodDifference() is computed from worked tiles alone and cannot see a changeFood() credit, so
	an import-fed city reads as starving to everything downstream. Anything reasoning about
	whether a city can feed its people must ask this instead - see Migration's scorers.
	"""
	iFoodDifference = city.foodDifference(False)

	if iFoodDifference >= 0:
		return iFoodDifference

	if not canImport(city):
		return iFoodDifference

	if cost(city, -iFoodDifference) > budget(city.getOwner()):
		return iFoodDifference

	# the deficit is bought, so the city is fed - but it has no surplus to offer either
	return 0


def budget(iPlayer):
	"""What the treasury will release for food this turn.

	A share of gold on hand rather than of income, so the spend is bounded by construction and
	can never take a player negative however many cities are hungry.
	"""
	return max(0, player(iPlayer).getGold()) * iTreasuryShare / 100


def cost(city, iDeficit):
	"""Gold to feed a city for one turn. Bigger cities pay more per unit."""
	return scale(iDeficit * (iGoldPerFood + city.getPopulation() / iSizeSurcharge))


### FAMINE ###

def famine(city):
	"""The city cannot be fed. Let it starve, but move the citizen rather than deleting them.

	doGrowth does the shrinking itself, so nothing here touches the source city's food or
	population - doing so would cost it two citizens instead of one. Only the arrival is added.
	"""
	iOwner = city.getOwner()

	# doGrowth spares size-1 cities, so growing a destination here would invent a citizen
	if city.getPopulation() <= 1:
		message(iOwner, 'TXT_KEY_FOOD_IMPORT_FAMINE', city.getName(),
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
			color=iRed, location=city)
		return

	destination = findRefuge(city)

	if destination is None:
		message(iOwner, 'TXT_KEY_FOOD_IMPORT_FAMINE', city.getName(),
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
			color=iRed, location=city)
		return

	destination.changePopulation(1)

	message(iOwner, 'TXT_KEY_FOOD_IMPORT_FAMINE_MIGRATED', city.getName(), destination.getName(),
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed, location=city)

	if destination.getOwner() != iOwner:
		message(destination.getOwner(), 'TXT_KEY_MIGRATION_IMMIGRATION', city.getName(), destination.getName(),
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iYellow, location=destination)


def findRefuge(city):
	"""Where the starving go. Reuses Migration's destination rules without disturbing them.

	Migration.findDestination requires the target to be meaningfully better and within reach, so
	a city with nowhere viable nearby simply starves - which is the correct outcome.
	"""
	candidates = players.major().existing().cities()
	dImmigration = dict((location(c), Migration.getImmigrationValue(c)) for c in candidates)

	return Migration.findDestination(city, candidates, dImmigration, [])


### NOTIFICATION ###

def notifyDependence(city):
	"""Tell the owner the first time a city stops feeding itself."""
	tLocation = location(city)

	if tLocation in data.lImportDependentCities:
		return

	data.lImportDependentCities.append(tLocation)

	message(city.getOwner(), 'TXT_KEY_FOOD_IMPORT_DEPENDENT', city.getName(),
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		color=iYellow, location=city)
