# The migrant: a citizen who leaves one city in order to settle in another.
#
# Civ4 offers neither half of this. iPopCost, which would let a unit cost population to build,
# does not exist in this DLL - no unit declares it and nothing reads it. CvUnit::join, the Great
# Person "join city" action, adds a free specialist rather than a citizen. So both the departure
# and the arrival are done here, from events the mod already receives.
#
# The arrival is settled on a turn boundary rather than the moment the unit walks in, because
# there is no event for a unit entering a city. The alternative was CvGameUtils.cannotTrain and
# friends, and this mod disables all twenty-five Python callbacks in PythonCallbackDefines - a
# deliberate choice with thirty-six civilizations, and not one to overturn for a single unit.

from Core import *
from Events import handler

import Migration


### CONSTANTS ###

# the last citizen cannot leave: emigration never empties a city
iMinimumPopulation = 2


### UNIT BUILT ###

@handler("unitBuilt")
def onMigrantBuilt(city, unit):
	"""Take the citizen out of the city that raised the migrant.

	The size check happens after the fact rather than by hiding the build order, because
	cannotTrain is one of the disabled callbacks. Refusing here costs the player the production,
	which is the point: without it a size-one city could raise migrants indefinitely and every one
	would be a citizen created from nothing.
	"""
	if base_unit(unit) != iMigrant:
		return

	iOwner = city.getOwner()

	if city.getPopulation() < iMinimumPopulation:
		unit.kill(False, PlayerTypes.NO_PLAYER)

		message(iOwner, 'TXT_KEY_MIGRANT_TOO_SMALL', city.getName(),
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iRed, location=city)
		return

	# Migration.shrink rather than changePopulation(-1): the food box is not scaled down with the
	# city, but growthThreshold() is, so a city that simply loses a citizen keeps a box that may
	# already exceed its new threshold and grows straight back. Every migrant would be half free.
	Migration.shrink(city)

	message(iOwner, 'TXT_KEY_MIGRANT_DEPARTED', city.getName(),
		event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
		button=infos.unit(iMigrant).getButton(), color=iYellow, location=city)


### BEGIN PLAYER TURN ###

@handler("BeginPlayerTurn")
def settleMigrants(iGameTurn, iPlayer):
	"""Every migrant that begins the turn in one of its owner's cities settles there.

	The destinations are resolved before anything is killed. Units is a snapshot of unit keys
	rather than of live objects, but settling removes a unit from the plot it is standing on, and
	deciding while mutating is how the terraforming handler took the process down.
	"""
	arrivals = []

	for unit in units.owner(iPlayer).where(lambda u: base_unit(u) == iMigrant):
		destination = city(unit)

		if not destination or destination.isNone():
			continue

		# a migrant cannot settle in someone else's city, however friendly
		if destination.getOwner() != iPlayer:
			continue

		arrivals.append((unit, destination))

	for unit, destination in arrivals:
		settle(unit, destination)


def settle(unit, destination):
	"""The migrant becomes a citizen of the city it is standing in."""
	sName = destination.getName()
	iOwner = destination.getOwner()

	destination.changePopulation(1)
	unit.kill(False, PlayerTypes.NO_PLAYER)

	message(iOwner, 'TXT_KEY_MIGRANT_SETTLED', sName,
		event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT,
		button=infos.unit(iMigrant).getButton(), color=iYellow, location=destination)
