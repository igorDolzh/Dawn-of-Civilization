# The Black Death's aftermath: the plague that ended serfdom.
#
# Plague.py already schedules five pandemics and already names this one - it is index 2 in
# tPlagueDates, dated 1347 +/- 50, with a Europe-specific virulence bonus. But mechanically it is
# just a bigger plague, and none of what made it the turning point of European history is there.
#
# What made it that was not the dying. It was what the survivors could afterwards demand. With a
# third of the workforce gone, labour became scarce and therefore expensive; wages rose, and the
# legal bindings that held peasants to the land stopped being enforceable. Serfdom collapsed in
# England and France - and, because the same scarcity let lords tighten their grip wherever the
# state was strong enough to help them, it deepened in eastern Europe. Both outcomes are offered.
#
# Nothing here schedules anything. The date, the jitter, the one-in-five cancellation and the
# Polish exception all live in Plague.py; this module only reads the turn it chose.

from Core import *
from Events import handler
from Popups import popup

import Stability


### CONSTANTS ###

# which of Plague's scheduled pandemics this is
iBlackDeath = 2

# how long after the outbreak the death toll is counted
iMeasureDelay = 15

# the share of its people a civilization must lose before the labour market changes at all
iLossThreshold = 20

# empire-wide production while labour is scarce and therefore dear
iShortageModifier = 25

# and the extra granted to those who let their peasants go
iEmancipationModifier = 20

iShortageDuration = 20

# coerced labour: holding on to one of these through the shortage is what costs stability
lCoercedLabour = [iSlavery, iManorialism, iCasteSystem]

# what emancipation installs instead
iFreeLabour = iIndividualism

# accumulates like iHumanRazePenalty, and decays the same way in Stability.decayPenalties
iEntrenchmentPenalty = -5


### POPUP ###

def emancipatePeasants():
	emancipate(active())


def entrenchSerfdom():
	entrench(active())


LABOUR_POPUP = (
	popup.text("TXT_KEY_BLACK_DEATH_LABOUR")
		.option(emancipatePeasants, "TXT_KEY_BLACK_DEATH_EMANCIPATE", button='Art/Interface/Buttons/Actions/Liberate.dds')
		.option(entrenchSerfdom, "TXT_KEY_BLACK_DEATH_ENTRENCH", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.build()
)


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkBlackDeath(iGameTurn):
	"""Record the population when the plague arrives, and count the dead once it has passed."""
	if scenarioStart():
		return

	iOutbreak = data.lGenericPlagueTurns[iBlackDeath]

	# -1 means Plague cancelled this pandemic, or it falls before the scenario begins
	if iOutbreak < 0:
		return

	if iGameTurn == iOutbreak:
		record()
	elif iGameTurn == iOutbreak + turns(iMeasureDelay):
		measure()


def record():
	for iPlayer in players.major().existing():
		data.players[iPlayer].iPrePlaguePopulation = player(iPlayer).getTotalPopulation()


def measure():
	"""Whoever lost enough people finds labour suddenly worth bidding for."""
	for iPlayer in players.major().existing():
		iBefore = data.players[iPlayer].iPrePlaguePopulation

		# never recorded, or born after the outbreak
		if iBefore <= 0:
			continue

		iLoss = 100 * (iBefore - player(iPlayer).getTotalPopulation()) / iBefore

		if iLoss >= iLossThreshold:
			shortage(iPlayer, iLoss)


### THE LABOUR SHORTAGE ###

def shortage(iPlayer, iLoss):
	setShortage(iPlayer, iShortageModifier, iShortageDuration)

	message(iPlayer, 'TXT_KEY_BLACK_DEATH_SHORTAGE', iLoss, iShortageModifier,
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iYellow)

	iCivic = coercedLabour(iPlayer)

	# nothing to abolish: the shortage is simply a windfall
	if iCivic is None:
		return

	if player(iPlayer).isHuman() and not autoplay():
		ask(iPlayer, iCivic)
	elif willEmancipate(iPlayer):
		emancipate(iPlayer)
	else:
		entrench(iPlayer)


def ask(iPlayer, iCivic):
	LABOUR_POPUP.text(infos.civic(iCivic).getText()) \
		.emancipatePeasants().entrenchSerfdom().launch()


def coercedLabour(iPlayer):
	"""The coerced-labour civic this player runs, if any."""
	for iCivic in lCoercedLabour:
		if has_civic(iPlayer, iCivic):
			return iCivic

	return None


def willEmancipate(iPlayer):
	"""Whether an AI lets its peasants go.

	Historically this split geographically, and for a reason worth encoding: serfdom collapsed in
	the west, where lords had to compete for scarce labour, and tightened in the east, where the
	state was strong enough to legislate peasants back into place. Proximity to the western
	European experience and an already-consultative government both push towards letting go.
	"""
	iValue = 40

	if civ(iPlayer) in dCivGroups[iCivGroupEurope]:
		iValue += 20

	if has_civic(iPlayer, iRepublic) or has_civic(iPlayer, iElective):
		iValue += 20

	if has_civic(iPlayer, iDespotism):
		iValue -= 20

	return iValue > 50


def emancipate(iPlayer):
	"""Let the peasants go. The shortage becomes an opportunity instead of a grievance."""
	player(iPlayer).setCivics(infos.civic(iFreeLabour).getCivicOptionType(), iFreeLabour)

	setShortage(iPlayer, iShortageModifier + iEmancipationModifier, iShortageDuration * 2)

	message(iPlayer, 'TXT_KEY_BLACK_DEATH_EMANCIPATED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iGreen)


def entrench(iPlayer):
	"""Bind them tighter. Legal, enforceable for now, and resented."""
	data.players[iPlayer].iSerfdomPenalty += iEntrenchmentPenalty

	Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_BLACK_DEATH_ENTRENCHED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)


### THE PRODUCTION MODIFIER ###

def setShortage(iPlayer, iModifier, iDuration):
	applyModifier(iPlayer, iModifier)
	data.players[iPlayer].iLabourShortageEnd = turn() + turns(iDuration)


def applyModifier(iPlayer, iTarget):
	"""Move this player's production modifier to iTarget, writing only the difference.

	changeYieldRateModifier is relative and the DLL keeps no record of who applied what, so the
	amount this module is responsible for is tracked here and only the delta is written. That is
	what makes it safe to call repeatedly, and what stops a reloaded save from either stranding
	the bonus or applying it twice.
	"""
	iCurrent = data.players[iPlayer].iLabourShortageModifier

	if iCurrent == iTarget:
		return

	player(iPlayer).changeYieldRateModifier(YieldTypes.YIELD_PRODUCTION, iTarget - iCurrent)
	data.players[iPlayer].iLabourShortageModifier = iTarget


@handler("BeginPlayerTurn")
def checkShortageEnd(iGameTurn, iPlayer):
	"""A generation passes and labour is ordinary again."""
	if data.players[iPlayer].iLabourShortageModifier == 0:
		return

	if iGameTurn < data.players[iPlayer].iLabourShortageEnd:
		return

	applyModifier(iPlayer, 0)

	message(iPlayer, 'TXT_KEY_BLACK_DEATH_SHORTAGE_OVER',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		color=iYellow)
