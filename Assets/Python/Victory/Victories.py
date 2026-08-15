import SimultaneousStart

from Core import *

from StoredData import data
from Events import events, handler
from Scenarios import getScenario
from GoalHandlers import event_handler_registry

from Types import *


### GLOBALS ###

# Empty rather than None so that reading one before it is populated degrades to "no goals"
# instead of raising. The civilization selection screen asks for victory descriptions before
# fontsLoaded fires, and "iCiv not in None" raises TypeError: iterable argument required.
dHistoricalGoals = {}
dReligiousGoals = {}
dAdditionalPaganGoal = {}


### EVENT HANDLERS ###

def ensureLoaded():
	"""Build the goal tables if they have not been built yet.

	Callers should use this rather than reading the globals directly. loadVictories runs on
	fontsLoaded, but the civilization selection screen is drawn before that, so the data has to
	be available on demand whenever the first reader appears.

	Idempotent: the tables are module-level dicts in HistoricalVictory and ReligiousVictory, so
	rebinding to the same objects costs nothing and repeated calls are free.

	The imports stay inside the function deliberately. HistoricalVictory builds its tables at
	module scope using plots.core(), which needs civilization infos - importing it at module
	scope is what took the whole mod down previously.
	"""
	global dHistoricalGoals
	global dReligiousGoals
	global dAdditionalPaganGoal

	if dHistoricalGoals:
		return

	import HistoricalVictory as Historical
	import ReligiousVictory as Religious

	# If either module raised while building its tables, Civ4's loader leaves the half-built module
	# cached in sys.modules, and every later import hands back that shell. Reading dGoals off it
	# then raises "AttributeError: 'module' object has no attribute 'dGoals'", which reports the
	# consequence and hides the original failure - and it repeats on every call.
	#
	# Leave the tables empty instead. The real exception was already raised and logged where it
	# happened; the game keeps running with no goals rather than failing again here.
	if not hasattr(Historical, "dGoals") or not hasattr(Religious, "dGoals"):
		return

	dHistoricalGoals = Historical.dGoals
	dReligiousGoals = Religious.dGoals
	dAdditionalPaganGoal = Religious.dAdditionalPaganGoal


@handler("fontsLoaded")
def loadVictories():
	ensureLoaded()

	#printVictories(dHistoricalGoals, dReligiousGoals, dAdditionalPaganGoal)


def printVictories(dHistoricalGoals, dReligiousGoals, dAdditionalPaganGoal):
	from Files import getPath
	
	lines = []
	
	for iCiv in range(iNumCivs):
		lines.append(infos.civ(iCiv).getDescription())
		
		for goal in dHistoricalGoals.get(iCiv, []):
			lines.append("%s: %s" %  (text(goal.options["title_key"]), goal.description()))
	
	for iReligion in dReligiousGoals:
		if iReligion < iNumReligions:
			lines.append(infos.religion(iReligion).getDescription())
		else:
			lines.append(str(iReligion))
		
		for goal in dReligiousGoals[iReligion]:
			lines.append("%s: %s" % (text(goal.options.get("title_key", "")), goal.description()))
	
	for iPaganReligion, goal in dAdditionalPaganGoal.items():
		lines.append(str(goal.description()))
	
	file = open(getPath("UHV Descriptions.txt"), "w")
	
	try:
		file.write("\n".join([line.encode("latin-1", "xmlcharrefreplace") for line in lines]))
	finally:
		file.close()


@handler("playerCivAssigned")
def assignGoals(iPlayer):
	# historical goals carry dates, and a simultaneous start has rewritten every one of them. China
	# founded in the Renaissance cannot be asked for anything by 1000 BC, and a goal that cannot be
	# attempted is worse than no goal: it fails on schedule and reports the failure.
	if SimultaneousStart.enabled():
		return

	if player(iPlayer).isHuman():
		data.players[iPlayer].historicalVictory = HistoricalVictory.create(iPlayer)
		data.players[iPlayer].religiousVictory = ReligiousVictory.create(iPlayer)


@handler("switch")
def onSwitch(iPrevious, iCurrent):
	# Same absence as switchReligiousGoals below: under a simultaneous start no goals were ever
	# created, so there is nothing to disable and nothing to build in their place. Switching
	# civilization is still offered in that game, so this is reachable rather than theoretical.
	if data.players[iPrevious].historicalVictory:
		data.players[iPrevious].historicalVictory.disable()

	if data.players[iPrevious].religiousVictory:
		data.players[iPrevious].religiousVictory.disable()

	data.players[iPrevious].historicalVictory = None
	data.players[iPrevious].religiousVictory = None

	if SimultaneousStart.enabled():
		return

	data.players[iCurrent].historicalVictory = HistoricalVictory.create(iCurrent)
	data.players[iCurrent].religiousVictory = ReligiousVictory.create(iCurrent)
	

@handler("civicChanged")
def onCivicChanged(iPlayer, iOldCivic, iNewCivic):
	if iPlayer == active() and infos.civic(iOldCivic).isStateReligion() != infos.civic(iNewCivic).isStateReligion():
		switchReligiousGoals(iPlayer)


