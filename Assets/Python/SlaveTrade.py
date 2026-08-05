# The Atlantic slave trade.
#
# The mod already owned most of the pieces - slave units and specialists, slave plantations, a
# TRADE_SLAVE diplomacy item, a playerSlaveTrade event carrying the gold paid, and the cash crops
# appearing in Resources.py exactly where and when history put them. What it lacked was a flow:
# an origin, a passage and a destination, and any consequence for either end.
#
# This module supplies the three legs and the reckoning that ended them:
#
#   supply     African polities take gold for captives and lose people for it
#   passage    selling into a plantation economy pays far better than selling into nothing
#   demand     slave plantations on colonial crops become the richest ground in the world
#   reckoning  revolts scaled to how much of a city is held in bondage, and abolitionist
#              opinion that hardens against slaveholders from the late eighteenth century
#
# The trade is deliberately profitable. It was, and a model that made it a poor choice would
# explain nothing about why it lasted four hundred years. It is also deliberately survivable
# only for a while: the costs below arrive later than the profits and do not decay while the
# practice continues.
#
# Geography is not re-derived here. CvPlot::canUseSlave already encodes the Atlantic triangle -
# slaves may be used in the Americas, and in sub-Saharan Africa only by a power based elsewhere -
# and CvCity::canSlaveJoin caps a colony at half its population in slaves. This module reads
# those rules rather than restating them.

from Core import *
from RFCUtils import *
from Events import handler

import Stability


### THE WINDOW ###

# Portugal reaches the Guinea coast in the 1440s; Brazil abolishes in 1888. Outside these years
# nothing here fires, so the mechanic cannot leak into the ancient or modern game.
iTradeStart = 1450
iTradeEnd = 1888

# abolitionist opinion becomes a diplomatic fact rather than a moral one
iAbolitionismStart = 1780


### SUPPLY: THE AFRICAN COAST ###

# Only sub-Saharan civs can sell, and only from cities on the coast the ships could actually
# reach. Regions come from Consts; lSubSaharanAfrica is the mod's own list.
lSupplyRegions = [rGuinea, rCongo, rSahel]

# gold per turn per European buyer present, before scaling
iSupplyGoldPerBuyer = 6

# what it costs: stability, and eventually people
iSupplyStabilityPenalty = -1
iDepopulationInterval = 12


### PASSAGE: SELLING INTO A PLANTATION ECONOMY ###

# A captive sold to a power with plantations to work is worth more than one sold to a power
# without. This is the bonus applied on top of whatever the deal itself paid, as a percentage
# of that gold, capped so a single sale cannot fund an empire.
iPassageBonusPerPlantation = 8
iPassageBonusCap = 200


### DEMAND: THE PLANTATION ECONOMY ###

# Commerce modifier granted for working slave plantations, per plantation, and its ceiling.
# Written as a tracked delta - see applyPlantationModifier.
iPlantationModifierPer = 3
iPlantationModifierCap = 45

# The crops the trade existed to grow. HistoricalVictory already names this basket for Portugal's
# third goal, and reusing it keeps the two from drifting apart - but it MUST be imported lazily.
#
# HistoricalVictory builds its goal tables at module scope, and those call plots.core(), which
# reads infos.civ(iCiv).getShortDescription(). When Handlers imports this module the civilization
# infos are not loaded yet, so that returns None and the whole mod dies with
# "AttributeError: 'NoneType' object has no attribute 'getShortDescription'".
#
# Victories.py defers its own HistoricalVictory import inside a function for exactly this reason.
def colonialResources():
	from HistoricalVictory import lColonialResources
	return lColonialResources


### THE RECKONING ###

# A revolt becomes possible once this share of a city is enslaved, and its chance climbs with
# the share. Percentages, checked per city per turn.
iRevoltThreshold = 30
iRevoltChanceDivisor = 12
iRevoltUnrest = 3

# Abolitionist opinion: the attitude penalty a free civ holds against a slaveholding one, and
# the stability pressure the slaveholder accumulates.
iAbolitionAttitudePenalty = -2
iAbolitionPressureStep = -1
iAbolitionPressureFloor = -12


### HELPERS ###

def isTradeActive():
	# year() returns a Turn, which subclasses int as a turn number - so the bounds have to be
	# converted to turns too rather than compared against calendar years
	return year().between(year(iTradeStart), year(iTradeEnd))


