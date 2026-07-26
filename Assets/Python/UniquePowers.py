from CvPythonExtensions import *
import CvUtil
import PyHelpers   
import Popup
from StoredData import data # edead
from Consts import *
from RFCUtils import *
from operator import itemgetter
from Events import handler

from Locations import *
from Core import *


@handler("firstCity")
def initBabylonianUP(city):
	# Babylonian UP: receive a free tech after discovering the first five techs
	iCivilization = civ(city)
	if iCivilization == iBabylonia:
		player(city).setFreeTechsOnDiscovery(5)


@handler("cityAcquired")
def arabianUP(iOwner, iPlayer, city):
	if civ(iPlayer) != iArabia:
		return

	iStateReligion = player(iArabia).getStateReligion()

	if iStateReligion >= 0:
		if not city.isHasReligion(iStateReligion):
			city.spreadReligion(iStateReligion)
		if not city.hasBuilding(temple(iStateReligion)):
			city.setHasRealBuilding(temple(iStateReligion), True)


@handler("cityAcquired")
def mongolUP(iOwner, iPlayer, city, bConquest):
	if civ(iPlayer) != iMongols:
		return
	
	if not bConquest:
		return
		
	if player(iPlayer).isHuman():
		return

	if city.getPopulation() >= 7:
		makeUnits(iMongols, iKeshik, city, 2, UnitAITypes.UNITAI_ATTACK_CITY)
	elif city.getPopulation() >= 4:
		makeUnit(iMongols, iKeshik, city, UnitAITypes.UNITAI_ATTACK_CITY)

	if city.getPopulation() >= 4:
		message(slot(iMongols), 'TXT_KEY_UP_MONGOL_HORDE')


@handler("combatResult")
def norseUP(winningUnit, losingUnit):
	iWinner = winningUnit.getOwner()
	if (civ(iWinner) == iNorse and year() <= year(1500)) or winningUnit.getUnitType() == iCorsair:
		if infos.unit(losingUnit).getDomainType() == DomainTypes.DOMAIN_SEA:
			iGold = scale(infos.unit(losingUnit).getProductionCost() / 2)
			player(iWinner).changeGold(iGold)
			message(iWinner, 'TXT_KEY_NORSE_NAVAL_UP', iGold, adjective(losingUnit), losingUnit.getName())
			
			events.fireEvent("combatGold", iWinner, iGold)


# Mughal UP: receives 50% of building cost as culture when building is completed
@handler("buildingBuilt")
def mughalUP(city, iBuilding):
	if civ(city) == iMughals:
		iCost = player(city).getBuildingProductionNeeded(iBuilding)
		city.changeCulture(city.getOwner(), iCost / 2, True)


@handler("BeginGameTurn")
def resetBabylonianPower():
	data.bBabyloniaTechReceived = False


@handler("cityAcquired")
def colombianPower(iOwner, iPlayer, city, bConquest):
	if civ(iPlayer) == iColombia and bConquest:
		if city in cities.regions(*(lCentralAmerica + lSouthAmerica)):
			city.setOccupationTimer(0)


@handler("techAcquired")
def mayanPower(iTech, iTeam, iPlayer):
	iEra = player(iPlayer).getCurrentEra()
	if civ(iPlayer) == iMaya and iEra < iMedieval:
		iNumCities = player(iPlayer).getNumCities()
		if iNumCities > 0:
			iFood = scale(20) / iNumCities
			for city in cities.owner(iPlayer):
				city.changeFood(iFood)
			
			message(iPlayer, 'TXT_KEY_MAYA_UP_EFFECT', infos.tech(iTech).getText(), iFood)


@handler("changeWar")
def resetMongolPower(bWar, iTeam, iOtherTeam):
	if not bWar and iMongols in civs.of(iTeam, iOtherTeam):
		for city in cities.owner(iMongols):
			city.setMongolUP(False)


@handler("improvementBuilt")
def americanImprovementPower(iImprovement, x, y):
	if scenarioStart():
		return
	
	improved = plot(x, y)
	if iImprovement >= 0 and improved.isOwned() and civ(improved) == iAmerica and not improved.isWater():
		if improved.getBonusType(improved.getTeam()) >= 0 and infos.improvement(iImprovement).isImprovementBonusTrade(improved.getBonusType(improved.getTeam())) and not infos.improvement(iImprovement).isActsAsCity():
			improved_city = improved.getWorkingCity()
			if not improved_city or improved_city.isNone():
				closest = closestCity(improved, owner=improved.getOwner())
				if closest and not closest.isNone() and distance(closest, improved) <= 3:
					improved_city = closest
			
			if improved_city and not improved_city.isNone():
				improved_city.changePopulation(1)
				improved_city.changeHappinessTimer(turns(10))
				
				message(improved.getOwner(), "TXT_KEY_UP_MANIFEST_DESTINY_IMPROVEMENT", infos.bonus(improved.getBonusType(improved.getTeam())).getText(), improved_city.getName())


@handler("immigration")
def americanImmigrationPower(_, city):
	if civ(city) == iAmerica:
		city.changePopulation(1)
		city.changeHappinessTimer(turns(10))
		
		message(city.getOwner(), "TXT_KEY_UP_MANIFEST_DESTINY_IMMIGRATION", city.getName())


