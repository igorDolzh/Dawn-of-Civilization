# The American Civil War: the one secession the Union fought to reverse.
#
# The mod already models secession thoroughly, but always as a symptom - a state that has grown
# too large, too foreign or too unstable sheds territory it can no longer hold, and the territory
# stays shed. That is the wrong shape for 1861. The Confederacy did not secede because the Union
# was overextended; it seceded over a single institution, and the Union fought a war specifically
# to undo it, and won.
#
# So this is a secession with a reconquest condition attached, and the reconquest is what abolishes
# slavery. That ordering is deliberate and it is the historical one: emancipation followed the war
# rather than causing it. A player who lets the South go keeps slavery and keeps paying for it.
#
# Written as a table rather than as hardcoded American constants, because the shape - slave region
# secedes from a slaveholding state, war follows, victory abolishes - is not unique to America.
# Only the entry is.

from Core import *
from Events import handler
from Popups import popup
from RFCUtils import createRoleUnits

import Secession
import Stability


### CONSTANTS ###

iCivilWarYear = 1861

# how far the date may drift, so it is not the same turn in every game
iYearVariation = 3

# civ -> (regions that secede, minimum cities before it is a war rather than a riot)
dCivilWars = {
	iAmerica: ([rDeepSouth], 3),
}

# The civics that actually end slavery, in the order they should be preferred, each with the tech
# it needs. This is not the same question as "does the player run the Slavery civic".
#
# CvPlayer::canUseSlaves is permissive by default: slavery is legal unless a civic sets
# bNoSlavery, and only these three do. Individualism - the obvious Society civic for a
# 19th century republic, and the one the Black Death emancipation uses - does NOT, so adopting it
# frees the peasants of Europe without touching the plantations of the South. Exactly the
# distinction the war was about.
lAbolitionCivics = [
	(iEgalitarianism, iCivilRights),     # Society: abolition as a civil right
	(iNationhood, iNationalism),         # Territory: one nation, and therefore no chattel in it
	(iMultilateralism, iGeopolitics),    # Territory: abolition by treaty
]

# who the seceded cities belong to
iConfederacy = iIndependent

# defenders granted to each seceding city, and reinforcements to the Union if it fights
iRebelDefenders = 2
iUnionReinforcements = 4

# letting them go is a permanent admission, and costs accordingly
iSecessionPenalty = -10


### POPUP ###

def preserveUnion():
	fight(active())


def acceptSecession():
	concede(active())


CIVIL_WAR_POPUP = (
	popup.text("TXT_KEY_CIVIL_WAR_CALL")
		.option(preserveUnion, "TXT_KEY_CIVIL_WAR_FIGHT", button='Art/Interface/Buttons/Actions/Fortify.dds')
		.option(acceptSecession, "TXT_KEY_CIVIL_WAR_CONCEDE", button='Art/Interface/Buttons/Actions/Liberate.dds')
		.build()
)


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def checkCivilWar(iGameTurn):
	if scenarioStart():
		return

	if data.bCivilWarStarted:
		return

	if iGameTurn != year(iCivilWarYear).deviate(iYearVariation, data.iSeed):
		return

	for iCiv, (lRegions, iMinimum) in dCivilWars.items():
		iPlayer = slot(iCiv)

		if iPlayer < 0 or not player(iPlayer).isExisting():
			continue

		# The war is about the institution, so the gate is whether slavery is still legal here -
		# not whether the player runs one particular civic. canUseSlaves() is the mod's own
		# predicate and covers all three routes to it, including the permissive default.
		if not player(iPlayer).canUseSlaves():
			continue

		rebels = cities.owner(iPlayer).regions(*lRegions)

		if rebels.count() < iMinimum:
			continue

		secede(iPlayer, rebels)


def secede(iPlayer, rebels):
	"""The slave states leave. Whether they stay gone is the next question."""
	data.bCivilWarStarted = True
	data.lConfederateCities = [location(city) for city in rebels]

	for city in rebels:
		Secession.secedeCity(city, iConfederacy, False, 0)

	for tCity in data.lConfederateCities:
		createRoleUnits(iConfederacy, tCity, [(iDefend, iRebelDefenders)], iExperience=2, bCreateSettlers=False)

	if plot(data.lConfederateCities[0]).isRevealed(player().getTeam(), False) and not autoplay():
		plot(data.lConfederateCities[0]).cameraLookAt()

	if player(iPlayer).isHuman() and not autoplay():
		ask(iPlayer)
	else:
		# the Union fought. An AI that shrugged would leave the map permanently wrong
		fight(iPlayer)


