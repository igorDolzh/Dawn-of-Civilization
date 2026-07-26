from Consts import *
from RFCUtils import *
from Events import *

def getModifier(iCivilization, iModifier):
	if iCivilization in lCivOrder:
		return tModifiers[iModifier][lCivOrder.index(iCivilization)]
	return tDefaults[iModifier]
	
def getAdjustedModifier(iPlayer, iModifier):
	if scenario() > i3000BC and dBirth[iPlayer] < dBirth[iNorse]:
		if iModifier in dLateScenarioModifiers:
			return getModifier(iPlayer, iModifier) * dLateScenarioModifiers[iModifier] / 100
	return getModifier(iPlayer, iModifier)
	
def getBaseModifier(iPlayer, iModifier):
	"""The value this player's civilization starts with, before any rule changes it at runtime.

	Identical to getAdjustedModifier except that it looks the civilization up explicitly. That one
	passes iPlayer straight into getModifier, which indexes lCivOrder - a plain list of
	civilizations, with no player resolution - so it silently falls through to tDefaults whenever
	the two ids differ. dBirth below is a CivDict and resolves players itself, which is why the
	discrepancy has never shown up.

	Anything that recomputes a modifier from its baseline every turn cannot tolerate that, so it
	uses this instead.
	"""
	iCivilization = civ(iPlayer)

	if scenario() > i3000BC and dBirth[iPlayer] < dBirth[iNorse]:
		if iModifier in dLateScenarioModifiers:
			return getModifier(iCivilization, iModifier) * dLateScenarioModifiers[iModifier] / 100

	return getModifier(iCivilization, iModifier)

def setModifier(iPlayer, iModifier, iNewValue):
	player(iPlayer).setModifier(iModifier, iNewValue)
	
def changeModifier(iPlayer, iModifier, iChange):
	setModifier(iPlayer, iModifier, player(iPlayer).getModifier(iModifier) + iChange)
	
def adjustModifier(iPlayer, iModifier, iPercent):
	setModifier(iPlayer, iModifier, player(iPlayer).getModifier(iModifier) * iPercent / 100)
	
def adjustModifiers(iPlayer):
	for iModifier in dLateScenarioModifiers:
		adjustModifier(iPlayer, iModifier, dLateScenarioModifiers[iModifier])
		
def adjustInflationModifier(iPlayer):
	adjustModifier(iPlayer, iModifierInflationRate, dLateScenarioModifiers[iModifierInflationRate])
	
def updateModifier(iPlayer, iCivilization, iModifier):
	setModifier(iPlayer, iModifier, getModifier(iCivilization, iModifier))
	
def updateModifiers(iPlayer, iCivilization):
	for iModifier in range(iNumModifiers):
		updateModifier(iPlayer, iCivilization, iModifier)


@handler("playerCivAssigned")
def init(iPlayer, iCivilization):
	updateModifiers(iPlayer, iCivilization)
	
	if scenario() > i3000BC and dBirth[iPlayer] < dBirth[iNorse]:
		adjustModifiers(iPlayer)
	
	player(iPlayer).updateMaintenance()


@handler("playerPeriodChange")
def onPeriodChange(iPlayer, iPeriod):
	if iPeriod == iPeriodMeiji:
		for iModifier in (iModifierResearchCost, iModifierCitiesMaintenance, iModifierCivicUpkeep, iModifierInflationRate):
			changeModifier(iPlayer, iModifier, -10)
	
	if iPeriod == iPeriodMing:
		for iModifier in (iModifierCitiesMaintenance, iModifierInflationRate):
			changeModifier(iPlayer, iModifier, -25)
		
		for iModifier in (iModifierCivicUpkeep, iModifierUnitCost, iModifierWonderCost):
			changeModifier(iPlayer, iModifier, -20)
		
		changeModifier(iPlayer, iModifierResearchCost, 10)


@handler("BeginGameTurn")
def updateLateModifiers(iGameTurn):			
	if scenario() == i3000BC and iGameTurn == year(600):
		for iPlayer in players.major().where(lambda p: dBirth[p] < dBirth[iNorse]):
			adjustInflationModifier(iPlayer)
		

### Modifier types ###

iNumModifiers = 14
(iModifierCulture, iModifierUnitUpkeep, iModifierResearchCost, iModifierDistanceMaintenance, iModifierColonyMaintenance,
iModifierCitiesMaintenance, iModifierCivicUpkeep, iModifierHealth, iModifierUnitCost, iModifierWonderCost, 
iModifierBuildingCost, iModifierInflationRate, iModifierGreatPeopleThreshold, iModifierGrowthThreshold) = range(iNumModifiers)

