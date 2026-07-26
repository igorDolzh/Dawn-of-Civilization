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
}

# techs whose effect lives outside the modifier system, handled individually below
iPlagueImmunityTech = iSyntheticGenomics

# stability suppression is read directly by Stability.calculateStability
iStabilityTech = iPlanetaryConsciousness


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


### QUERIES ###

def hasRule(iPlayer, iTech):
	"""Whether this player holds a rule-breaking technology. Used by Stability."""
	return team(iPlayer).isHasTech(iTech)
