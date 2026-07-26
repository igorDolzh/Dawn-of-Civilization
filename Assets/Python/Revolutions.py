# The age of revolutions: regime change as something that happens to you.
#
# In this mod a civilization's government is only ever its own free choice. The player picks
# civics, and nothing ever takes that choice away. That makes the whole period from 1789 to 1917
# unrepresentable, because the states it happened to did not choose it: the Bastille, the
# Springtime of Nations, the abdications.
#
# There are two kinds here, and they are not variations on one theme - they differ in both halves.
#
#   Liberal (1789, 1830, 1848): a fiscal crisis and an educated bourgeoisie break an absolute
#   monarchy, and a constitutional republic replaces it.
#
#   Socialist (1917): a long unsuccessful war dissolves an industrial state, and a party-state
#   with a planned economy replaces it. Note what it does NOT require - an absolute monarchy.
#   Russia in October was already a republic; February had seen to that. A socialist revolution
#   can follow a liberal one, and historically did.
#
# The socialist branch is checked first, because a war-broken autocracy satisfies both and the
# liberal outcome would otherwise always win the race - which is precisely the failure mode where
# 1917 produces Kerensky and stops there.
#
# Contagion is kind-aware. A liberal revolution makes liberal revolutions likelier nearby; a
# socialist one raises socialist pressure, which is the Comintern.

from Core import *
from Civics import civics
from Events import handler
from Popups import popup

import DynamicCivs
import Stability


### CONSTANTS ###

(iLiberal, iSocialist) = range(2)

iLiberalYear = 1789

# a backstop only: the Collectivism requirement below does the real gating, and an industrial
# working class cannot exist before it
iSocialistYear = 1900

# how often the world is examined
iCheckInterval = 3

# governments rigid enough to break instead of bending. Only the liberal revolution needs one
lAncienRegime = [iDespotism, iMonarchy]

# the liberal idea. One of these loose anywhere in the world is enough - revolutions are not had
# in isolation, and the civilization that revolts need not be the one that had the thought
lLiberalIdeas = [iCivilLiberties, iSocialContract]

iLiberalGovernment = iRepublic
iLiberalLegitimacy = iConstitution

# the socialist precondition is not an idea but a class: Collectivism stands in for having an
# industrial workforce large enough to matter
iSocialistIdea = iCollectivism

# Central Planning alone satisfies Civics.isCommunist, so the revolution can succeed in the
# Industrial era and acquire its constitutional form later
iSocialistEconomy = iCentralPlanning
iSocialistGovernment = iStateParty
iSocialistGovernmentTech = iMacroeconomics

# a war must have lasted this long to be the kind that dissolves a state. Matches the threshold
# Stability already uses for its own war-duration penalty
iWarDuration = 20

# a civilization must be no more stable than this to be vulnerable at all
iVulnerableStability = iStabilityShaky

# chance per check, before the example of the neighbours is added
iBaseChance = 10

# contagion
iPressurePerRevolution = 20
iPressureCeiling = 60
iPressureDecay = 2
iPressureRange = 12

# turns before the same civilization can go through it again
iCooldown = 30

# accumulates like iHumanRazePenalty, and decays the same way in Stability.decayPenalties
iSuppressionPenalty = -8


### POPUPS ###

def leadRevolution():
	lead(active())


def suppressRevolution():
	suppress(active(), iLiberal)


def leadSocialistRevolution():
	sovietise(active())


def suppressSocialistRevolution():
	suppress(active(), iSocialist)


