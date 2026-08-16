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

# Turns between attempts to arrange pacts.
#
# Not every turn, and this is not a performance nicety. CvTeam::signDefensivePact does nothing at
# all unless canTradeItem succeeds on both sides, and reports nothing when it does not - so a pact
# that cannot be signed this turn is silently retried forever, and every retry costs two
# canTradeItem calls. Across thirty civilizations that was hundreds of failed negotiations a turn,
# for the rest of the game.
iPactInterval = 10

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

	# Once the world has declared there is nothing left to prepare for, and every turn spent
	# arranging pacts after that is spent for nothing.
	if data.bAllianceDeclared:
		return

	if turn() % turns(iPactInterval) == 0:
		sign(lAllies)

	if data.iAllianceConquests >= iWarThreshold:
		declare(lAllies, iAdvanced)


def sign(lAllies):
	"""Pair the world off, one partner each.

	Deliberately not a web. Thirty civilizations each pacted to all the others is four hundred and
	thirty five agreements, and CvTeam::declareWar walks every defensive pact of every team it
	declares on and declares again through each of them - recursively, at CvTeam.cpp:1566. A joint
	declaration across a full mesh is therefore a cascade of hundreds of recursive declarations,
	each one recalculating war plans and attitudes for everybody. That is not slow, it is a game
	that never finishes the turn.

	One partner each keeps the diplomacy visible on the screen, which is the point of it, while
	leaving the cascade linear in the number of civilizations rather than quadratic.
	"""
	unpaired = [iPlayer for iPlayer in lAllies
				if team(iPlayer).isDefensivePactTrading() and not pacted(iPlayer, lAllies)]

	while len(unpaired) >= 2:
		iPlayer = unpaired.pop(0)
		iPartner = partner(iPlayer, unpaired)

		if iPartner is None:
			continue

		unpaired.remove(iPartner)
		team(iPlayer).signDefensivePact(player(iPartner).getTeam())


def pacted(iPlayer, lAllies):
	"""Whether this civilization already has a partner among the others."""
	for iOther in lAllies:
		if iOther != iPlayer and team(iPlayer).isDefensivePact(player(iOther).getTeam()):
			return True

	return False


def partner(iPlayer, candidates):
	"""The first civilization this one could actually sign with, or None.

	A pact between strangers is meaningless and one between belligerents is impossible, and neither
	side can trade the agreement at all without the technology for it - which is checked here rather
	than discovered by a call that fails in silence.
	"""
	for iOther in candidates:
		tOther = player(iOther).getTeam()

		if not team(iPlayer).isHasMet(tOther):
			continue

		if team(iPlayer).isAtWar(tOther):
			continue

		if team(iPlayer).isDefensivePact(tOther):
			continue

		if not team(iOther).isDefensivePactTrading():
			continue

		return iOther

	return None


### REPAIR ###

@handler("OnLoad")
def prunePacts():
	"""Cut an existing defensive pact web back to one partner each.

	Changing how pacts are made does nothing for a game that already made them. Pacts are deals,
	deals live in the DLL's list and are serialised with the save, so a game begun under the mesh
	version carries all four hundred and thirty five of them for the rest of its life - and
	CvTeam::declareWar still recurses through every one at the moment the world declares.

	Neither setDefensivePact nor cancelDefensivePacts is exposed to Python. CyDeal.kill is, and a
	defensive pact is a deal like any other, so this is the only way to reach them.

	Pruned rather than cleared: the first agreement each civilization made stands, and only the
	surplus is cut. The diplomacy was the point of the mechanic.
	"""
	if not SimultaneousStart.advancedEnabled():
		return

	# collected first and killed afterwards, because killing a deal while walking the list is how
	# you end up reading one that has already been freed
	lPacts = []

	for iDeal in range(game.getIndexAfterLastDeal()):
		deal = game.getDeal(iDeal)

		if not deal or deal.isNone():
			continue

		if isPactDeal(deal):
			lPacts.append((deal.getID(), deal.getFirstPlayer(), deal.getSecondPlayer()))

	paired = set()
	iKilled = 0

	for iID, iFirst, iSecond in lPacts:
		if iFirst not in paired and iSecond not in paired:
			paired.add(iFirst)
			paired.add(iSecond)
			continue

		deal = game.getDeal(iID)

		if deal and not deal.isNone():
			deal.kill()
			iKilled += 1

	if iKilled > 0:
		message(active(), latin1(u"Grand Alliance: %d surplus defensive pacts dissolved." % iKilled),
			color=iYellow, force=True)


def isPactDeal(deal):
	"""Whether this deal is a defensive pact, from either side of it."""
	for iTrade in range(deal.getLengthFirstTrades()):
		if deal.getFirstTrade(iTrade).ItemType == TradeableItems.TRADE_DEFENSIVE_PACT:
			return True

	for iTrade in range(deal.getLengthSecondTrades()):
		if deal.getSecondTrade(iTrade).ItemType == TradeableItems.TRADE_DEFENSIVE_PACT:
			return True

	return False


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