def isSupplier(iPlayer):
	"""An African polity positioned to sell into the Atlantic trade."""
	if is_minor(iPlayer):
		return False

	capital_city = capital(iPlayer)
	if not capital_city:
		return False

	return capital_city.getRegionID() in lSupplyRegions


def isSlaveholder(iPlayer):
	"""Whether this power can hold slaves at all.

	canUseSlaves is the mod's own predicate and is permissive by default: slavery is legal
	unless a civic sets bNoSlavery. Testing it rather than the Slavery civic is what makes
	Colonialism count - a European colonial power holds slaves without ever adopting Slavery.
	"""
	return player(iPlayer).canUseSlaves()


def countSlavePlantations(iPlayer):
	"""Slave plantations this player works on colonial crops."""
	crops = colonialResources()

	iCount = 0
	for city in cities.owner(iPlayer):
		for plot in plots.surrounding(city):
			if plot.getImprovementType() == iSlavePlantation:
				if plot.getBonusType(-1) in crops:
					iCount += 1
	return iCount


def countColonies(iPlayer):
	"""Overseas cities this player holds.

	CvPlayer::countColonies exists but is not exposed to Python; CyCity::isColony is, and is what
	Stability, Wonders and Resurrection already use.
	"""
	return cities.owner(iPlayer).where(lambda city: city.isColony()).count()


def countBuyers():
	"""Powers currently able to buy captives for colonies."""
	return players.major().existing().where(
		lambda p: isSlaveholder(p) and not isSupplier(p) and countColonies(p) > 0).count()


### SUPPLY AND DEMAND, PER TURN ###

@handler("BeginPlayerTurn")
def slaveTrade(iGameTurn, iPlayer):
	if is_minor(iPlayer) or not player(iPlayer).isExisting():
		return

	if not isTradeActive():
		# outside the window the plantation bonus must be withdrawn, or it would persist forever
		applyPlantationModifier(iPlayer, 0)
		return

	if isSupplier(iPlayer):
		supply(iGameTurn, iPlayer)
	elif isSlaveholder(iPlayer):
		demand(iPlayer)


def supply(iGameTurn, iPlayer):
	"""Gold for captives, paid for in people.

	The choice this models is the one Kongo, Dahomey and Asante actually faced: revenue now
	against depopulation later. The mod already assumes participation - Congo's second UHV is
	SlaveTradeGold(1000, by=1800) - so this gives that goal a mechanism rather than inventing
	a stance.
	"""
	iBuyers = countBuyers()
	if iBuyers <= 0:
		return

	player(iPlayer).changeGold(scale(iBuyers * iSupplyGoldPerBuyer))
	data.players[iPlayer].iSlaveTradeIncome += scale(iBuyers * iSupplyGoldPerBuyer)

	# the cost arrives on a slower clock than the income, which is the point
	if iGameTurn % turns(iDepopulationInterval) == 0:
		depopulate(iPlayer)


def depopulate(iPlayer):
	"""The coast loses the people the ships carried away."""
	coastal = cities.owner(iPlayer).where(lambda city: city.isCoastal(20))
	if not coastal:
		return

	# maximum, not where_maximum: the latter returns the subset of cities that tie for the largest
	# population, and a collection has no getPopulation
	city = coastal.maximum(lambda city: city.getPopulation())
	if not city or city.isNone() or city.getPopulation() <= 1:
		return

	city.changePopulation(-1)

	if data.players[iPlayer].iSlaveTradePenalty > iAbolitionPressureFloor:
		data.players[iPlayer].iSlaveTradePenalty += iSupplyStabilityPenalty
		Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_SLAVE_TRADE_DEPOPULATION', city.getName())


def demand(iPlayer):
	"""Plantations worked by slaves become the most valuable ground in the world."""
	iPlantations = countSlavePlantations(iPlayer)
	iTarget = min(iPlantations * iPlantationModifierPer, iPlantationModifierCap)
	applyPlantationModifier(iPlayer, iTarget)


