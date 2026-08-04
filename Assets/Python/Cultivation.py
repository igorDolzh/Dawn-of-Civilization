# Cultivation and restocking: spreading a crop, a herd or a shoal you already keep onto ground
# or water that will take it.
#
# Not the invention of a resource, the spread of one. You may only sow what you already have
# connected, so this is the same diffusion the mod already models when a civilization group meets
# another (Resources.spreadCivGroupResources) - the potato reaching Europe rather than Europe
# discovering the potato. Without that rule a bronze age European could conjure maize.
#
# One build per element rather than one per resource. Civ4 builds are fixed actions, so a
# "plant corn", "plant wheat" and so on would put a row of mostly greyed-out buttons on the
# worker; instead the ground and the empire's own resources decide between them, which also
# makes the rule visible rather than hiding it behind disabled options. Cultivate is the
# worker's, on grass and plains; Restock is the work boat's, on coast and ocean.
#
# Deferred to BeginGameTurn for the reason Terraforming is: improvementBuilt fires from inside
# CvPlot::setImprovementType, and clearing the marker from there re-enters the function that is
# still running.

from Core import *
from Events import handler

import Resources


### CONSTANTS ###

# What can be cultivated, in the order it is preferred. These are exactly the members of
# BONUSCLASS_GRAIN and BONUSCLASS_LIVESTOCK - the mod already separates what grows from what is
# dug up, so there is no hand-written judgement here about what counts as farmable.
#
# Grain before livestock, and within each the more productive first: the tile is the point, and a
# grass tile carrying corn is worth more than the same tile carrying sheep.
lCultivable = [iCorn, iRice, iWheat, iPotato, iCow, iSheep, iPig]

# What can be restocked. There is no bonus class for the sea, so unlike the land list this one is
# a judgement: the marine resources that reproduce, and can therefore be seeded and left to breed.
# Pearls belong here - pearl culture is a real and old industry - and amber does not, being fossil
# resin that washes ashore rather than anything that can be stocked.
lStockable = [iFish, iClam, iCrab, iWhales, iPearls]

# which improvement draws on which list
dWorks = {
	iCultivation: lCultivable,
	iRestocking: lStockable,
}


### BEGIN IMPROVEMENT BUILT ###

@handler("improvementBuilt")
def onCultivation(iImprovement, x, y):
	"""Record the works; what grew is decided next turn.

	Nothing may touch the plot here. This fires from inside CvPlot::setImprovementType
	(CvPlot.cpp:6389) and clearing the marker would re-enter it on the plot it is halfway through
	updating - the defect that made reclamation take the whole process down.
	"""
	if iImprovement in dWorks:
		data.lCultivationQueue.append((x, y, iImprovement))


@handler("BeginGameTurn")
def processCultivation(iGameTurn):
	"""Decide what grew on each cultivated or restocked tile."""
	queue = data.lCultivationQueue
	data.lCultivationQueue = []

	for x, y, iImprovement in queue:
		target = plot(x, y)

		# the marker can be gone by now: pillaged, or the tile captured and rebuilt
		if target.getImprovementType() != iImprovement:
			continue

		cultivate(target, dWorks[iImprovement])


def cultivate(target, lChoices):
	"""Put a resource on the plot, if the owner keeps one that will live there."""
	iOwner = target.getOwner()
	x, y = location(target)

	# the works are over either way, so the marker goes before anything else can fail
	target.setImprovementType(-1)

	if iOwner < 0:
		return

	iBonus = choose(target, iOwner, lChoices)

	if iBonus < 0:
		message(iOwner, 'TXT_KEY_CULTIVATION_BARREN',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MINOR_EVENT,
			color=iRed, location=target)
		return

	# Resources.createResource rather than setBonusType: it keeps the bonus variety art, repairs
	# an improvement the new resource invalidates, and notifies the owner the same way every other
	# resource appearing on the map does
	Resources.createResource(x, y, iBonus, createTextKey='TXT_KEY_CULTIVATION_GREW')


def choose(target, iOwner, lChoices):
	"""The best thing the owner already keeps that this ground or water will support, or -1.

	canHaveBonus is the DLL's own test and covers everything that matters: a bonus already on the
	plot, peaks, hills, the terrain and feature the bonus needs, and latitude. Reimplementing any
	of that in Python would only be a second opinion that could disagree with the first.

	getNumAvailableBonuses counts what the empire has connected, so an unworked copy in a city
	that is cut off does not qualify - you can spread what you actually have to hand.
	"""
	for iBonus in lChoices:
		if player(iOwner).getNumAvailableBonuses(iBonus) <= 0:
			continue

		if not target.canHaveBonus(iBonus, False):
			continue

		return iBonus

	return -1
