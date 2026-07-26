# The Crusades as scripted historical events.
#
# Replaces the vanilla random-event quest, which fired in any era against no particular place and
# declared war on the player's behalf without asking. Here the call goes out on its historical
# dates, every Catholic power is asked, and answering or refusing both leave a mark.
#
# Follows the Reformation's shape: a real choice, consequences applied in Python, and the decision
# recorded in StoredData so the world can react to it later.

from Core import *
from RFCUtils import *
from Events import handler
from Popups import popup

import Stability


### CONSTANTS ###

tJerusalem = (84, 45)

# the crusader states, used as landing points for the armies that answer the call
lLevantTargets = [(84, 45), (85, 50), (84, 47), (84, 46)]

# crusade -> (year, army size, defender reinforcement)
dCrusades = {
	1: (1095, 4, 1),   # the call succeeds; Jerusalem is takeable
	2: (1147, 3, 3),   # historically a costly failure: weaker call, stronger defenders
	3: (1189, 5, 4),   # response to Saladin, and only if Jerusalem has been lost again
}

# how far the AI's willingness to answer is swayed by its attitude to the caller
iAnswerThreshold = 55

# decision values recorded per player per crusade
(iNotAsked, iRefused, iAnswered) = range(3)

# refusing the call accumulates a stability penalty the same way razing a city does,
# so it decays rather than being permanent
iRefusalPenalty = -6


### POPUP ###

def answerCall(iCrusade):
	answer(active(), iCrusade)


def refuseCall(iCrusade):
	refuse(active(), iCrusade)


CRUSADE_POPUP = (
	popup.text("TXT_KEY_CRUSADE_CALL")
		.option(answerCall, "TXT_KEY_CRUSADE_ANSWER", button='Art/Interface/Buttons/Actions/Join.dds')
		.option(refuseCall, "TXT_KEY_CRUSADE_REFUSE", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.build()
)


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkCrusades(iGameTurn):
	for iCrusade, (iYear, _, _) in dCrusades.items():
		if iGameTurn == year(iYear):
			call(iCrusade)


def call(iCrusade):
	"""Proclaim a crusade, if there is anything to crusade for."""
	if scenarioStart():
		return

	# already resolved: the guard makes the handler idempotent if the turn is replayed
	if data.dCrusadeDecisions.get(iCrusade):
		return

	# the Third Crusade answers the loss of Jerusalem, so it needs Jerusalem to have been lost
	if iCrusade == 3 and not data.bJerusalemFallen:
		return

	target = holder()
	if target < 0:
		return

	called = players.major().existing().religion(iCatholicism).where(lambda p: p != target)
	if called.none():
		return

	data.dCrusadeDecisions[iCrusade] = {}

	if not autoplay() and plot(tJerusalem).isRevealed(player().getTeam(), False):
		plot(tJerusalem).cameraLookAt()

	for iPlayer in called:
		if player(iPlayer).isHuman() and not autoplay():
			ask(iPlayer, iCrusade)
		elif willAnswer(iPlayer, target):
			answer(iPlayer, iCrusade)
		else:
			refuse(iPlayer, iCrusade)


def ask(iPlayer, iCrusade):
	CRUSADE_POPUP.text(text(dCallKeys[iCrusade]), name(holder())) \
		.answerCall().refuseCall().launch(iCrusade)


def willAnswer(iPlayer, target):
	"""Whether an AI answers. Piety and hostility to the holder both push towards yes."""
	iValue = 30

	if has_civic(iPlayer, iFanaticism):
		iValue += 30
	if has_civic(iPlayer, iClergy) or has_civic(iPlayer, iMonasticism):
		iValue += 15
	if has_civic(iPlayer, iSecularism):
		iValue -= 30

	if team(iPlayer).isAtWar(player(target).getTeam()):
		iValue += 25

	iValue -= 5 * player(iPlayer).AI_getAttitude(target)

	return iValue >= iAnswerThreshold


### OUTCOMES ###

def answer(iPlayer, iCrusade):
	"""Commit to the crusade: an army lands in the Levant and war is declared."""
	_, iArmy, iDefenders = dCrusades[iCrusade]
	target = holder()
	if target < 0:
		return

	record(iCrusade, iPlayer, iAnswered)

	muster(iPlayer, iArmy)
	reinforce(target, iDefenders)
	makeWar(iPlayer, target)

	# standing rises among those who also answered, and falls across the Muslim world
	for iOther in answered(iCrusade):
		if iOther != iPlayer:
			player(iOther).AI_changeAttitudeExtra(iPlayer, 2)
			player(iPlayer).AI_changeAttitudeExtra(iOther, 2)

	for iMuslim in players.major().existing().religion(iIslam):
		player(iMuslim).AI_changeAttitudeExtra(iPlayer, -3)
		# a decaying memory rather than a permanent grudge, so relations can recover
		player(iMuslim).AI_changeMemoryCount(iPlayer, MemoryTypes.MEMORY_DECLARED_WAR, turns(10))

	message(iPlayer, 'TXT_KEY_CRUSADE_ANSWERED', name(target),
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iGreen, location=tJerusalem)

	events.fireEvent("crusade", iPlayer, iCrusade, True)


def refuse(iPlayer, iCrusade):
	"""Decline the call: nothing is spent, but it is noticed."""
	record(iCrusade, iPlayer, iRefused)

	for iOther in answered(iCrusade):
		player(iOther).AI_changeAttitudeExtra(iPlayer, -1)

	if player(iPlayer).isHuman():
		data.iHumanRefusedCrusadePenalty += iRefusalPenalty
		Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_CRUSADE_REFUSED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		color=iRed)

	events.fireEvent("crusade", iPlayer, iCrusade, False)