def ask(iPlayer):
	CIVIL_WAR_POPUP.text(len(data.lConfederateCities)) \
		.preserveUnion().acceptSecession().launch()


### THE TWO ANSWERS ###

def fight(iPlayer):
	"""Preserve the Union by force."""
	if not team(iPlayer).isAtWar(player(iConfederacy).getTeam()):
		team(iPlayer).declareWar(player(iConfederacy).getTeam(), True, WarPlanTypes.WARPLAN_TOTAL)

	capital = player(iPlayer).getCapitalCity()

	if not capital.isNone():
		createRoleUnits(iPlayer, location(capital),
			[(iCityAttack, iUnionReinforcements), (iSiege, max(1, iUnionReinforcements / 2))],
			iExperience=2, bCreateSettlers=False)

	message(iPlayer, 'TXT_KEY_CIVIL_WAR_FIGHTING',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)


def concede(iPlayer):
	"""Let them go. The institution survives, and so does the grievance."""
	data.bCivilWarResolved = True

	if team(iPlayer).isAtWar(player(iConfederacy).getTeam()):
		team(iPlayer).makePeace(player(iConfederacy).getTeam())

	# the same accumulator a suppressed revolution uses: an internal challenge to the state's
	# authority that was not overcome. Stability decays it on the usual schedule
	data.players[iPlayer].iSuppressionPenalty += iSecessionPenalty
	Stability.checkStability(iPlayer)

	message(iPlayer, 'TXT_KEY_CIVIL_WAR_CONCEDED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iRed)


### THE RECONQUEST ###

@handler("cityAcquired")
def checkReconquestOnAcquired(iOwner, iPlayer, city):
	if isUnion(iPlayer):
		checkReconquest(iPlayer)


@handler("BeginGameTurn")
def checkReconquestEachTurn(iGameTurn):
	"""Also checked on a timer, because cityAcquired is not the only way a rebel city can stop
	being rebel-held. Razing, nuking or a collapse would otherwise strand the war unresolved and
	leave slavery in place forever, having been fought over and won."""
	if not data.bCivilWarStarted or data.bCivilWarResolved:
		return

	for iCiv in dCivilWars:
		iPlayer = slot(iCiv)
		if iPlayer >= 0 and player(iPlayer).isExisting():
			checkReconquest(iPlayer)


def checkReconquest(iPlayer):
	"""Victory is no seceded city still in rebel hands - and victory is what abolishes slavery.

	Emancipation followed the war rather than causing it, so it is applied here and nowhere else.
	"""
	if not data.bCivilWarStarted or data.bCivilWarResolved:
		return

	if held(iConfederacy) > 0:
		return

	data.bCivilWarResolved = True

	if team(iPlayer).isAtWar(player(iConfederacy).getTeam()):
		team(iPlayer).makePeace(player(iConfederacy).getTeam())

	abolish(iPlayer)


def held(iOwner):
	"""How many of the seceded cities this player still holds. A razed city counts for nobody."""
	iCount = 0

	for tCity in data.lConfederateCities:
		city = plot(tCity).getPlotCity()

		if city and not city.isNone() and city.getOwner() == iOwner:
			iCount += 1

	return iCount


def isUnion(iPlayer):
	return civ(iPlayer) in dCivilWars


def abolish(iPlayer):
	"""The amendment the war made possible - if the century has caught up enough to write it.

	Only a civic that sets bNoSlavery actually ends slavery, so the choice is made from the list
	above rather than from whatever reads as progressive. If none of them is available yet the
	Union is still restored, but the institution survives its war, which is a real outcome and
	should be reported as one rather than silently faked.
	"""
	for iCivic, iTech in lAbolitionCivics:
		if team(iPlayer).isHasTech(iTech):
			player(iPlayer).setCivics(infos.civic(iCivic).getCivicOptionType(), iCivic)

			message(iPlayer, 'TXT_KEY_CIVIL_WAR_UNION_RESTORED', infos.civic(iCivic).getText(),
				event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
				color=iGreen)
			return

	message(iPlayer, 'TXT_KEY_CIVIL_WAR_UNION_RESTORED_UNRESOLVED',
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		color=iYellow)
