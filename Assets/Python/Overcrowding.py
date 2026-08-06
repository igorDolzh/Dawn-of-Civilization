# Overcrowding: restoring the vanilla rule that a citizen is worth one unhappy face.
#
# CvCity::getOvercrowdingPercentAnger works from
#
#     iOvercrowding = iPopulation + max(0, iPopulation - 10)
#
# at CvCity.cpp:5490, so every citizen past the tenth angers twice over. A city of sixteen carries
# twenty-two unhappy faces. Beyond the Sword uses the population by itself.
#
# That line is a literal in the DLL, not a define in GlobalDefines, so it cannot be changed without
# rebuilding. What can be done from here is to hand each city back exactly what the second term
# took - max(0, population - 10) of happiness - which leaves the arithmetic identical to the
# vanilla rule and disturbs nothing else.
#
# The health formula at CvCity.cpp:5879 doubles in the same way and is deliberately left alone:
# this is about the complaint that was made, and unhealthiness is a separate decision.
#
# If the DLL is ever rebuilt with the vanilla formula restored, delete this module rather than
# leaving it in place. It would then be granting happiness that nothing is taking away.

from Core import *
from Events import handler


### BEGIN GAME TURN ###

@handler("BeginGameTurn")
def relieveOvercrowding(iGameTurn):
	"""Keep every city's relief in step with its population.

	Recomputed for every city each turn rather than hooked to growth: population moves for a great
	many reasons - growth, starvation, whipping, drafting, migration, conquest, a migrant settling
	- and a handler for each is a handler that can be forgotten.
	"""
	live = set()

	for iPlayer in players.major().existing():
		for city in cities.owner(iPlayer):
			relieve(city)
			live.add(location(city))

	# a razed or captured city leaves its entry behind, and a city founded later on the same tile
	# would then be measured against a stranger's population
	for tile in data.dOvercrowdingRelief.keys():
		if tile not in live:
			del data.dOvercrowdingRelief[tile]


def relieve(city):
	"""Give this city back the anger the second term of the overcrowding formula invented.

	Written as a tracked delta rather than an absolute value. Extra happiness is one field that
	world builder, events and anything else also write to, so setting it outright would quietly
	erase whatever else had contributed to it.
	"""
	tile = location(city)
	iRelief = max(0, city.getPopulation() - 10)
	iApplied = data.dOvercrowdingRelief.get(tile, 0)

	if iRelief == iApplied:
		return

	city.changeExtraHappiness(iRelief - iApplied)
	data.dOvercrowdingRelief[tile] = iRelief