def applyPlantationModifier(iPlayer, iTarget):
	"""Move this player's commerce modifier to iTarget, writing only the difference.

	changeYieldRateModifier is relative and the DLL keeps no record of who applied what, so the
	amount this module is responsible for is tracked in StoredData and only the delta is written.
	That is what makes it safe to call every turn, and what stops a reloaded save from either
	stranding the bonus or applying it twice. Copied deliberately from BlackDeath.applyModifier.
	"""
	iCurrent = data.players[iPlayer].iPlantationModifier

	if iCurrent == iTarget:
		return

	player(iPlayer).changeYieldRateModifier(YieldTypes.YIELD_COMMERCE, iTarget - iCurrent)
	data.players[iPlayer].iPlantationModifier = iTarget


### THE PASSAGE ###

@handler("playerSlaveTrade")
def middlePassage(iPlayer, iGold):
	"""A captive sold into a working plantation economy is worth more than one sold into none.

	playerSlaveTrade is fired by CvDeal with the gold the buyer paid, so this adds to a sale
	that already happened rather than creating one.
	"""
	if not isTradeActive():
		return

	iPlantations = countSlavePlantations(iPlayer)
	if iPlantations <= 0:
		return

	iBonusPercent = min(iPlantations * iPassageBonusPerPlantation, iPassageBonusCap)
	iBonus = iGold * iBonusPercent / 100

	if iBonus > 0:
		player(iPlayer).changeGold(iBonus)
		message(iPlayer, 'TXT_KEY_SLAVE_TRADE_PASSAGE_PROFIT', iBonus)


### THE RECKONING ###

@handler("BeginPlayerTurn")
def slaveRevolts(iGameTurn, iPlayer):
	"""Cities held largely in bondage rise.

	Haiti is the case the mod already models as a civilization; this is the same event at the
	scale of a single city, and the reason a plantation economy cannot simply be scaled up.
	"""
	if is_minor(iPlayer) or not player(iPlayer).isExisting():
		return

	if not isTradeActive() or not isSlaveholder(iPlayer):
		return

	for city in cities.owner(iPlayer):
		iSlaves = city.getFreeSpecialistCount(iSpecialistSlave)
		iPopulation = city.getPopulation()
		if iPopulation <= 0 or iSlaves <= 0:
			continue

		iShare = 100 * iSlaves / iPopulation
		if iShare < iRevoltThreshold:
			continue

		if rand(100) < iShare / iRevoltChanceDivisor:
			revolt(iPlayer, city, iSlaves)


def revolt(iPlayer, city, iSlaves):
	"""The enslaved of one city rise: unrest, freed specialists, and rebels in the field."""
	city.changeHurryAngerTimer(turns(iRevoltUnrest))
	city.setFreeSpecialistCount(iSpecialistSlave, max(0, iSlaves - 1 - iSlaves / 2))

	createRoleUnits(iIndependent, location(city), [(iCityAttack, 1 + iSlaves / 3)],
					iExperience=1, bCreateSettlers=False)

	message(iPlayer, 'TXT_KEY_SLAVE_TRADE_REVOLT', city.getName(), color=iRed)


@handler("BeginPlayerTurn")
def abolitionistOpinion(iGameTurn, iPlayer):
	"""Holding slaves becomes a diplomatic liability rather than merely a moral one.

	Nothing else in the mod occupies this axis: the only AI_changeAttitudeExtra callers are
	crusades, revolutions, bribery and resurrection. The penalty is applied once per decade so
	it accumulates into something a slaveholder notices without swamping ordinary diplomacy.
	"""
	if is_minor(iPlayer) or not player(iPlayer).isExisting():
		return

	if year() < year(iAbolitionismStart):
		return

	if not isSlaveholder(iPlayer):
		# a power that has abolished stops attracting the penalty, and its own pressure lifts
		if data.players[iPlayer].iAbolitionPressure < 0:
			data.players[iPlayer].iAbolitionPressure += 1
		return

	if iGameTurn % turns(10) != 0:
		return

	for iOther in players.major().existing().where(lambda p: p != iPlayer):
		if not isSlaveholder(iOther):
			player(iOther).AI_changeAttitudeExtra(iPlayer, iAbolitionAttitudePenalty)

	if data.players[iPlayer].iAbolitionPressure > iAbolitionPressureFloor:
		data.players[iPlayer].iAbolitionPressure += iAbolitionPressureStep
		Stability.checkStability(iPlayer)


### QUERIES ###

def getSlaveTradePenalty(iPlayer):
	"""Read by Stability.calculateStability alongside the other accumulators."""
	return data.players[iPlayer].iSlaveTradePenalty + data.players[iPlayer].iAbolitionPressure
