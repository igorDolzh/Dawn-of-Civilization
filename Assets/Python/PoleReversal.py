# The reversal: the day the climate stops being a constant.
#
# Every other mechanic in this mod happens to civilizations. This one happens to the map. The
# terrain a player has farmed for four thousand years is the one thing the game has never taken
# away, and taking it away is a different kind of disaster from a plague or a war - there is no
# diplomacy that answers it and no army that helps.
#
# What actually happens is a climate catastrophe rather than continents sliding, because plate
# tectonics on a Civilization IV map means moving cities, and a mechanic that deletes a capital
# without warning is not a disaster, it is a reason to reload. Instead the cold band descends: the
# temperate latitudes, which is where almost every city on the map is, turn to tundra and snow.
# The caps thaw at the same time, which opens ground nobody wanted and does not remotely compensate.
# And the sea rises.
#
# CvPlot::getLatitude returns an absolute value, so the two hemispheres cannot be told apart and
# there is no version of this where one pole freezes and the other melts. Bands moving equatorward
# is the reading that fits both the fiction and the API, and it is the more destructive one anyway,
# since it lands on settled land rather than on ice.
#
# The one thing it will not do is drown a city. erase() inside setPlotType calls pCity->kill(), and
# Terraforming.py refuses the same thing for the same reason: it is unrecoverable, unannounced, and
# no fun at all.

from Core import *
from Events import handler

import Disasters


### CONSTANTS ###

# Whether this can happen. Off restores the mod exactly as it was.
bEnabled = True

# Also gated on the Natural Disasters map option, so a player who turned those off does not get
# the largest one of all anyway.

# Not before both of these.
iReversalEra = iGlobal
iReversalYear = 1950

# Chance per turn, in percent, once it is possible. Low, so the date is never known in advance -
# which is most of what makes it frightening rather than merely scheduled.
iReversalChance = 2

# Turns between the first instruments failing and the climate following.
iWarningTurns = 6


# The cold band descends onto the temperate latitudes. This is the destructive half: it is where
# the cities are.
iFreezeMinLatitude = 40
iFreezeMaxLatitude = 72
iFreezeChance = 45

# and the caps thaw, which opens ground at the top of the world that nobody has ever wanted
iThawLatitude = 72
iThawChance = 60

# The sea rises. Deliberately small: at eight percent of coastal land it redraws every coastline on
# the map without erasing anyone's empire.
iFloodChance = 8

# what the cold turns things into, and what the thaw turns them back into
dFreeze = {
	iGrass: iTundra, iPlains: iTundra, iSteppe: iTundra,
	iMarsh: iTundra, iSemidesert: iTundra, iDesert: iTundra,
	iTaiga: iTundra, iTundra: iSnow,
}

dThaw = {
	iSnow: iTundra, iTundra: iTaiga,
}

# growth that does not survive the change
lCleared = [iForest, iJungle, iRainforest]


### THE ARC ###

@handler("BeginGameTurn")
def reversal(iGameTurn):
	if not bEnabled:
		return

	if data.bReversalDone:
		return

	if data.iReversalTurn < 0:
		if possible() and rand(100) < iReversalChance:
			warn()
		return

	if since(data.iReversalTurn) < turns(iWarningTurns):
		return

	execute()


def possible():
	if not Disasters.enabled():
		return False

	if year() < year(iReversalYear):
		return False

	for iPlayer in players.major().existing():
		if player(iPlayer).getCurrentEra() >= iReversalEra:
			return True

	return False


def warn():
	data.iReversalTurn = turn()

	for iPlayer in players.major().existing():
		message(iPlayer, 'TXT_KEY_REVERSAL_WARNING',
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iYellow, force=True)


### THE CHANGE ###

def execute():
	"""Redraw the climate, once.

	Every plot is decided independently against a percentage rather than by a rule that sweeps whole
	bands, so the result is patchy the way weather is, and two games do not produce the same map.
	"""
	data.bReversalDone = True

	iFrozen, iThawed, iFlooded = 0, 0, 0

	for plot in plots.all().land():
		if plot.isPeak():
			continue

		iLatitude = plot.getLatitude()

		if iLatitude >= iThawLatitude:
			if thaw(plot):
				iThawed += 1
		elif iLatitude >= iFreezeMinLatitude and iLatitude < iFreezeMaxLatitude:
			if freeze(plot):
				iFrozen += 1

	iFlooded = drown()

	# One rebuild, after every plot type has settled. setPlotType would otherwise reach
	# recalculateAreas itself, from inside its own conversion, holding CvArea pointers that the
	# rebuild has just destroyed - see Terraforming.convert for the whole of that story.
	if iFlooded > 0:
		map.recalculateAreas()

	announce(iFrozen, iThawed, iFlooded)


def freeze(plot):
	"""The cold arrives here."""
	if rand(100) >= iFreezeChance:
		return False

	iTerrain = plot.getTerrainType()

	if iTerrain not in dFreeze:
		return False

	plot.setTerrainType(dFreeze[iTerrain], True, True)

	if plot.getFeatureType() in lCleared:
		plot.setFeatureType(-1, 0)

	return True


def thaw(plot):
	"""The cap retreats from here."""
	if rand(100) >= iThawChance:
		return False

	iTerrain = plot.getTerrainType()

	if iTerrain not in dThaw:
		return False

	plot.setTerrainType(dThaw[iTerrain], True, True)
	return True


def drown():
	"""The sea takes the low coast.

	Collected before anything is converted rather than converted while iterating: setPlotType
	changes what its neighbours are, and a plot's eligibility is decided by its neighbours.
	"""
	sinking = [plot for plot in plots.all().land()
			   if plot.isCoastalLand() and not plot.isPeak() and not city(plot)
			   and rand(100) < iFloodChance]

	for plot in sinking:
		# false, so the DLL does not rebuild the areas here; execute() does it once at the end
		plot.setPlotType(PlotTypes.PLOT_OCEAN, False, True)

	return len(sinking)


def announce(iFrozen, iThawed, iFlooded):
	for iPlayer in players.major().existing():
		message(iPlayer, 'TXT_KEY_REVERSAL_HAPPENED', iFrozen, iFlooded,
			event=InterfaceMessageTypes.MESSAGE_TYPE_MAJOR_EVENT, color=iRed, force=True)
