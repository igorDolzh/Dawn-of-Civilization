# The age of revolutions: regime change as something that happens to you.
#
# In this mod a civilization's government is only ever its own free choice. The player picks
# civics, and nothing ever takes that choice away. That makes the whole period from 1789 to 1848
# unrepresentable, because the states it happened to did not choose it: the Bastille, the
# Springtime of Nations, the abdications.
#
# Three things have to coincide, which is roughly what the historians ask for too - a grievance, an
# idea to give it shape, and a regime rigid enough to break rather than bend. The distinguishing
# mechanic is what follows: revolutions are contagious. 1830 and 1848 happened because 1789 had,
# and the monarchies that survived spent the next sixty years in coalitions against the ones that
# had not.

from Core import *
from Civics import civics
from Events import handler
from Popups import popup

import DynamicCivs
import Stability


### CONSTANTS ###

iRevolutionYear = 1789

# how often the world is examined
iCheckInterval = 3

# the ideas. One of these loose anywhere in the world is enough - revolutions are not had in
# isolation, and the civilization that revolts need not be the one that had the thought
lRevolutionaryIdeas = [iCivilLiberties, iSocialContract]

# governments rigid enough to break instead of bending
lAncienRegime = [iDespotism, iMonarchy]

# what a revolution installs
iRevolutionaryGovernment = iRepublic
iRevolutionaryLegitimacy = iConstitution

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


### POPUP ###

def leadRevolution():
	lead(active())


def suppressRevolution():
	suppress(active())


REVOLUTION_POPUP = (
	popup.text("TXT_KEY_REVOLUTION_CALL")
		.option(leadRevolution, "TXT_KEY_REVOLUTION_LEAD", button='Art/Interface/Buttons/Actions/Liberate.dds')
		.option(suppressRevolution, "TXT_KEY_REVOLUTION_SUPPRESS", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.build()
)


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkRevolutions(iGameTurn):
	if scenarioStart():
		return

	if iGameTurn < year(iRevolutionYear):
		return

	if not every(iCheckInterval):
		return

	decayPressure()

	# without the idea, grievance is just misery
	if not ideasExist():
		return

	for iPlayer in players.major().existing():
		if isRipe(iPlayer):
			revolt(iPlayer)


def ideasExist():
	return players.major().existing().any(lambda iPlayer: any(team(iPlayer).isHasTech(iTech) for iTech in lRevolutionaryIdeas))


def isRipe(iPlayer):
	"""Whether a revolution breaks out here, now."""
	# one upheaval per generation
	if turn() < data.players[iPlayer].iRevolutionTurn + turns(iCooldown):
		return False

	if not isAncienRegime(iPlayer):
		return False

	# stability() is a Core helper, not a Stability one, despite the name
	if stability(iPlayer) > iVulnerableStability:
		return False

	return rand(100) < iBaseChance + data.players[iPlayer].iRevolutionaryPressure


def isAncienRegime(iPlayer):
	return civics(iPlayer).iGovernment in lAncienRegime


### THE REVOLUTION ###

def revolt(iPlayer):
	# recorded before the choice, so the cooldown applies whichever way it goes
	data.players[iPlayer].iRevolutionTurn = turn()
	data.iRevolutions += 1

	if player(iPlayer).isHuman() and not autoplay():
		ask(iPlayer)
	else:
		lead(iPlayer)


def ask(iPlayer):
	REVOLUTION_POPUP.text() \
		.leadRevolution().suppressRevolution().launch()


def lead(iPlayer):
	"""Accept the new order. The government changes without anarchy, and so does its figurehead."""
	player(iPlayer).setCivics(infos.civic(iRevolutionaryGovernment).getCivicOptionType(), iRevolutionaryGovernment)
	player(iPlayer).setCivics(infos.civic(iRevolutionaryLegitimacy).getCivicOptionType(), iRevolutionaryLegitimacy)

	# the mod already picks leaders by era and ideology, and already knows who follows a monarchy
	DynamicCivs.checkLeader(iPlayer)

	message(iPlayer, 'TXT_KEY_REVOLUTION_LED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iGreen)

	spread(iPlayer)
	coalition(iPlayer)


def suppress(iPlayer):
	"""Hold the old order together by force. It works, for a while, and is remembered."""
	data.players[iPlayer].iSuppressionPenalty += iSuppressionPenalty

	Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_REVOLUTION_SUPPRESSED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)

	# a failed revolution is still an example - 1848 succeeded almost nowhere and changed everything
	spread(iPlayer)


### CONTAGION ###

def spread(iPlayer):
	"""Neighbours who watch a throne fall become likelier to lose their own."""
	for iOther in players.major().existing().where(lambda p: p != iPlayer):
		if not isNeighbour(iPlayer, iOther):
			continue

		data.players[iOther].iRevolutionaryPressure = min(
			iPressureCeiling,
			data.players[iOther].iRevolutionaryPressure + iPressurePerRevolution)


def decayPressure():
	"""The example fades. Without this, one revolution would eventually flip the whole world."""
	for iPlayer in players.major():
		iPressure = data.players[iPlayer].iRevolutionaryPressure

		if iPressure > 0:
			data.players[iPlayer].iRevolutionaryPressure = max(0, iPressure - iPressureDecay)


def isNeighbour(iPlayer, iOther):
	"""Close enough to be watching. Capitals, because that is where the news lands."""
	capital = player(iPlayer).getCapitalCity()
	other = player(iOther).getCapitalCity()

	if capital.isNone() or other.isNone():
		return False

	return distance(capital, other) <= iPressureRange


def coalition(iPlayer):
	"""Monarchies do not take kindly to regicide next door."""
	for iOther in players.major().existing().where(lambda p: p != iPlayer):
		if isAncienRegime(iOther) and isNeighbour(iPlayer, iOther):
			player(iOther).AI_changeAttitudeExtra(iPlayer, -2)
