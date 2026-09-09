# The invasion: something arrives that does not care who is winning.
#
# The mod's scripted history stops in 1945. Every mechanism it has - crusades, the plague, the slave
# trade, revolutions, congresses, the world wars - has fired and finished by then, and the game runs
# to 2050. There is not one dated trigger anywhere in the mod after 1950, and FutureRules spends
# that same stretch retiring the constraints the player has lived under all game. The last century
# gets emptier and easier at once.
#
# The deeper problem is that by then nothing can threaten the leader. Civilization IV has no
# machinery for it: AI_getAttitudeVal scores a runaway first place at about one point of attitude,
# and an AI three eras behind cannot fight anyway. GrandAlliance.py addresses that inside the
# advanced-civilization scenario by uniting the world, but a united medieval world is still a
# medieval world.
#
# This is the answer that does not depend on the AI being any good. The invaders are not a
# civilization, they are not diplomatic, and they do not care about score. They scale to the power
# of whoever they land on, so the stronger the leader is, the heavier the wave that arrives - which
# is exactly the property no human opponent in this game can have.
#
# It is finite, and that matters. Eight waves and it is over, win or lose. An endless threat is
# just a tax with better flavour, and this file already has one of those in its history.

from Core import *
from Events import handler


### CONSTANTS ###

# Whether any of this happens. Off restores the mod exactly as it was.
bEnabled = True

# Not before both of these. The era gate is what makes it a late-game event in any scenario; the
# year keeps it out of a Renaissance start that races up the tree.
iInvasionEra = iDigital
iInvasionYear = 1970

# Turns of warning before the first landing, so it is not a surprise that cannot be prepared for.
iWarningTurns = 8

# Turns between landings, and how many landings there are.
iWaveInterval = 6
iWaves = 8

# Invaders per landing: this many at the first wave, growing by this much each time.
iBaseInvaders = 3
iInvadersPerWave = 1

# How many civilizations are landed on at once. The strongest first, always.
iTargets = 3

# What lands. Deliberately the heaviest units in the game rather than anything new: adding a unit
# would mean a new entry in CIV4UnitInfos and a matching one in the Consts tuples, and that
# positional agreement is the single easiest thing in this mod to break.
lInvaders = [iMainBattleTank, iMechanizedInfantry, iGunship]


### THE ARC ###

@handler("BeginGameTurn")
def invasion(iGameTurn):
	"""The whole sequence: watch, warn, land, and eventually stop."""
	if not bEnabled:
		return

	if data.bInvasionEnded:
		return

	if data.iInvasionTurn < 0:
		if imminent():
			begin()
		return

	iSince = since(data.iInvasionTurn)

	if iSince < turns(iWarningTurns):
		return

	if iSince == turns(iWarningTurns):
		truce()

	# the first wave lands the moment the warning ends, and every interval after
	iElapsed = iSince - turns(iWarningTurns)

	if iElapsed % turns(iWaveInterval) != 0:
		return

	if data.iInvasionWave >= iWaves:
		conclude()
		return

	data.iInvasionWave += 1
	land()


def imminent():
	"""Whether the world is late enough for this."""
	if year() < year(iInvasionYear):
		return False

	for iPlayer in players.major().existing():
		if player(iPlayer).getCurrentEra() >= iInvasionEra:
			return True

	return False


def begin():
	data.iInvasionTurn = turn()

	for iPlayer in players.major().existing():
		message(iPlayer, 'TXT_KEY_INVASION_WARNING',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iYellow, force=True)


### THE TRUCE ###

def truce():
	"""Everyone stops fighting each other, once.

	Not generosity - it is the only way the event reads as what it is. A world that carries on its
	own wars through this is a world where nothing arrived. Peace is made rather than offered
	because no AI would accept it: attitudes at this point in a game are the accumulated grudges of
	four thousand years.
	"""
	lPlayers = list(players.major().existing())

	for iPlayer in lPlayers:
		for iOther in lPlayers:
			if iPlayer >= iOther:
				continue

			if team(iPlayer).isAtWar(player(iOther).getTeam()):
				team(iPlayer).makePeace(player(iOther).getTeam())

	for iPlayer in lPlayers:
		message(iPlayer, 'TXT_KEY_INVASION_TRUCE',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iRed, force=True)


### THE LANDINGS ###

def land():
	"""Put down one wave, on the strongest civilizations in the world.

	Strongest rather than nearest or random, and that is the entire point of the mechanic. The
	leader is the one player nothing else in the game can threaten, so the leader is the one this
	lands on hardest - and the wave is sized from that civilization's own power, so outgrowing the
	world does not outgrow this.
	"""
	for iPlayer in strongest():
		site = landingSite(iPlayer)

		if site is None:
			continue

		iNumber = waveSize(iPlayer)

		for iIndex in range(iNumber):
			iUnit = lInvaders[iIndex % len(lInvaders)]
			makeUnits(barbarian(), iUnit, site, 1, UnitAITypes.UNITAI_ATTACK_CITY)

		message(iPlayer, 'TXT_KEY_INVASION_LANDING', iNumber,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iRed,
			location=site, force=True)


def strongest():
	"""The civilizations this wave lands on, most powerful first."""
	lRanked = [(player(iPlayer).getPower(), iPlayer)
			   for iPlayer in players.major().existing()
			   if player(iPlayer).getNumCities() > 0]

	# sorted with a key argument would be neater and arrived in Python 2.5; this is 2.4
	lRanked.sort()
	lRanked.reverse()

	return [iPlayer for _, iPlayer in lRanked[:iTargets]]


def waveSize(iPlayer):
	"""How many land on this civilization.

	Grows with the wave for everyone, and again with how far ahead of the world this particular
	civilization is - so a runaway leader faces a wave nobody else has to.
	"""
	iNumber = iBaseInvaders + iInvadersPerWave * (data.iInvasionWave - 1)

	iAverage = averagePower()

	if iAverage > 0 and player(iPlayer).getPower() > iAverage * 2:
		iNumber = iNumber * 3 / 2

	return max(1, iNumber)


def averagePower():
	lPowers = [player(iPlayer).getPower() for iPlayer in players.major().existing()]

	if not lPowers:
		return 0

	return sum(lPowers) / len(lPowers)


def landingSite(iPlayer):
	"""Somewhere near one of this civilization's cities, but not on one.

	Near a city because an invasion that lands in empty tundra is a rumour rather than an event, and
	not on one because CvPlot cannot hold a unit stack on a city it does not own without the DLL
	resolving it immediately.
	"""
	targets = cities.owner(iPlayer)

	if not targets:
		return None

	target = targets.random()

	sites = plots.ring(target, radius=2).where(
		lambda p: not p.isWater() and not p.isPeak() and not p.isCity() and p.getNumUnits() == 0)

	if not sites:
		return None

	return sites.random()


### THE END ###

def conclude():
	"""It is over. Say so, once, and never run again.

	Finite by construction: after the last wave this fires whether the invaders were destroyed or
	are still standing, because a mechanic that only ends on a condition the player might never
	meet is a mechanic that never ends.
	"""
	data.bInvasionEnded = True

	for iPlayer in players.major().existing():
		message(iPlayer, 'TXT_KEY_INVASION_ENDED',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iGreen, force=True)


def barbarian():
	"""The player the invaders belong to.

	Read from the DLL rather than through slot(iBarbarian), which answers with a NullPlayer when the
	civilization holds no slot - see UnitFactory.owner for how that fails.
	"""
	return gc.getBARBARIAN_PLAYER()
