# The demographic transition: from the Industrial era, food stops making babies.
#
# For all of human history until roughly 1870, population was limited by food, and the game models
# that correctly - a city with a surplus grows, in every era, at the same rate. Then societies
# industrialised and urbanised, birth rates collapsed, and the link broke. Modern Japan, Italy and
# South Korea have abundant food and shrinking populations.
#
# Two halves, one constant governing both:
#
#   1. Each era from Industrial onward raises the food cost of a new citizen. Cities still grow,
#      just slowly. The existing size ramp in CvPlayer::getGrowthThreshold does the rest - it
#      already charges 340 food per citizen at size 40 against 40 at size 10, so large cities feel
#      this far more than small ones without any per-city machinery.
#
#   2. The share of growth the transition costs comes back as production, because that is what
#      actually happened: fewer hands were needed on the land, and they went into industry.
#
# The AI needs no teaching. CvCityAI::AI_yieldValue reads growthThreshold() directly
# (CvCityAI.cpp:7788), so raising what the DLL genuinely returns makes the AI value food tiles less
# and shift toward production on its own. That is why this works through MODIFIER_GROWTH_THRESHOLD
# rather than any cheaper Python trick that would leave foodDifference() untouched.

from Core import *
from Events import handler
from Modifiers import getBaseModifier, setModifier

import FoodImports


### CONSTANTS ###

# Growth threshold as a percentage of the civilization's own baseline, per era.
# MUST have exactly iNumEras entries: getCurrentEra() indexes this directly.
tEraGrowthPenalty = (
	100,  # ancient
	100,  # classical
	100,  # medieval
	100,  # renaissance   - the Malthusian world, where food is the only constraint
	130,  # industrial    - the transition begins
	160,  # global
	190,  # digital
	220,  # synthetic
)

# Post-Scarcity retires the whole mechanic: back to the civilization's baseline, and no production
# compensation, because there is no longer anything to compensate for.
iTransitionEndTech = iPostScarcity

# Surplus food becomes production only in cities that store food. setBuildingYieldChange applies a
# value only where the city owns an active building of the class (CvCity.cpp:17743), so the carrier
# is a real design constraint - the Granary is chosen because it is cheap, comes from Pottery, and
# is free from a Medieval start, so by the Industrial era it gates almost nothing.
iSurplusCarrier = iGranary


### BEGIN PLAYER TURN ###

@handler("BeginPlayerTurn")
def updateBirthRate(iGameTurn, iPlayer):
	"""Recompute the growth penalty and the production it returns.

	Runs before the player's cities do: BeginPlayerTurn fires at CvPlayer.cpp:3008 and the city
	loop is at :3047, so the threshold is already correct when doGrowth tests against it.

	Recomputed every turn rather than driven by an era-change event. That costs one integer write
	per player, picks up era advancement with no extra plumbing, and means a save made before this
	module existed corrects itself on the first turn instead of needing an OnLoad pass.
	"""
	if is_minor(iPlayer):
		return

	if not player(iPlayer).isExisting():
		return

	iPenalty = growthPenalty(iPlayer)

	# absolute, computed from the civ baseline rather than from the current value, so applying it
	# twice is the same as applying it once and Modifiers.init cannot leave a stale value behind
	setModifier(iPlayer, iModifierGrowthThreshold, getBaseModifier(iPlayer, iModifierGrowthThreshold) * iPenalty / 100)

	for city in cities.owner(iPlayer):
		convertSurplus(city, iPenalty)

	announce(iPlayer, iPenalty)


def growthPenalty(iPlayer):
	"""How much dearer a citizen is than this civilization's baseline, as a percentage."""
	if team(iPlayer).isHasTech(iTransitionEndTech):
		return 100

	return tEraGrowthPenalty[player(iPlayer).getCurrentEra()]


### SURPLUS ###

def convertSurplus(city, iPenalty):
	"""Turn the share of the food surplus the transition wastes into production.

	At a penalty of 190 a citizen costs 90/190 more food than before, so that same fraction of the
	surplus comes back as hammers. The food itself is deliberately left alone: the threshold has
	already slowed growth, and taking the food as well would charge for the same thing twice.
	"""
	iProduction = surplusProduction(FoodImports.effectiveFoodDifference(city), iPenalty)

	# absolute set, so a city that loses its surplus loses the bonus on the same turn, and a value
	# of 0 erases the record entirely. Losing the Granary needs no handling here - processBuilding
	# unwinds the yield itself (CvCity.cpp:4559).
	city.setBuildingYieldChange(infos.building(iSurplusCarrier).getBuildingClassType(), YieldTypes.YIELD_PRODUCTION, iProduction)


def surplusProduction(iSurplus, iPenalty):
	"""Hammers owed for a food surplus, given how dear citizens have become."""
	if iPenalty <= 100:
		return 0

	return max(0, iSurplus) * (iPenalty - 100) / iPenalty


### NOTIFICATION ###

def announce(iPlayer, iPenalty):
	"""Tell the player once, when their civilization enters the transition.

	Without this the mechanic is silent: cities simply grow more slowly than the player remembers,
	and the production appearing on the Granary looks unrelated.
	"""
	if iPenalty <= 100:
		return

	if data.players[iPlayer].bDemographicTransition:
		return

	data.players[iPlayer].bDemographicTransition = True

	message(iPlayer, 'TXT_KEY_DEMOGRAPHIC_TRANSITION',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iYellow)
