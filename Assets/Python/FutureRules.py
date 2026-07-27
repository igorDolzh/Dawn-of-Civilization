# Future technologies that retire rules the rest of the game is built on.
#
# The Synthetic era techs mostly unlocked nothing. Rather than giving them buildings, each one
# here removes a constraint the player has lived under for four thousand years: distance costing
# money, empires fragmenting, disease returning, cities capped by food and happiness.
#
# Everything is expressed as an absolute value written through Modifiers.setModifier, which the
# DLL serialises in m_aiModifiers. That makes each rule idempotent and save-persistent: firing it
# twice is the same as firing it once, so the OnLoad reconciliation below is free of side effects.

from Core import *
from Events import handler

from Modifiers import setModifier


### RULES ###

# tech -> [(modifier, absolute new value)]
#
# Values are percentages of the civilization's baseline, so 0 means "this cost no longer exists"
# and 50 means "halved". They are deliberately not all zero: retiring every constraint at once
# would leave the last era with nothing to play against.
dModifierRules = {
	# Distance costs money. Empire size has been throttled by distance and colony upkeep all game.
	iNeuralUplink: [
		(iModifierDistanceMaintenance, 0),
		(iModifierColonyMaintenance, 0),
	],

	# Cities are limited by food.
	# The growth threshold half of this lives in BirthRate.py, which recomputes that modifier every
	# turn from the civilization baseline. Two absolute writers of one integer would race on load
	# order, so this table must not touch it.
	iPostScarcity: [
		(iModifierCitiesMaintenance, 50),
	],

	# Buildings take time.
	iNanoassembly: [
		(iModifierBuildingCost, 50),
		(iModifierWonderCost, 60),
	],

	# A civilization has one research focus.
	iMachineConsciousness: [
		(iModifierResearchCost, 75),
	],

	# Great people are rationed.
	iPlanetaryConsciousness: [
		(iModifierGreatPeopleThreshold, 60),
	],

	# Industry is dirty.
	iClimateEngineering: [
		(iModifierHealth, 150),
	],

	# A civilization's output is bounded by the people in it. Transhumanism unbinds that.
	iTranshumanism: [
		(iModifierCulture, 200),
	],

	# Units are built on the ground and moved to where they are needed.
	iOrbitalIndustry: [
		(iModifierUnitCost, 50),
	],

	# Energy is scarce and its price sets the price of everything else.
	iHeliumThreeExtraction: [
		(iModifierInflationRate, 0),
	],

	# Governing costs more the more you govern. Perfect optimisation ends that.
	iQuantumComputing: [
		(iModifierCivicUpkeep, 40),
	],

	# An army has to be fed and paid wherever it stands.
	iDirectedEnergy: [
		(iModifierUnitUpkeep, 40),
	],
}

# techs whose effect lives outside the modifier system, handled individually below
iPlagueImmunityTech = iSyntheticGenomics

# stability suppression is read directly by Stability.calculateStability
iStabilityTech = iPlanetaryConsciousness

# Asteroid mining puts a metal supply beyond any territory in reach of every city
iFreeResourceTech = iAsteroidMining
iFreeResource = iAluminium

# Orbital habitation lifts the housing constraint: land stops bounding how many can live somewhere
iOrbitalHousingTech = iOrbitalHabitation
iOrbitalHousing = 3


### HANDLERS ###

@handler("techAcquired")
def applyFutureRules(iTech, iTeam, iPlayer):
	apply(iPlayer, iTech)


@handler("OnLoad")
def reconcileFutureRules():
	"""Re-apply every rule a player already qualifies for.

	techAcquired never fires again for a tech already held, so a save made before these rules
	existed - or before a rule was added to the table - would never receive them. Re-applying is
	safe because every rule writes an absolute value.
	"""
	for iPlayer in players.major().existing():
		for iTech in dModifierRules:
			if team(iPlayer).isHasTech(iTech):
				apply(iPlayer, iTech)

		if team(iPlayer).isHasTech(iPlagueImmunityTech):
			apply(iPlayer, iPlagueImmunityTech)


def apply(iPlayer, iTech):
	for iModifier, iValue in dModifierRules.get(iTech, []):
		setModifier(iPlayer, iModifier, iValue)

	# Disease is a permanent threat. Synthetic genomics ends plague outright rather than
	# shortening it, which is what Microbiology already does in Plague.acquireVaccine.
	if iTech == iPlagueImmunityTech:
		data.players[iPlayer].iPlagueCountdown = -turns(1000)

	# Asteroid mining: a metal supply that owes nothing to territory
	if iTech == iFreeResourceTech:
		for city in cities.owner(iPlayer):
			if city.getFreeBonus(iFreeResource) <= 0:
				city.changeFreeBonus(iFreeResource, 1)


### QUERIES ###

def hasRule(iPlayer, iTech):
	"""Whether this player holds a rule-breaking technology. Used by Stability."""
	return team(iPlayer).isHasTech(iTech)