@handler("playerChangeStateReligion")
def onStateReligionChanged(iPlayer):
	if iPlayer == active():
		switchReligiousGoals(iPlayer)


@handler("victory")
def onVictory(iPlayer):
	if iPlayer == active():
		CyInterface().DoSoundtrack("AS2D_VICTORY")
	else:
		CyInterface().DoSoundtrack("AS2D_DEFEAT")


	
### UTILITY FUNCTIONS ###

def switchReligiousGoals(iPlayer):
	# A simultaneous start has no goals to switch. assignGoals returns before creating any, because
	# a historical goal carrying a date cannot be asked of a civilization whose date was rewritten,
	# so religiousVictory is still None - and both handlers that call this fire on the very first
	# turn, as thirty-one civilizations take their civics and their state religions at once.
	#
	# StoredData.onLoad already tests these the same way before enabling them; these two callers
	# were simply the ones that did not.
	if not data.players[iPlayer].religiousVictory:
		return

	data.players[iPlayer].religiousVictory.disable()
	data.players[iPlayer].religiousVictory = ReligiousVictory.create(iPlayer)


### CLASSES ###

class Victory(object):

	def __init__(self, iPlayer, descriptions):
		self.iPlayer = iPlayer
		self.goals = tuple(self.create_goal(description) for description in descriptions)
		
		self.bGoldenAge = False
		self.bVictory = False
		
		self.enable()
		
	def enable(self):
		for goal in self.goals:
			goal.succeed = goal.override(self.goal_succeed())
			goal.fail = goal.override(self.goal_fail())
			
			goal.enable()
		
		events.addEventHandler("BeginGameTurn", self.check_complete)
	
	def disable(self):
		for goal in self.goals:
			goal.disable()
		
		events.removeEventHandler("BeginGameTurn", self.check_complete)

	def goal_succeed(self):
		def succeed(goal):
			goal.set_state(SUCCESS)
		
			if goal.succeeded():
				if goal.mode == STATEFUL:
					goal.announce_success()
			
				self.check()
		
		return succeed

	def goal_fail(self):
		def fail(goal):
			goal.set_state(FAILURE)
	
			if goal.state == FAILURE:
				goal.announce_failure()
		
		return fail

	def succeeded_goals(self):
		return count(goal.succeeded() for goal in self.goals)
	
	def num_goals(self):
		return len(self.goals)
	
	def area_names(self, tile):
		return [goal.area_name(tile) for goal in self.goals]
	
	def check(self):
		pass
	
	def check_complete(self, iGameTurn):
		if self.bGoldenAge:
			self.bGoldenAge = False
			self.golden_age()
		
		if self.bVictory:
			self.bVictory = False
			self.victory()
	
	def create_goal(self, description):
		return description(self.iPlayer)
	
	def victory(self):
		if game.getWinner() == -1:
			game.setWinner(self.iPlayer, self.VICTORY_TYPE)
	
	def golden_age(self):
		iGoldenAgeTurns = player(self.iPlayer).getGoldenAgeLength()
		player(self.iPlayer).changeGoldenAgeTurns(iGoldenAgeTurns)
		
		message(self.iPlayer, "TXT_KEY_VICTORY_INTERMEDIATE", color=iPurple)


class HistoricalVictory(Victory):

	VICTORY_TYPE = VictoryTypes.VICTORY_HISTORICAL

	@classmethod
	def create(cls, iPlayer):
		ensureLoaded()

		iCiv = civ(iPlayer)

		# a scenario may carry its own goals; every other scenario keeps the historical set.
		# Written long-hand: Civ4 embeds Python 2.4, which has no conditional expression.
		scenario_goals = getScenario().dGoals
		if scenario_goals is None:
			scenario_goals = dHistoricalGoals
		descriptions = scenario_goals.get(iCiv, [])
		
		victory = cls(iPlayer, descriptions)
		
		getScenario().initGoals(iPlayer, victory.goals)
		
		return victory
	
	def enable(self):
		Victory.enable(self)

	def check(self):
		iSucceededGoals = self.succeeded_goals()
		iNumGoals = self.num_goals()
		
		if iSucceededGoals == iNumGoals - 1:
			self.bGoldenAge = True
		elif iSucceededGoals == iNumGoals:
			self.bVictory = True
	

class ReligiousVictory(Victory):

	VICTORY_TYPE = VictoryTypes.VICTORY_RELIGIOUS

	@classmethod
	def create(cls, iPlayer):
		ensureLoaded()

		iStateReligion = player(iPlayer).getStateReligion()
		
		if iStateReligion >= 0:
			return cls(iPlayer, dReligiousGoals[iStateReligion])
		elif player(iPlayer).isStateReligion():
			iCivilization = player(iPlayer).getCivilizationType()
			iPaganReligion = infos.civ(iCivilization).getPaganReligion()
			return cls(iPlayer, concat(dReligiousGoals[iPaganVictory], dAdditionalPaganGoal[iPaganReligion]))
		else:
			return cls(iPlayer, dReligiousGoals[iSecularVictory])

	def check(self):
		if self.succeeded_goals() == self.num_goals():
			self.bVictory = True
	
	def create_goal(self, description):
		return description(self.iPlayer, mode=STATELESS)