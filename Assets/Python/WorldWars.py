# The World Wars: the outbreak the mod never had.
#
# Congresses.py already contains most of a world war. It can recognise one - startsGlobalWar fires
# when at least two powers face two others and half the top quartile of the world is involved - and
# it already ends one properly, forcing a general peace and convening a congress of winners and
# losers, which is Vienna and Versailles in the same machinery.
#
# What it cannot do is start one. determineAlliances derives the two sides from wars that already
# exist, so the whole system is purely reactive: it labels a great-power war a world war after the
# fact. Nothing ever divides the world into blocs and lights the fuse.
#
# So this module supplies only the missing half. It forms the blocs, declares the war, and mobilises
# the economies. Everything after that - the alliance bookkeeping, the peace, the conference that
# redraws the map - is Congresses.py doing what it already does. The one deliberate design
# constraint is that the outbreak must look to that code exactly like any other war, so that it
# picks the war up on its own rather than needing to be told.

from Core import *
from Events import handler

import Congresses


### CONSTANTS ###

# war -> year. Jittered by the seed, so it is not the same turn in every game
dWorldWars = {
	1: 1914,
	2: 1939,
}

iYearVariation = 4

# how many great powers are drawn into the blocs
iPowers = 8

# both sides need at least this many, or Congresses.startsGlobalWar will not recognise it
iMinimumBloc = 2

# the war economy, while a world war is being fought
iMobilisation = 30


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkWorldWars(iGameTurn):
	if scenarioStart():
		return

	for iWar, iYear in dWorldWars.items():
		if iWar in data.lWorldWarsFought:
			continue

		if iGameTurn != year(iYear).deviate(iYearVariation, data.iSeed):
			continue

		outbreak(iWar)


def outbreak(iWar):
	"""Divide the great powers and let them at each other."""
	# the congress system is what recognises and ends a world war. Without it there is no
	# machinery to hand the war to, and the United Nations has retired the whole idea
	if not Congresses.isCongressEnabled():
		return

	# one at a time
	if Congresses.isGlobalWar():
		return

	lAlliance, lCoalition = blocs()

	if len(lAlliance) < iMinimumBloc or len(lCoalition) < iMinimumBloc:
		return

	data.lWorldWarsFought.append(iWar)

	declare(lAlliance, lCoalition)
	mobilise(lAlliance + lCoalition)

	announce(iWar, lAlliance + lCoalition)


### THE BLOCS ###

def blocs():
	"""Split the great powers in two, around the strongest and whoever likes it least.

	Returns plain lists of player ids rather than collections. Players.of takes varargs and its
	constructor rejects anything that is not a flat sequence of ints or Civs, so building a
	collection element by element is a trap; lists are what the rest of this module wants anyway.

	Deliberately built from the diplomacy already in the game rather than from a table of
	historical alignments. A game in which Britain and Germany are friends and France is the
	menace should produce that war, not a scripted 1914 that ignores everything the player did.
	"""
	powers = players.major().existing().where(lambda p: not team(p).isAVassal()).highest(iPowers, lambda p: team(p).getPower(True))

	lPowers = [iPlayer for iPlayer in powers]

	if len(lPowers) < 2 * iMinimumBloc:
		return [], []

	iFirst = max(lPowers, key=lambda p: team(p).getPower(True))
	lRest = [iPlayer for iPlayer in lPowers if iPlayer != iFirst]

	# the strongest power's least favourite great power leads the other side
	iSecond = min(lRest, key=lambda p: player(iFirst).AI_getAttitude(p))

	lAlliance = [iFirst]
	lCoalition = [iSecond]

	# everyone else goes where they are more comfortable
	for iPlayer in lRest:
		if iPlayer == iSecond:
			continue

		if player(iPlayer).AI_getAttitude(iFirst) >= player(iPlayer).AI_getAttitude(iSecond):
			lAlliance.append(iPlayer)
		else:
			lCoalition.append(iPlayer)

	return lAlliance, lCoalition


def declare(lAlliance, lCoalition):
	"""Everyone against everyone on the other side.

	The leaders go first, so that Congresses.onChangeWar sees the largest pair and records them
	as the war's principals. The rest follow and are picked up as allies by determineAlliances.
	"""
	for iAttacker in lAlliance:
		for iDefender in lCoalition:
			if team(iAttacker).isAtWar(player(iDefender).getTeam()):
				continue

			if team(iAttacker).isAVassal() or team(iDefender).isAVassal():
				continue

			team(iAttacker).declareWar(player(iDefender).getTeam(), False, WarPlanTypes.WARPLAN_TOTAL)


### THE WAR ECONOMY ###

def mobilise(lParticipants):
	for iPlayer in lParticipants:
		applyMobilisation(iPlayer, iMobilisation)


@handler("BeginPlayerTurn")
def checkDemobilisation(iGameTurn, iPlayer):
	"""The war economy lasts exactly as long as the war.

	Congresses clears iGlobalWarAttacker when the principals make peace, so that is the signal -
	no separate timer to drift out of step with the war it is supposed to be tracking.
	"""
	if data.players[iPlayer].iMobilisationModifier == 0:
		return

	if Congresses.isGlobalWar():
		return

	applyMobilisation(iPlayer, 0)

	message(iPlayer, 'TXT_KEY_WORLD_WAR_DEMOBILISED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		color=iYellow)


def applyMobilisation(iPlayer, iTarget):
	"""Move this player's war-economy modifier to iTarget, writing only the difference.

	changeYieldRateModifier is relative and the DLL records no attribution, so the amount this
	module is responsible for is tracked separately from the one BlackDeath tracks. Both write
	deltas against their own stored figure, so they compose without either stranding the other.
	"""
	iCurrent = data.players[iPlayer].iMobilisationModifier

	if iCurrent == iTarget:
		return

	player(iPlayer).changeYieldRateModifier(YieldTypes.YIELD_PRODUCTION, iTarget - iCurrent)
	data.players[iPlayer].iMobilisationModifier = iTarget


### NOTIFICATION ###

def announce(iWar, lParticipants):
	if autoplay():
		return

	for iPlayer in lParticipants:
		message(iPlayer, 'TXT_KEY_WORLD_WAR_OUTBREAK', iWar, iMobilisation,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
			color=iRed, force=True)