@handler("cityAcquired")
def assyrianPower(iOwner, iPlayer, city, bConquest):
	if civ(iPlayer) == iAssyria and bConquest:
		city.setOccupationTimer(0)


@handler("unitSpreadReligionAttempt")
def kushanPower(unit, iReligion, bSuccess):
	if civ(unit.getOwner()) == iKushans and bSuccess:
		spread_city = city(unit)
		capital_city = capital(unit)
		if spread_city and capital_city:
			if player(spread_city.getOwner()).getStateReligion() != iReligion:
				iGold = scale(20 + distance(capital_city, spread_city))
				message(unit.getOwner(), "TXT_KEY_UP_SYNCRETISM_EFFECT", iGold, infos.religion(iReligion).getText(), spread_city.getName(), location=spread_city, button=infos.religion(iReligion).getButton())
				player(unit.getOwner()).changeGold(iGold)


@handler("unitPillage")
def tatarPillagePower(unit, iImprovement):
	if civ(unit.getOwner()) == iTatars and iImprovement >= 0:
		unit.changeExperience(1, 1000, True, False, True)


@handler("unitCaptured")
def tatarCapturePower(iOwner, iUnit, unit):
	iPlayer = unit.getOwner()
	if civ(iPlayer) == iTatars:
		iGold = scale(20)
		message(iPlayer, "TXT_KEY_UP_DESPOILMENT_EFFECT", iGold, adjective(iOwner), unit.getName(), location=unit, button=unit.getButton())
		player(iPlayer).changeGold(iGold)
		
		events.fireEvent("combatGold", iPlayer, iGold)


# Swiss UP: Armed Neutrality - a share of every war we stay out of, in mercenary contracts and
# in the deposits of people who would rather their money sat somewhere quiet.
iSwissNeutralityGold = 4


@handler("BeginPlayerTurn")
def swissPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iSwitzerland:
		return

	# the power is neutrality itself: fighting forfeits it
	if team(iPlayer).getAtWarCount(True) > 0:
		return

	iWars = otherWars(iPlayer)
	if iWars <= 0:
		return

	iGold = scale(iWars * iSwissNeutralityGold)
	player(iPlayer).changeGold(iGold)

	# once a decade rather than every turn, or the log becomes unreadable
	if every(10):
		message(iPlayer, "TXT_KEY_UP_NEUTRALITY_EFFECT", iGold, iWars, color=iYellow)


def otherWars(iPlayer):
	"""Wars between other major civilizations, counted once per pair."""
	others = players.major().existing().where(lambda p: p != iPlayer)
	lOthers = [p for p in others]

	iCount = 0
	for i, iFirst in enumerate(lOthers):
		for iSecond in lOthers[i+1:]:
			if team(iFirst).isAtWar(player(iSecond).getTeam()):
				iCount += 1

	return iCount


# Hungarian UP: Bulwark of Christendom - the border forts that held the Mongols and then the
# Ottomans. A war of religion against Hungary finds the frontier already garrisoned.
iHungarianDefenders = 2


@handler("changeWar")
def hungarianPower(bWar, iTeam, iOtherTeam):
	if not bWar:
		return

	for iPlayer in players.major().existing().where(lambda p: civ(p) == iHungary):
		if player(iPlayer).getTeam() != iTeam:
			continue

		iAttacker = slot_of_team(iOtherTeam)
		if iAttacker < 0:
			continue

		# only against a different faith - this is a frontier power, not a general one
		if player(iAttacker).getStateReligion() == player(iPlayer).getStateReligion():
			continue

		garrison(iPlayer)


def garrison(iPlayer):
	"""Reinforce the core, where the border castles stood."""
	core = cities.owner(iPlayer).core(iPlayer)

	for city in core:
		ensureDefenders(iPlayer, location(city), iHungarianDefenders)

	if core:
		message(iPlayer, "TXT_KEY_UP_BULWARK_EFFECT", core.count(), color=iYellow)


def slot_of_team(iTeam):
	for iPlayer in players.major().existing():
		if player(iPlayer).getTeam() == iTeam:
			return iPlayer
	return -1


# Bulgarian UP: the Cyrillic alphabet. Bulgaria gave the Slavs their letters, and the prestige of
# that ran far past its borders - so its culture grows with the reach of the faith it wrote for.
iBulgarianCulturePerCity = 1


@handler("BeginPlayerTurn")
def bulgarianPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iBulgaria:
		return

	if player(iPlayer).getStateReligion() != iOrthodoxy:
		return

	iForeign = cities.all().religion(iOrthodoxy).where(lambda city: city.getOwner() != iPlayer).count()
	if iForeign <= 0:
		return

	iCulture = scale(iForeign * iBulgarianCulturePerCity)

	for city in cities.owner(iPlayer):
		city.changeCulture(iPlayer, iCulture, True)

	if every(10):
		message(iPlayer, "TXT_KEY_UP_CYRILLIC_EFFECT", iCulture, iForeign, color=iYellow)