### Modifiers (by civilization!) ###

# 				            EGY BAB HAR ASS NUB CHI HIT GRE IND CAR POL PER CEL ROM MAY DRA ETH TOL KUS KOR KHM MAL BYZ FRA MAL JAP NOR TUR ARA TIB BUL MOO JAV SPA ENG HRE BUR RUS VIE SWA MIS HUN GEO POL NAM POR INC ITA MON AZT MUG ZIM THA SWE TAT RUS OTT MAO SWI CON IRA NET MAN ASH GER SAU AME HAI ARG MEX COL ZUL BRA BEL AUS SAF CAN IND IND NAT BAR

tCulture =		          ( 90, 80, 80, 80, 80, 80, 80,100, 80,100,100,100, 80,100,100,110, 90,100,100,100,120,130,100,150,120,110,100,120,110,120,130,125,120,125,130,150,120,120,100,110,100,110,100,110,100,140,140,100,135,140,125,100,120,130,130,130,150,100,110,130,135,165,150,100,150,120,140,100,130,140,140,100,140,180,140,100,140, 20, 20, 20, 30)	# Culture

tUnitUpkeep = 		      (135,120,200,100,130,120,110,110,135,115,100,120,110,100,110,100,115,110,120,100, 90,100,110,100,100,100, 90,100,100,110,100,110,100,110,100,100,100,100,100,100,120, 90,100,100,100,100,100,125, 90, 90,110,100, 90, 90, 80,110,120,100, 80, 90,110, 90, 85,100, 75, 80, 75,100, 80, 90, 90,100, 80, 90, 75,100, 75, 50, 50,100,100)	# Unit Upkeep
tResearchCost = 	      (150,140,125,120,150, 90,125,180,130,110,300,130,150,120,125,120,120,135,120,105, 90, 85,140, 90,100,120, 90,120,125, 90,120,100,100, 85, 75,100, 90, 90, 90,110,130,110,100, 85,100, 90, 80, 80,100, 80,120,100,115,100, 80, 85,100,100, 90, 85,110, 90,125,100, 75, 85, 75,100, 70, 90, 90,100, 90, 70, 75,100, 70,125,125,125,110)	# Research Cost
tDistanceMaintenance = 	  (150,110,120,100,125,125,120,110,120, 60, 75,110, 60, 70,100, 95,120,150,120,120, 80, 80,120, 90, 80,120, 70, 60,100,120,100, 80, 80, 90, 80, 85, 90, 90,110, 80,130, 90,100,100,100, 80, 60, 90, 75, 70,130,100,110, 80, 90, 80,100,100, 70, 80,100, 75,100,100, 80,125, 60,100, 50, 70, 70,100, 80, 80, 75,100, 70,100,100,100, 20)	# Distance Maintenance
tColonyMaintenance =      (150,150,150,150,150,150,150,150,125,125,125,150,125,125,150,100,150,150,150,150,150,125,150, 75,125,100,100,125,150,150,150,150,150, 75, 65,110,150,150,150,125,150,150,100,125,100, 90,125,100,150,125,150,100,150,150,100,125,125,100,150,150,150, 75,150,100, 90,150,110,100,125,125,125,100,125, 60,125,100,125,100,100,100, 20)	# Colony Maintenance
tCitiesMaintenance = 	  (120,135,125,100,150,125,125,125,150,120,100, 90,120, 70,115,100,110,160,120,130,100, 90,120, 85,100,125, 75, 90,100,120,100, 70,100, 75, 85, 75,100, 80,100, 70,130, 90,100, 80,100, 85, 80,100, 90, 85,120,100, 90,100, 75, 60,125,100, 80, 90,100, 90, 80,100, 75,120, 60,100, 50, 85, 85,100, 80,100, 70,100, 60,100,100,100, 30)	# Cities Maintenance
tCivicUpkeep = 		      (130,110,120,110,125,100,110,110,140, 70,100,100,120, 80, 80, 80,100,100,120, 80,100, 75,140, 90,100,120, 80,110, 80, 80,100, 90,100, 80, 75, 70,100, 80, 80, 80,120, 90,100, 80,100, 80, 60, 60, 60, 70,110,100, 80, 80, 65, 85, 90,100, 70, 80, 80, 75, 80,100, 60,120, 50,100, 50, 70, 70,100, 75, 80, 75,100, 75,100,100,100, 70)	# Civic Upkeep
tHealth = 		      	  (  1,  1,  1,  1,  1,  1,  1,  3,  1,  3,  3,  3,  1,  3,  3,  2,  3,  3,  3,  3,  3,  2,  3,  2,  3,  2,  3,  2,  2,  3,  2,  2,  3,  2,  2,  2,  3,  2,  3,  2,  2,  2,  2,  2,  2,  2,  3,  2,  3,  3,  4,  2,  3,  4,  2,  2,  3,  2,  3,  4,  3,  3,  3,  2,  3,  3,  3,  2,  3,  3,  3,  2,  3,  3,  3,  2,  3,  0,  0,  0,  0)	# Health

