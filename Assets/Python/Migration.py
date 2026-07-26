# Population migration: people leave cities that have become bad places to live
# and resettle in better ones nearby, across borders as well as within them.
#
# Generalises the former Old World -> New World immigration rule that used to live in Rules.py.

from Core import *
from RFCUtils import *
from Events import handler


### CONSTANTS ###

# turns between migration cycles: iMigrationInterval + rand(iMigrationIntervalRand)
iMigrationInterval = 3
iMigrationIntervalRand = 5

# at most this many people move in a single cycle, across the entire world
iMaxMigrationsPerCycle = 3

# how far people are willing to travel, in plots
iMaxMigrationDistance = 12

# a city is never reduced to or below this size by emigration
iMinSourcePopulation = 2

# how miserable a city has to be before anyone leaves at all
iMinEmigrationValue = 3

# the destination has to be this much better than the origin, so that population
# cannot oscillate between two equally mediocre cities every cycle
iMigrationMargin = 2

# distance is traded off against attractiveness at this rate
iDistancePenaltyDivisor = 4


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkMigration(iGameTurn):
	# city states are not settled on the first turn of a scenario
	if scenarioStart():
		return

	data.iImmigrationTimer -= 1

	if data.iImmigrationTimer <= 0:
		migration()
		data.iImmigrationTimer = turns(iMigrationInterval + rand(iMigrationIntervalRand))


### SCORING ###

def foodDifference(city):
	"""The city's food balance as its people experience it.

	From the railway age a city may buy the food its land cannot grow, and CvCity::foodDifference
	sums worked tiles only, so it reports such a city as starving. Both scorers must use this
	instead, or a city kept alive by imports would repel migrants and shed its own population -
	the exact opposite of what feeding it is for.

	Imported inside the function because FoodImports imports this module.
	"""
	import FoodImports
	return FoodImports.effectiveFoodDifference(city)



# Both scoring functions add rand(0, 2) of jitter, which draws from the synced RNG.
# They must therefore be evaluated exactly once per city per cycle: see migration().

def getEmigrationValue(city):
	"""How badly people want to leave this city. Only negative conditions contribute."""
	if city.getPopulation() <= iMinSourcePopulation:
		return 0

	iOwner = city.getOwner()

	iFoodDifference = foodDifference(city)
	iHappinessDifference = city.happyLevel() - city.unhappyLevel(0)
	iHealthRate = city.healthRate(False, 0)

	iValue = 0

	# unhappiness and civil disorder
	iValue -= min(0, iHappinessDifference)
	if city.isDisorder():
		iValue += 3

	# starvation
	iValue -= min(0, iFoodDifference / 2)

	# disease
	iValue -= min(0, iHealthRate / 2)
	if city.hasBuilding(iPlague):
		iValue += 4

	# war, occupation and weak cultural control
	if city.isOccupation():
		iValue += 3

	if team(iOwner).getAtWarCount(True) > 0:
		iValue += 2

	if city.calculateCulturePercent(iOwner) < 50:
		iValue += 2

	if iValue > 0:
		iValue += city.getPopulation() / 5
		iValue += rand(0, 2)

	return iValue


def getImmigrationValue(city):
	"""How attractive this city is to settle in. Cities in crisis attract nobody."""
	if city.isDisorder() or city.isOccupation() or city.hasBuilding(iPlague):
		return 0

	iFoodDifference = foodDifference(city)

	# a city that cannot feed itself cannot feed newcomers
	if iFoodDifference < 0:
		return 0

	iValue = 0

	iValue += max(0, city.happyLevel() - city.unhappyLevel(0))
	iValue += max(0, iFoodDifference / 2)
	iValue += max(0, city.healthRate(False, 0) / 2)
	iValue += city.getPopulation() / 2

	if iValue > 0:
		iValue += rand(0, 2)

	return iValue


### MIGRATION ###

def migration():
	candidates = players.major().existing().cities()

	# Score every city exactly once. Evaluating the scorers again inside a filter or a
	# sort key would draw from the synced RNG a second time, so a city would be ranked
	# by a different score than it was filtered by, and the number of RNG draws per turn
	# would depend on collection ordering.
	dEmigration = {}
	dImmigration = {}
	for city in candidates:
		tLocation = location(city)
		dEmigration[tLocation] = getEmigrationValue(city)
		dImmigration[tLocation] = getImmigrationValue(city)

	def emigrationValue(city):
		return dEmigration.get(location(city), 0)

	sourceCities = candidates.where(lambda city: canEmigrateFrom(city, emigrationValue(city))) \
							 .highest(iMaxMigrationsPerCycle, emigrationValue)

	# locations already involved this cycle, so nobody migrates twice in one go
	lUsed = []

	for sourceCity in sourceCities:
		# cities can be razed or captured by a handler fired earlier in this loop
		if not sourceCity or sourceCity.isNone():
			continue

		# population may have changed since the sources were picked
		if sourceCity.getPopulation() <= iMinSourcePopulation:
			continue

		targetCity = findDestination(sourceCity, candidates, dImmigration, lUsed)
		if targetCity is None:
			continue

		lUsed.append(location(sourceCity))
		lUsed.append(location(targetCity))

		migrate(sourceCity, targetCity)


