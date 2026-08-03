from BugEventManager import g_eventManager as events
import inspect
import sys
import traceback

from Core import *

from GoalHandlers import event_handler_registry


victory_handlers = appenddict()

logged_events = []

# BugEventManager wraps every handler call in a bare `except:` and reports the failure with
# BugUtil.trace, which writes to the on-screen message area and nowhere else - no traceback, no
# file. A handler that raises on every turn therefore leaves no evidence beyond one line that
# scrolls away, which is how a NameError in Rules.moveSlavesToNewWorld survived unnoticed.
#
# fileLog is the engine's own writer (CvPythonExtensions) and goes straight to
# Logs\<name>, so it does not depend on the BUG log level options being set.
ERROR_LOG = "Errors.log"


def logHandlerError(event, func):
	"""Write the current exception, with its traceback, to Logs\\Errors.log.

	Re-raising afterwards leaves BugEventManager's own behaviour untouched: it still catches the
	exception and shows its one-line notice, so nothing that worked before changes. This only
	adds the record that was missing.

	Deliberately defensive - a failure while reporting a failure must not replace the original
	exception with a less useful one.
	"""
	try:
		fileLog(ERROR_LOG, "%s in %s.%s handling '%s'\n%s\n" % (
			sys.exc_info()[0].__name__,
			getattr(func, "__module__", "?"),
			getattr(func, "__name__", "?"),
			event,
			traceback.format_exc()))
	except:
		pass


def handler(event):
	def handler_decorator(func):
		arg_names = inspect.getargspec(func)[0]
		
		if event in logged_events:
			func = log(func)
		
		def handler_func(args):
			try:
				return func(*args[:len(arg_names)])
			except:
				logHandlerError(event, func)
				raise
			
		handler_func.__name__ = func.__name__
		handler_func.__module__ = func.__module__
		handler_func.func_name = func.func_name
				
		events.addEventHandler(event, handler_func)
		return handler_func
		
	return handler_decorator
	
	
def noop(*args, **kwargs):
	pass


def popup_handler(event_id):
	def handler_decorator(func):
		events.addCustomEvent(event_id, func.__name__, func, noop)
		return func
		
	return handler_decorator


def register_victory_handler(event, handler):
	victory_handlers[event].append(handler)
	events.addEventHandler(event, handler)
	

def reset_victory_handlers():
	global victory_handlers
	for event, handlers in victory_handlers.items():
		for handler in handlers:
			if events.hasEventHandler(event, handler):
				events.removeEventHandler(event, handler)
	
	victory_handlers = appenddict()


events.addEvent("firstCity")
events.addEvent("capitalMoved")
events.addEvent("wonderBuilt")
events.addEvent("immigration")
events.addEvent("collapse")
events.addEvent("crusade")
events.addEvent("periodChange")
events.addEvent("playerPeriodChange")
events.addEvent("birth")
events.addEvent("resurrection")
events.addEvent("enslave")
events.addEvent("combatGold")
events.addEvent("combatFood")
events.addEvent("sacrificeGoldenAge")
events.addEvent("prepareBirth")
events.addEvent("flip")
events.addEvent("conquerors")
events.addEvent("tribute")
events.addEvent("playerCityRenamed")
events.addEvent("buildingProcessed")
events.addEvent("citySacked")
events.addEvent("unitCaptured")
events.addEvent("goldGranted")


@handler("buildingBuilt")
def capitalMovedOnPalaceBuilt(city, iBuilding):
	if iBuilding == iPalace:
		events.fireEvent("capitalMoved", city)


@handler("firstCity")
def capitalMovedOnFirstCity(city):
	events.fireEvent("capitalMoved", city)


@handler("cityAcquired")
def capitalMovedOnCityAcquired(iOwner, iNewOwner, city):
	capital_city = capital(iOwner)
	if capital_city and not at(capital_city, city):
		events.fireEvent("capitalMoved", capital_city)


@handler("cityAcquiredAndKept")
def firstCityOnCityAcquiredAndKept(iPlayer, city):
	if city.isCapital():
		events.fireEvent("firstCity", city)


@handler("cityBuilt")
def firstCityOnCityBuilt(city):
	if city.isCapital():
		events.fireEvent("firstCity", city)


@handler("buildingBuilt")
def wonderBuiltOnBuildingBuilt(city, iBuilding):
	if isWorldWonderClass(infos.building(iBuilding).getBuildingClassType()):
		events.fireEvent("wonderBuilt", city, iBuilding)
		

@handler("PythonReloaded")
def resetHandlersOnPythonReloaded():
	event_handler_registry.reset()


@handler("OnLoad")
def resetHandlersOnLoad():
	event_handler_registry.reset()


@handler("BeginGameTurn")
def evictSaveData():
	data.units.evict()