REVOLUTION_POPUP = (
	popup.text("TXT_KEY_REVOLUTION_CALL")
		.option(leadRevolution, "TXT_KEY_REVOLUTION_LEAD", button='Art/Interface/Buttons/Actions/Liberate.dds')
		.option(suppressRevolution, "TXT_KEY_REVOLUTION_SUPPRESS", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.build()
)

SOCIALIST_POPUP = (
	popup.text("TXT_KEY_SOCIALIST_REVOLUTION_CALL")
		.option(leadSocialistRevolution, "TXT_KEY_SOCIALIST_REVOLUTION_LEAD", button='Art/Interface/Buttons/Actions/Liberate.dds')
		.option(suppressSocialistRevolution, "TXT_KEY_SOCIALIST_REVOLUTION_SUPPRESS", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.build()
)


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkRevolutions(iGameTurn):
	if scenarioStart():
		return

	if iGameTurn < year(iLiberalYear):
		return

	if not every(iCheckInterval):
		return

	decayPressure()

	for iPlayer in players.major().existing():
		if not canRevolt(iPlayer):
			continue

		# socialist first: a war-broken autocracy satisfies both, and the liberal outcome would
		# otherwise always win, leaving 1917 stuck at the Provisional Government
		if isSocialistRipe(iPlayer):
			revolt(iPlayer, iSocialist)
		elif isLiberalRipe(iPlayer):
			revolt(iPlayer, iLiberal)


def canRevolt(iPlayer):
	"""One upheaval per generation, whichever kind and whichever way it went."""
	return turn() >= data.players[iPlayer].iRevolutionTurn + turns(iCooldown)


### THE LIBERAL REVOLUTION ###

def isLiberalRipe(iPlayer):
	# without the idea, grievance is just misery
	if not ideasExist():
		return False

	if not isAncienRegime(iPlayer):
		return False

	# stability() is a Core helper, not a Stability one, despite the name
	if stability(iPlayer) > iVulnerableStability:
		return False

	return rand(100) < iBaseChance + data.players[iPlayer].iRevolutionaryPressure


def ideasExist():
	return players.major().existing().any(lambda iPlayer: any(team(iPlayer).isHasTech(iTech) for iTech in lLiberalIdeas))


def isAncienRegime(iPlayer):
	return civics(iPlayer).iGovernment in lAncienRegime


def lead(iPlayer):
	"""Accept the new order. The government changes without anarchy, and so does its figurehead."""
	player(iPlayer).setCivics(infos.civic(iLiberalGovernment).getCivicOptionType(), iLiberalGovernment)
	player(iPlayer).setCivics(infos.civic(iLiberalLegitimacy).getCivicOptionType(), iLiberalLegitimacy)

	# the mod already picks leaders by era and ideology, and already knows who follows a monarchy
	DynamicCivs.checkLeader(iPlayer)

	message(iPlayer, 'TXT_KEY_REVOLUTION_LED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iGreen)

	spread(iPlayer, iLiberal)
	coalition(iPlayer, iLiberal)


### THE SOCIALIST REVOLUTION ###

def isSocialistRipe(iPlayer):
	if turn() < year(iSocialistYear):
		return False

	# an industrial working class
	if not team(iPlayer).isHasTech(iSocialistIdea):
		return False

	# already there
	if has_civic(iPlayer, iSocialistEconomy):
		return False

	if not isLosingLongWar(iPlayer):
		return False

	if stability(iPlayer) > iVulnerableStability:
		return False

	return rand(100) < iBaseChance + data.players[iPlayer].iSocialistPressure


def isLosingLongWar(iPlayer):
	"""A long war going badly - the condition that actually broke the Tsarist state.

	Both halves matter. A short disaster ends in a peace treaty and a long victorious war ends in
	a parade; it is the long unsuccessful one that dissolves an army into a revolution. The
	duration threshold matches the one Stability already uses for its own war-weariness penalty,
	and the war start turns are the ones Stability.startWar already records.
	"""
	tPlayer = team(iPlayer)

	for iEnemy in players.major().existing().where(lambda p: p != iPlayer):
		if not tPlayer.isAtWar(iEnemy):
			continue

		iWarTurns = turn() - data.players[iPlayer].dWarStartTurn.get(iEnemy, turn())

		if iWarTurns < turns(iWarDuration):
			continue

		if team(iEnemy).AI_getWarSuccess(iPlayer) > tPlayer.AI_getWarSuccess(iEnemy):
			return True

	return False


def sovietise(iPlayer):
	"""The planned economy first, the party-state when the century catches up with it."""
	player(iPlayer).setCivics(infos.civic(iSocialistEconomy).getCivicOptionType(), iSocialistEconomy)

	# the party-state is a Global era institution. Before Macroeconomics the revolution has its
	# economy but not yet its constitutional form, which is roughly the gap from 1917 to 1922
	if team(iPlayer).isHasTech(iSocialistGovernmentTech):
		player(iPlayer).setCivics(infos.civic(iSocialistGovernment).getCivicOptionType(), iSocialistGovernment)

	DynamicCivs.checkLeader(iPlayer)

	message(iPlayer, 'TXT_KEY_SOCIALIST_REVOLUTION_LED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)

	spread(iPlayer, iSocialist)
	coalition(iPlayer, iSocialist)


### SHARED ###

def revolt(iPlayer, iKind):
	# recorded before the choice, so the cooldown applies whichever way it goes
	data.players[iPlayer].iRevolutionTurn = turn()
	data.iRevolutions += 1

	if player(iPlayer).isHuman() and not autoplay():
		ask(iPlayer, iKind)
	elif iKind == iSocialist:
		sovietise(iPlayer)
	else:
		lead(iPlayer)


def ask(iPlayer, iKind):
	if iKind == iSocialist:
		SOCIALIST_POPUP.text() \
			.leadSocialistRevolution().suppressSocialistRevolution().launch()
	else:
		REVOLUTION_POPUP.text() \
			.leadRevolution().suppressRevolution().launch()


def suppress(iPlayer, iKind):
	"""Hold the old order together by force. It works, for a while, and is remembered."""
	data.players[iPlayer].iSuppressionPenalty += iSuppressionPenalty

	Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_REVOLUTION_SUPPRESSED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)

	# a failed revolution is still an example - 1848 succeeded almost nowhere and changed everything
	spread(iPlayer, iKind)


### CONTAGION ###

def spread(iPlayer, iKind):
	"""Neighbours who watch a throne fall become likelier to lose their own.

	Kind-aware: a liberal revolution does not make its neighbours communist, and a socialist one
	does not make them constitutional monarchies.
	"""
	for iOther in players.major().existing().where(lambda p: p != iPlayer):
		if not isNeighbour(iPlayer, iOther):
			continue

		setPressure(iOther, iKind, pressure(iOther, iKind) + iPressurePerRevolution)


def decayPressure():
	"""The example fades. Without this, one revolution would eventually flip the whole world."""
	for iPlayer in players.major():
		for iKind in (iLiberal, iSocialist):
			setPressure(iPlayer, iKind, pressure(iPlayer, iKind) - iPressureDecay)


def pressure(iPlayer, iKind):
	if iKind == iSocialist:
		return data.players[iPlayer].iSocialistPressure

	return data.players[iPlayer].iRevolutionaryPressure


def setPressure(iPlayer, iKind, iValue):
	"""The only writer, so the ceiling and the floor cannot be bypassed."""
	iValue = max(0, min(iPressureCeiling, iValue))

	if iKind == iSocialist:
		data.players[iPlayer].iSocialistPressure = iValue
	else:
		data.players[iPlayer].iRevolutionaryPressure = iValue


def isNeighbour(iPlayer, iOther):
	"""Close enough to be watching. Capitals, because that is where the news lands."""
	capital = player(iPlayer).getCapitalCity()
	other = player(iOther).getCapitalCity()

	if capital.isNone() or other.isNone():
		return False

	return distance(capital, other) <= iPressureRange


def coalition(iPlayer, iKind):
	"""Nobody takes kindly to regicide next door.

	The liberal case is a neighbourhood affair - the monarchies that could see it. The socialist
	one is not: the intervention in the Russian Civil War came from Britain, France, the United
	States and Japan, none of them neighbours.
	"""
	for iOther in players.major().existing().where(lambda p: p != iPlayer):
		if iKind == iSocialist:
			if not has_civic(iOther, iSocialistEconomy):
				player(iOther).AI_changeAttitudeExtra(iPlayer, -2)
		elif isAncienRegime(iOther) and isNeighbour(iPlayer, iOther):
			player(iOther).AI_changeAttitudeExtra(iPlayer, -2)