tUnitCost = 		      (125,140,200,120,140,120,100,110,120, 90,100,120,100, 80,105, 85,100,120,110, 80, 90, 90,115, 90,100,100, 85,100,100,110,100,100, 90, 90,100, 90, 80, 90, 90,100,110, 90,100, 80,100, 90,100,125, 80,100,100,100, 80, 90, 75,110,100,100, 90, 70, 90, 90,100,100, 75, 80, 85,100, 80, 85, 85,100, 85, 90, 85,100, 85,300,300,150,140)	# Unit Cost
tWonderCost = 		      ( 80, 80,120, 80,140,120,100, 80,100, 90,100, 90,120,100, 90,100,125,100,110,100, 90, 90,110, 70, 90,125, 90,120, 90,100, 90, 85, 80, 90, 90,100,100, 90,100,100, 90,100,100,100,100, 90, 80, 80,100, 80, 80,100,100, 90,100,100,100,100,100,100, 85,100,100,100, 90,110, 70,100, 70, 90, 90,100, 90, 80, 80,100, 80,150,150,150,100)	# Wonder Cost
tBuildingCost = 	      (110,110,100,110,120,100,110,100,110, 90,100,110,120, 80, 90, 70,100,120,110, 80,100, 80,110, 90, 90,110, 90,100,100, 80,100, 90, 90, 90, 90, 85,100, 90, 90, 80, 90,100,100, 80,100, 80, 70, 80, 80, 80, 85,100, 80, 80, 75,110, 80,100, 90, 80, 80, 80,100,100, 70, 90, 70,100, 70, 80, 80,100, 75, 75, 80,100, 80,100,100,150,100)	# Building Cost
tInflationRate = 	      (130,130,150,125,150,150,130,150,140,130,130,130,140,130,125,110,130,125,120, 90,100,120,130,100,100, 80, 70, 90,130,100,100, 85, 90, 90, 75, 70, 90,100, 90, 90,125,100,100, 75,100, 80, 80, 90, 90, 80,120,100, 90, 75, 70, 85,130,100, 70, 75, 85, 90,110,100, 70, 90, 65,100, 60, 65, 65,100, 60, 50, 65,100, 60, 95, 95, 95, 95)	# Inflation Rate
tGreatPeopleThreshold =   (140,140,140,140,140,125,140,140,125,120,120,120,140,110,100,110,110,120,120,110, 90, 80,120, 75, 90,100, 90, 90, 80, 85,110, 75,100, 75, 75, 80, 90, 90, 90, 80, 85,110,100, 80,100, 75, 70, 65, 70, 70,100,100,100, 80, 70, 80, 90,100, 90, 85, 80, 70,125,100, 65, 85, 65,100, 70, 80, 80,100, 80, 75, 80,100, 75,100,100,100,100)	# Great People Threshold
tGrowthThreshold = 	      (150,150,175,150,150,140,150,130,150,120,120,130,150,120,110,110,100,120,130,112, 80, 75, 90, 90,100,140, 80, 80, 80, 80,110, 80, 90, 80, 70, 80, 90, 80,120, 80, 75,110,100, 80,100, 80, 70, 70, 75, 70, 90,100, 75, 75, 80, 90, 70,100,120, 75, 70, 75,140,100, 70, 80, 70,100, 70, 70, 70,100, 70, 70, 70,100, 70,125,125,125,125)	# Growth Threshold

tModifiers = (tCulture, tUnitUpkeep, tResearchCost, tDistanceMaintenance, tColonyMaintenance, tCitiesMaintenance, tCivicUpkeep, tHealth, tUnitCost, tWonderCost, tBuildingCost, tInflationRate, tGreatPeopleThreshold, tGrowthThreshold)

tDefaults = (100, 100, 100, 100, 100, 100, 100, 2, 100, 100, 100, 100, 100, 100)

dLateScenarioModifiers = {
iModifierUnitUpkeep : 90,
iModifierDistanceMaintenance : 85,
iModifierCitiesMaintenance : 80,
iModifierCivicUpkeep : 90,
iModifierInflationRate : 85,
iModifierGreatPeopleThreshold : 85,
iModifierGrowthThreshold : 80,
}