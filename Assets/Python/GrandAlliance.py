# The Grand Alliance: the world against the anachronism.
#
# Without this the advanced civilization scenario has no opposition worth the name. Civilization IV
# has almost no machinery for ganging up on a leader: AI_getAttitudeVal applies
# (WorseRankDifference * rankDifference) / (civsAlive + 1), which for a runaway first place among
# thirty-one civilizations comes to about one point of attitude, and AI_getCompetitorAttitude only
# fires between civilizations of similar rank, so it returns nothing at all for a bottom-half
# medieval state looking at a superpower. AIWars.planWars picks one attacker and one target at a
# time and never prefers the strongest. The result is thirty civilizations that mildly dislike you
# and fight each other.
#
# So this supplies three things the game does not: a grievance that grows, a reason to combine, and
# enough industry to make combining matter.
#
# Deliberately built from what the mod already does rather than from anything new. The escalation
# is the tracked-delta discipline of BlackDeath.applyModifier and WorldWars.applyMobilisation; the
# pacts and the joint declaration are the shape of WorldWars.blocs and outbreak. Nothing here is a
# mechanism the mod has not already accepted somewhere else.

from Core import *
from Events import handler

import SimultaneousStart


### CONSTANTS ###

# How much the world resents the anachronism, per era it is ahead. Three eras at birth, so twelve
# points before anything has even happened - enough to sit below every leader's tech refusal
# threshold and most of their war thresholds, which is the point.
iResentmentPerEra = -4

# and what each city taken from anyone adds on top, so conquest compounds the grievance
iResentmentPerConquest = -2

# nobody's patience is infinite, but the number has to stop somewhere or attitude saturates and
# further outrages stop registering
iMaximumResentment = -30


# What the backward world gets to fight with, as a production modifier. Given only while it is
# behind, so it is a handicap that closes rather than a permanent gift: a civilization that catches
# up loses it.
iAllianceProduction = 25

# and the tech gap at which it begins - one era behind is a race, two is a crisis
iProductionGap = 2


# Cities the advanced civilization must take before the world stops watching and starts signing.
iPactThreshold = 2

# and before it declares
iWarThreshold = 5


### RESENTMENT ###

@handler("BeginGameTurn")
def maintainAlliance(iGameTurn):
	"""Keep the world's opinion of the anachronism current."""
	if not SimultaneousStart.advancedEnabled():
		return

	iAdvanced = SimultaneousStart.advancedPlayer()

	if iAdvanced < 0 or not player(iAdvanced).isAlive():
		return

	for iPlayer in players.major().existing().without(iAdvanced):
		resent(iPlayer, iAdvanced)
		subsidise(iPlayer, iAdvanced)

	combine(iAdvanced)


def resentment(iAdvanced):
	"""How much the world holds against the advanced civilization, as a negative number."""
	iEras = player(iAdvanced).getCurrentEra() - SimultaneousStart.iBackwardEra
	iTotal = max(0, iEras) * iResentmentPerEra + data.iAllianceConquests * iResentmentPerConquest

	return max(iMaximumResentment, iTotal)


def resent(iPlayer, iAdvanced):
	"""Apply the grievance, as the difference from what was applied before.

	AI_changeAttitudeExtra is relative and the DLL records no attribution, so the amount this
	module is responsible for is tracked separately - Crusades, Congresses and the slave trade all
	write to the same field, and overwriting it would silently undo them.
	"""
	iResentment = resentment(iAdvanced)
	iApplied = data.dAllianceResentment.get(iPlayer, 0)

	if iResentment == iApplied:
		return

	player(iPlayer).AI_changeAttitudeExtra(iAdvanced, iResentment - iApplied)
	data.dAllianceResentment[iPlayer] = iResentment


### INDUSTRY ###

def subsidise(iPlayer, iAdvanced):
	"""Production for anyone meaningfully behind the advanced civilization.

	Withdrawn the moment they are not, which is what makes it a handicap rather than a gift. Same
	tracked delta as the resentment above and for the same reason: changeYieldRateModifier is
	relative, and BlackDeath and WorldWars are both already writing to it.
	"""
	iGap = player(iAdvanced).getCurrentEra() - player(iPlayer).getCurrentEra()
	iSubsidy = iGap >= iProductionGap and iAllianceProduction or 0
	iApplied = data.dAllianceProduction.get(iPlayer, 0)

	if iSubsidy == iApplied:
		return

	player(iPlayer).changeYieldRateModifier(YieldTypes.YIELD_PRODUCTION, iSubsidy - iApplied)
	data.dAllianceProduction[iPlayer] = iSubsidy

	if iSubsidy > 0:
		message(iPlayer, 'TXT_KEY_ALLIANCE_SUBSIDY', iSubsidy,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iYellow)


### COMBINATION ###

@handler("cityAcquired")
def countConquest(iOwner, iPlayer, city, bConquest):
	"""Every city the advanced civilization takes is remembered by everyone."""
	if not SimultaneousStart.advancedEnabled():
		return

	if not bConquest:
		return

	if iPlayer != SimultaneousStart.advancedPlayer():
		return

	data.iAllianceConquests += 1


def combine(iAdvanced):
	"""Pacts first, then war. The world watches, then arms, then acts.

	Two stages because one is not a story. A world that declares the moment it is outmatched gives
	no time to build anything; a world that never declares is scenery.
	"""
	if data.iAllianceConquests < iPactThreshold:
		return

	lAllies = [iPlayer for iPlayer in players.major().existing().without(iAdvanced)
			   if not player(iPlayer).isHuman()]

	if len(lAllies) < 2:
		return

	sign(lAllies)

	if data.iAllianceConquests >= iWarThreshold and not data.bAllianceDeclared:
		declare(lAllies, iAdvanced)


def sign(lAllies):
	"""Defensive pacts among everyone not the anachronism.

	Only between civilizations that have met and are not already at war with each other, because a
	pact between strangers is meaningless and one between belligerents is impossible.
	"""
	for iPlayer in lAllies:
		for iOther in lAllies:
			if iPlayer >= iOther:
				continue

			tPlayer, tOther = team(iPlayer), team(iOther)

			if not tPlayer.isHasMet(player(iOther).getTeam()):
				continue

			if tPlayer.isAtWar(player(iOther).getTeam()):
				continue

			if tPlayer.isDefensivePact(player(iOther).getTeam()):
				continue

			tPlayer.signDefensivePact(player(iOther).getTeam())


def declare(lAllies, iAdvanced):
	"""The world goes to war at once.

	Together rather than in sequence, which is the entire difference between this and what the game
	does unaided: thirty civilizations declaring one at a time are thirty wars won separately.
	"""
	data.bAllianceDeclared = True

	tAdvanced = player(iAdvanced).getTeam()

	for iPlayer in lAllies:
		if team(iPlayer).isAtWar(tAdvanced):
			continue

		if not team(iPlayer).isHasMet(tAdvanced):
			continue

		if team(iPlayer).isAVassal():
			continue

		team(iPlayer).declareWar(tAdvanced, False, WarPlanTypes.WARPLAN_TOTAL)

	message(iAdvanced, 'TXT_KEY_ALLIANCE_DECLARED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iRed, force=True)
