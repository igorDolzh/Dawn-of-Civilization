# Urbanisation: why modern cities are enormous when modern families are not.
#
# The mod already models half of this, and models it well. BirthRate.py implements the demographic
# transition - from the Industrial era a citizen costs steadily more food, because that is what
# happened: societies industrialised, birth rates collapsed, and Japan and Italy now have abundant
# food and shrinking populations. Nothing here touches that. Growing a city from within is meant to
# be hard and stays hard.
#
# But real cities kept growing anyway, and the reason is not fertility. It is that the land learned
# to feed far more people than farmed it, and that those people moved. London did not grow because
# Londoners had more children; it grew because grain arrived by rail and ship, and because the
# countryside emptied into it.
#
# So this supplies the other half, in two parts that are useless apart:
#
#   1. Carrying capacity. Late technology raises what a city can feed and keep healthy, so a large
#      city can be sustained at all. Without this, arrivals simply starve.
#   2. The rural exodus. Migration.py already moves people from bad cities to good ones and already
#      scores large cities as more attractive, but at three people per cycle for the entire world it
#      cannot represent the largest movement of population in human history. From the Industrial era
#      that rate climbs, and people begin leaving places that are merely small rather than only
#      places that are miserable.
#
# The result is the shape asked for: big cities are still hard to grow and easy to maintain, and
# they fill up from outside.

from Core import *
from Events import handler


### CARRYING CAPACITY ###

# tech -> (food yield percent, health)
#
# Food is a percentage because carrying capacity is multiplicative: mechanised farming does not add
# a fixed number of loaves to a city, it raises what the same worked land returns. Health is flat,
# because sanitation is a threshold rather than a rate.
#
# Applied at player level. CvCity::getBaseYieldRateModifier folds the owner's yield modifier into
# every city's yield at CvCity.cpp:10245, and CvCity::foodConsumption subtracts healthRate directly
# at :6069 - so a point of health is quite literally a point of food that is no longer eaten.
dCarryingCapacity = {
	# sanitation, before there is anything to transport: the first thing that let a city be large
	# without being lethal
	iUrbanPlanning:  (0, 2),

	# the same acre feeds more people
	iBiology:        (15, 0),

	# grain from a thousand miles away, which is the single largest reason a modern city can exist
	iRailroad:       (15, 0),

	# and food that survives the journey
	iRefrigeration:  (10, 2),

	iEcology:        (10, 2),
	iGenetics:       (15, 1),
}


@handler("BeginPlayerTurn")
def updateCarryingCapacity(iGameTurn, iPlayer):
	"""Bring this civilization's carrying capacity up to what its technology allows.

	Recomputed every turn from the techs actually held, rather than granted once on techAcquired.
	That costs two integer comparisons for a player whose technology has not changed, and it means a
	save made before this module existed corrects itself on the first turn instead of needing an
	OnLoad pass - the same reasoning BirthRate.updateBirthRate gives for the same choice.

	Both are written as the difference from what this module last applied. changeYieldRateModifier
	and changeExtraHealth are relative and the DLL records no attribution, so anything that set them
	absolutely would silently erase whatever else had written to the same field.
	"""
	if is_minor(iPlayer):
		return

	if not player(iPlayer).isExisting():
		return

	iFood, iHealth = capacity(iPlayer)

	iAppliedFood = data.players[iPlayer].iUrbanFood
	if iFood != iAppliedFood:
		player(iPlayer).changeYieldRateModifier(YieldTypes.YIELD_FOOD, iFood - iAppliedFood)
		data.players[iPlayer].iUrbanFood = iFood

	iAppliedHealth = data.players[iPlayer].iUrbanHealth
	if iHealth != iAppliedHealth:
		player(iPlayer).changeExtraHealth(iHealth - iAppliedHealth)
		data.players[iPlayer].iUrbanHealth = iHealth


def capacity(iPlayer):
	"""Food percentage and health this civilization's technology has earned."""
	iFood, iHealth = 0, 0
	tPlayer = team(iPlayer)

	for iTech, (iTechFood, iTechHealth) in dCarryingCapacity.items():
		if tPlayer.isHasTech(iTech):
			iFood += iTechFood
			iHealth += iTechHealth

	return iFood, iHealth


### THE RURAL EXODUS ###

# People who move in a single migration cycle, across the whole world, by the most advanced era
# anyone has reached. MUST have exactly iNumEras entries: worldEra() indexes this directly.
#
# Three was the figure for the whole of history and it is right for most of it - pre-industrial
# populations barely moved. It is badly wrong afterwards. Between 1800 and 1900 England went from
# a fifth urban to three quarters urban, and no rate that small can show it.
tEraMigrations = (
	3,   # ancient
	3,   # classical
	3,   # medieval
	3,   # renaissance
	7,   # industrial   - the countryside begins to empty
	10,  # global
	12,  # digital
	12,  # synthetic
)


# How bad a city has to be before anyone leaves it, by the same era.
#
# Migration.iMinEmigrationValue is 3, meaning only cities in real distress send anyone away. That is
# the right rule for a world where leaving is dangerous and the next town is no better. It is the
# wrong rule for one with railways: people left perfectly tolerable villages, not failing ones,
# because somewhere else offered more. Lowering the bar is what turns migration from a relief valve
# into a current.
tEraEmigrationThreshold = (
	3,
	3,
	3,
	3,
	2,   # industrial
	1,   # global
	1,   # digital
	1,   # synthetic
)


def worldEra():
	"""The most advanced era anyone has reached.

	The exodus is a property of the world rather than of one civilization: once railways and cities
	exist somewhere, people move towards them from wherever they are. Bounded because a table
	indexed by an era is a table that will one day be indexed by an era it does not have.
	"""
	lEras = [player(iPlayer).getCurrentEra() for iPlayer in players.major().existing()]

	if not lEras:
		return 0

	return min(max(lEras), len(tEraMigrations) - 1)


def migrationsPerCycle(iDefault):
	"""How many people may move in one cycle."""
	return max(iDefault, tEraMigrations[worldEra()])


def emigrationThreshold(iDefault):
	"""How miserable a city must be before anyone leaves it."""
	return min(iDefault, tEraEmigrationThreshold[worldEra()])