def canEmigrateFrom(city, iEmigrationValue):
	if player(city.getOwner()).isBirthProtected():
		return False

	return iEmigrationValue >= iMinEmigrationValue


def findDestination(sourceCity, candidates, dImmigration, lUsed):
	iSourceOwner = sourceCity.getOwner()
	tSourceLocation = location(sourceCity)
	iSourceValue = dImmigration.get(tSourceLocation, 0)

	def pullValue(city):
		return dImmigration.get(location(city), 0)

	def isViable(city):
		if not city or city.isNone():
			return False

		tLocation = location(city)
		if tLocation == tSourceLocation or tLocation in lUsed:
			return False

		if distance(sourceCity, city) > iMaxMigrationDistance:
			return False

		# people do not flee into the arms of an enemy
		if team(iSourceOwner).isAtWar(player(city.getOwner()).getTeam()):
			return False

		# nor to a civilization they have never heard of
		iOwner = city.getOwner()
		if iOwner != iSourceOwner and not team(iSourceOwner).isHasMet(player(iOwner).getTeam()):
			return False

		iValue = pullValue(city)
		return iValue > 0 and iValue >= iSourceValue + iMigrationMargin

	viableCities = candidates.where(isViable)
	if viableCities.count() == 0:
		return None

	return viableCities.maximum(lambda city: pullValue(city) - distance(sourceCity, city) / iDistancePenaltyDivisor)


def migrate(sourceCity, targetCity):
	iSourcePlayer = sourceCity.getOwner()
	iTargetPlayer = targetCity.getOwner()

	# names have to be read before the message calls, and while both cities still exist
	sSourceName = sourceCity.getName()
	sTargetName = targetCity.getName()

	shrink(sourceCity)
	targetCity.changePopulation(1)

	# extra cottage growth for target city's vicinity
	for pCurrent in plots.surrounding(targetCity, radius=2):
		if pCurrent.getWorkingCity() == targetCity:
			pCurrent.changeUpgradeProgress(turns(10))

	iCultureChange = 0

	# migration between civilizations brings culture with it
	if iSourcePlayer != iTargetPlayer:
		targetPlot = plot(targetCity)

		iCultureChange = targetPlot.getCulture(iTargetPlayer) / targetCity.getPopulation()
		targetPlot.changeCulture(iSourcePlayer, iCultureChange, False)

		iCultureChange = targetCity.getCulture(iTargetPlayer) / targetCity.getPopulation()
		targetCity.changeCulture(iSourcePlayer, iCultureChange, False)

	announce(sourceCity, targetCity, sSourceName, sTargetName)

	# only foreign arrivals count as immigration: firing this for movement inside a single
	# civilization would let America's Manifest Destiny power create population out of nothing
	if iSourcePlayer != iTargetPlayer:
		events.fireEvent("immigration", sourceCity, targetCity, 1, iCultureChange)


def shrink(city):
	"""Remove one population, keeping the same fraction of progress towards regrowth.

	changePopulation() does not touch the food box, but growthThreshold() scales with
	population. A city that shrinks therefore keeps a food box that may already exceed
	its new, lower threshold, and grows straight back next turn. Left unscaled, every
	migration would create a population point out of nothing.
	"""
	iFood = city.getFood()
	iThreshold = city.growthThreshold()

	city.changePopulation(-1)

	if iThreshold > 0:
		city.setFood(city.growthThreshold() * iFood / iThreshold)


def announce(sourceCity, targetCity, sSourceName, sTargetName):
	iSourcePlayer = sourceCity.getOwner()
	iTargetPlayer = targetCity.getOwner()

	if iSourcePlayer == iTargetPlayer:
		message(iSourcePlayer, 'TXT_KEY_MIGRATION_INTERNAL', sSourceName, sTargetName,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			button=infos.unit(iSettler).getButton(), color=iYellow, location=targetCity)
		return

	message(iSourcePlayer, 'TXT_KEY_MIGRATION_EMIGRATION', sSourceName, sTargetName,
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		button=infos.unit(iSettler).getButton(), color=iYellow, location=sourceCity)

	message(iTargetPlayer, 'TXT_KEY_MIGRATION_IMMIGRATION', sSourceName, sTargetName,
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		button=infos.unit(iSettler).getButton(), color=iYellow, location=targetCity)