### MECHANICS ###

def muster(iPlayer, iArmy):
	"""Land a crusading army on the nearest free ground to the Holy Land."""
	site = landing(iPlayer)
	if site is None:
		return

	dUnits = {
		iCityAttack: iArmy,
		iSiege: max(1, iArmy - 1),
		iShockCity: max(1, iArmy / 2),
		iDefend: max(1, iArmy / 2),
	}
	createRoleUnits(iPlayer, site, dUnits.items(), iExperience=2, bCreateSettlers=False)


def landing(iPlayer):
	"""A crusader state site that is free, else any passable land beside Jerusalem."""
	for tTarget in lLevantTargets:
		target = plot(tTarget)
		if not target.isCity() and target.isFlatlands():
			return target

	return plots.ring(tJerusalem, radius=1).where(lambda p: not p.isWater() and not p.isPeak() and not p.isCity()).first()


def reinforce(target, iDefenders):
	"""Give the holder of Jerusalem a garrison, so the crusade is opposed."""
	city = plot(tJerusalem).getPlotCity()
	if not city or city.isNone():
		return

	# ease off when the human is the one being crusaded against, as the conquistador
	# code does for a human victim
	if player(target).isHuman():
		iDefenders = max(1, iDefenders - 1)

	createRoleUnits(target, city, [(iDefend, iDefenders), (iCounter, max(1, iDefenders / 2))],
		iExperience=2, bCreateSettlers=False)


def makeWar(iPlayer, target):
	if team(iPlayer).isAtWar(player(target).getTeam()):
		return

	team(iPlayer).setDefensivePact(player(target).getTeam(), False)
	team(iPlayer).declareWar(player(target).getTeam(), True, WarPlanTypes.WARPLAN_TOTAL)


### JERUSALEM ###

@handler("cityAcquired")
def watchJerusalem(iOwner, iPlayer, city, bConquest):
	"""Remember whether the Holy City has been lost again, which gates the Third Crusade."""
	if location(city) != tJerusalem:
		return

	if player(iPlayer).getStateReligion() == iIslam:
		data.bJerusalemFallen = True
	elif player(iPlayer).getStateReligion() == iCatholicism:
		data.bJerusalemFallen = False


### QUERIES ###

def holder():
	"""The Muslim power holding Jerusalem, or -1 if it is not a crusading target."""
	city = plot(tJerusalem).getPlotCity()
	if not city or city.isNone():
		return -1

	iOwner = city.getOwner()
	if is_minor(iOwner):
		return -1
	if player(iOwner).getStateReligion() != iIslam:
		return -1

	return iOwner


def answered(iCrusade):
	return [iPlayer for iPlayer, iDecision in data.dCrusadeDecisions.get(iCrusade, {}).items()
			if iDecision == iAnswered]


def record(iCrusade, iPlayer, iDecision):
	data.dCrusadeDecisions.setdefault(iCrusade, {})[iPlayer] = iDecision


dCallKeys = {
	1: "TXT_KEY_CRUSADE_CALL_FIRST",
	2: "TXT_KEY_CRUSADE_CALL_SECOND",
	3: "TXT_KEY_CRUSADE_CALL_THIRD",
}