@handler("BeginPlayerTurn")
def orbitalHousing(iGameTurn, iPlayer):
	"""Land stops bounding how many people can live somewhere.

	A standing effect rather than a one-off, so it is applied per turn like the other continuous
	rules rather than through apply(), which only fires once when the technology arrives.
	"""
	if is_minor(iPlayer):
		return

	if not team(iPlayer).isHasTech(iOrbitalHousingTech):
		return

	for city in cities.owner(iPlayer):
		city.changeFood(scale(iOrbitalHousing))


### THE LATE SYNTHETIC RULES ###

# The modifier table is full: every one of the fourteen is already claimed, and GrowthThreshold
# belongs to BirthRate. These twelve therefore act directly, in the manner of Synthetic Genomics
# and Asteroid Mining above, rather than through Modifiers.

iGraviticProduction = 4
iGenerativeCulture = 6
iJurisprudenceSpecialists = 1
iTransferGreatPeople = 2
iHydrosphericFood = 3
iAutonomousExperience = 4
iAgricultureResource = iWheat
iEducationResearch = 40
iTransitGoldPerRoute = 6
iMemeticAttitude = 1
iProbeGreatPeople = 3
iStellarGold = 60


@handler("BeginPlayerTurn")
def lateSyntheticRules(iGameTurn, iPlayer):
	"""The standing effects of the late Synthetic technologies.

	Recomputed every turn rather than applied once, because each is a continuous benefit rather
	than a one-off grant. Everything here is additive, so nothing needs the idempotent-delta
	discipline that the yield modifiers elsewhere require.
	"""
	if is_minor(iPlayer):
		return

	if not player(iPlayer).isExisting():
		return

	tPlayer = team(iPlayer)
	owned = cities.owner(iPlayer)

	# mass ceases to be a fixed property of matter
	if tPlayer.isHasTech(iGraviticEngineering):
		for city in owned:
			city.changeProduction(scale(iGraviticProduction))

	# culture that composes itself
	if tPlayer.isHasTech(iGenerativeArts):
		for city in owned:
			city.changeCulture(iPlayer, scale(iGenerativeCulture), True)

	# the ocean floor becomes habitable ground
	if tPlayer.isHasTech(iHydrosphericEngineering):
		for city in owned.coastal():
			city.changeFood(scale(iHydrosphericFood))

	# the mind outlives the body that carried it
	if tPlayer.isHasTech(iConsciousnessTransfer):
		for city in owned:
			city.changeGreatPeopleProgress(scale(iTransferGreatPeople))

	# the first thing we made to leave for good
	if tPlayer.isHasTech(iInterstellarProbe):
		capital_city = capital(iPlayer)
		if capital_city:
			capital_city.changeGreatPeopleProgress(scale(iProbeGreatPeople))

	# distance stops costing time
	if tPlayer.isHasTech(iVacuumTransit):
		iRoutes = owned.sum(lambda city: city.getTradeRoutes())
		if iRoutes > 0:
			player(iPlayer).changeGold(scale(iRoutes * iTransitGoldPerRoute))

	# a star, tended like a field
	if tPlayer.isHasTech(iStellarHusbandry):
		player(iPlayer).changeGold(scale(iStellarGold))


@handler("unitBuilt")
def autonomousWarfare(city, unit):
	"""War fought by machines that need no orders: every unit arrives already experienced."""
	iPlayer = unit.getOwner()

	if not team(iPlayer).isHasTech(iAutonomousWarfare):
		return

	unit.changeExperience(iAutonomousExperience, -1, False, False, False)


@handler("techAcquired")
def lateSyntheticGrants(iTech, iTeam, iPlayer):
	"""The two late rules that grant something once rather than every turn."""
	# food assembled rather than grown
	if iTech == iMolecularAgriculture:
		for city in cities.owner(iPlayer):
			if city.getFreeBonus(iAgricultureResource) <= 0:
				city.changeFreeBonus(iAgricultureResource, 1)

	# everything known, known by everyone, at once
	if iTech == iUniversalEducation:
		for city in cities.owner(iPlayer):
			city.setFreeSpecialistCount(iSpecialistScientist, city.getFreeSpecialistCount(iSpecialistScientist) + iJurisprudenceSpecialists)

	# one law, applied identically everywhere, by nobody
	if iTech == iUniversalJurisprudence:
		for city in cities.owner(iPlayer):
			city.setFreeSpecialistCount(iSpecialistStatesman, city.getFreeSpecialistCount(iSpecialistStatesman) + iJurisprudenceSpecialists)

	# ideas designed to spread, and spreading as designed
	if iTech == iMemeticEngineering:
		for iOther in players.major().existing().where(lambda p: p != iPlayer):
			player(iOther).AI_changeAttitudeExtra(iPlayer, iMemeticAttitude)
