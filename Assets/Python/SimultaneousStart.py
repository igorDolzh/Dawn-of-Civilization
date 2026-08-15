# Simultaneous start: every civilization on the list appears together, at the same technology.
#
# This is the opposite of what the mod is. Dawn of Civilization is built on staggered births -
# stability is measured against a birth turn, historical goals carry dates, and the roster only
# fits at all because a dead civilization's player slot is handed to a later one. Turning that off
# does not produce a variant of the mod; it produces a large Civilization IV map of the Earth.
#
# It is therefore an option, off by default, and the historical goals go with it: a China founded
# in the Renaissance cannot be asked to do anything by 1000 BC.
#
# The list is thirty-one because the DLL has thirty-six player slots (MAX_CIV_PLAYERS) and five
# are spoken for by the independents, the natives, the minors and the barbarians. Sixty-eight
# civilizations would otherwise want to exist. Nothing here can raise that ceiling.

from Core import *
from Events import handler


### THE OPTION ###

# Custom map option slot, declared in PrivateMaps/Dawn_of_Civilization.py. Slot 0 is the scenario
# and slot 1 the disasters, so this is slot 2; the two must agree.
iSimultaneousOption = 2
iSimultaneousOn = 1


def enabled():
	"""Whether this game starts everyone together.

	Fails to False rather than True, the reverse of Disasters.enabled. There the safe answer was
	the mod's existing behaviour; here the mod's existing behaviour is off, and a game that
	silently rewrote every birth date because an option could not be read would be far worse than
	one that quietly played normally.
	"""
	try:
		if map.getNumCustomMapOptions() <= iSimultaneousOption:
			return False

		return map.getCustomMapOption(iSimultaneousOption) == iSimultaneousOn
	except:
		return False


### THE ADVANCED CIVILIZATION ###

# Slot 3, declared alongside the others in PrivateMaps/Dawn_of_Civilization.py. Off, the human, or
# one artificial player drawn at random; the indices are the contract with that file.
iAdvancedOption = 3
iAdvancedOff = 0
iAdvancedHuman = 1
iAdvancedAI = 2


def advancedSetting():
	"""Which of the three the player chose, defaulting to off if it cannot be read."""
	try:
		if map.getNumCustomMapOptions() <= iAdvancedOption:
			return iAdvancedOff

		return map.getCustomMapOption(iAdvancedOption)
	except:
		return iAdvancedOff


def advancedEnabled():
	"""Whether one civilization is out of its time. Requires the simultaneous start itself.

	On its own the setting would mean little: without a simultaneous start the civilizations
	arrive centuries apart already, and being three eras ahead of a neighbour who has not been
	born yet is not a scenario.
	"""
	return enabled() and advancedSetting() != iAdvancedOff


def advancedPlayer():
	"""Which player is the advanced one, or -1.

	Chosen once and remembered, because it must not be reconsidered every time a civilization is
	born: the draw uses the synchronised generator, and asking it again would both give different
	answers and desynchronise a multiplayer game.
	"""
	if data.iAdvancedPlayer != -1:
		return data.iAdvancedPlayer

	if advancedSetting() == iAdvancedHuman:
		data.iAdvancedPlayer = active()
		return data.iAdvancedPlayer

	candidates = [iPlayer for iPlayer in players.major().alive() if not player(iPlayer).isHuman()]

	if not candidates:
		return -1

	data.iAdvancedPlayer = candidates[rand(len(candidates))]
	return data.iAdvancedPlayer


### THE ROSTER ###

# Chosen as nations that still exist rather than by birth date, which is why France, China, Japan
# and Korea are here despite ancient starts, and why the Aztecs, the Mongols and the Tatars are
# not. Canada, Belgium and Zulu were the three cut to reach thirty-one: Canada sits on top of
# America with nothing between them at turn one, the Netherlands already holds the Low Countries,
# and South Africa is one of the twenty civilizations the array limit keeps out, which would have
# left the Zulu alone at the bottom of the continent.
lSimultaneousCivs = [
	# Europe
	iFrance, iSpain, iPortugal, iEngland, iGermany, iItaly, iNetherlands, iPoland, iSweden,
	iRussia, iOttomans,

	# Asia
	iChina, iJapan, iKorea, iVietnam, iThailand, iBurma, iJava, iMughals, iIran,

	# Africa and the Middle East
	iMisr, iMoors, iEthiopia, iCongo, iSaudis,

	# The Americas and Oceania
	iAmerica, iMexico, iBrazil, iArgentina, iColombia, iAustralia,
]


### THE TECHNOLOGY ###

# Everyone starts at the end of the Renaissance: the earliest point at which a simultaneous world
# start makes sense, because it is the first era in which every civilization can reach every other.
# Earlier and the Americas and Australia are alone on their maps until someone invents a ship.
iStartingEra = iRenaissance


# The one civilization out of its time, when the advanced option is on. Everyone else drops to
# medieval, so the gap is three eras: machine guns and artillery against knights.
#
# Global rather than anything later because it is the widest gap in which the medieval world still
# has an answer - mass, distance, terrain and attrition. Beyond it there is no game, only a
# demonstration.
iBackwardEra = iMedieval
iAdvancedEra = iGlobal


def techsUpTo(iEra):
	"""Every technology up to and including an era.

	Read from the era each technology declares rather than listed by hand, so it stays correct if
	techs are added or moved between eras - which has happened to this tree before.
	"""
	return [iTech for iTech in infos.techs() if infos.tech(iTech).getEra() <= iEra]


def startingEra(iPlayer):
	"""Which era this civilization begins in."""
	if not advancedEnabled():
		return iStartingEra

	if iPlayer == advancedPlayer():
		return iAdvancedEra

	return iBackwardEra


@handler("prepareBirth")
def grantStartingTechs(iCiv):
	"""Bring a civilization up to its starting technology, before it is given anything else.

	prepareBirth rather than birth, and the difference is the whole point. Birth fires at the end
	of Birth.birth(), by which time assignAttributes and createUnits have already run - and
	createUnits asks getUnitForRole for the strongest unit the civilization can presently train.
	Granting the technology afterwards produces a renaissance empire defended by archers.

	prepare() runs at Rise.py:797, after activate() has taken a player slot and before birth() at
	:812 touches anything. Nothing here is undone later: civ.apply adds its own technologies and
	setHasTech only ever adds.
	"""
	if not enabled():
		return

	iPlayer = slot(iCiv)

	if iPlayer < 0:
		return

	tPlayer = team(iPlayer)

	for iTech in techsUpTo(startingEra(iPlayer)):
		if not tPlayer.isHasTech(iTech):
			tPlayer.setHasTech(iTech, True, iPlayer, False, False)

	player(iPlayer).setStartingEra(player(iPlayer).getCurrentEra())
