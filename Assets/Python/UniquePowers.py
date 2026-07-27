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


# Georgian UP: Monasteries of the Caucasus - the mountain monasteries of the Georgian golden age,
# which made a small kingdom a centre of learning out of all proportion to its size.
iGeorgianGreatPeople = 1


@handler("BeginPlayerTurn")
def georgianPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iGeorgia:
		return

	for city in cities.owner(iPlayer):
		if plots.ring(city).any(lambda plot: plot.isPeak()):
			city.changeGreatPeopleProgress(scale(iGeorgianGreatPeople))


# Zimbabwean UP: Gold of the Interior - Great Zimbabwe was built on the gold trade out of the
# Shona plateau, which reached the coast and from there the Indian Ocean.
iZimbabweanGold = 3


@handler("BeginPlayerTurn")
def zimbabweanPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iZimbabwe:
		return

	iSources = player(iPlayer).getNumAvailableBonuses(iGold) + player(iPlayer).getNumAvailableBonuses(iGems)
	if iSources <= 0:
		return

	iAmount = scale(iSources * iZimbabweanGold)
	player(iPlayer).changeGold(iAmount)

	if every(10):
		message(iPlayer, "TXT_KEY_UP_ZIMBABWE_EFFECT", iAmount, iSources, color=iYellow)


# Maori UP: Utu - the obligation of reciprocity. A victory defending your own ground is not just
# survival, it is mana, and mana is what a chief is measured by.
iMaoriCulture = 20


@handler("combatResult")
def maoriPower(winningUnit, losingUnit):
	iPlayer = winningUnit.getOwner()
	if civ(iPlayer) != iMaori:
		return

	# defending, and at home: utu is owed on your own land
	if plot(winningUnit).getOwner() != iPlayer:
		return

	defended = city(winningUnit)
	if not defended:
		return

	defended.changeCulture(iPlayer, scale(iMaoriCulture), True)


# Ashanti UP: the Golden Stool - the Akan state was built on gold, and the stool that embodied it
# was said to hold the soul of the nation. Prosperity and legitimacy were the same thing.
iAshantiGold = 6


@handler("cityGrowth")
def ashantiPower(city, iPlayer):
	if civ(iPlayer) != iAshanti:
		return

	iAmount = scale(iAshantiGold)
	player(iPlayer).changeGold(iAmount)


# Haitian UP: Revolution - an army of the formerly enslaved, which beat three European powers in
# succession. It fights hardest against the states that still hold people.
iHaitianExperience = 2


@handler("combatResult")
def haitianPower(winningUnit, losingUnit):
	iPlayer = winningUnit.getOwner()
	if civ(iPlayer) != iHaiti:
		return

	if not player(losingUnit.getOwner()).canUseSlaves():
		return

	winningUnit.changeExperience(iHaitianExperience, -1, False, False, False)


# Zulu UP: Impi - Shaka's reorganisation of the regiments, which turned a minor clan into the
# dominant military power of southern Africa within a decade.
iZuluExperience = 3


@handler("unitBuilt")
def zuluPower(city, unit):
	iPlayer = unit.getOwner()
	if civ(iPlayer) != iZulu:
		return

	if not isUnitOfRole(unit.getUnitType(), iAttack) and not isUnitOfRole(unit.getUnitType(), iShock):
		return

	unit.changeExperience(iZuluExperience, -1, False, False, False)


# South African UP: the Great Trek - the Boer republics were founded by wagon columns that simply
# went inland and declared the land theirs. Their claim arrived with them.
@handler("cityBuilt")
def southAfricanPower(city):
	iPlayer = city.getOwner()
	if civ(iPlayer) != iSouthAfrica:
		return

	convertSurroundingPlotCulture(iPlayer, plots.ring(city))


# Native American UP: the Land - a relationship to territory that did not depend on clearing it.
# Forest and marsh were not obstacles to be removed before the land could be worth something.
iNativeCulture = 1


@handler("BeginPlayerTurn")
def nativeAmericanPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iNativeAmericans:
		return

	for city in cities.owner(iPlayer):
		iWild = plots.ring(city).where(lambda plot: plot.getFeatureType() in (iForest, iJungle)).count()
		if iWild > 0:
			city.changeCulture(iPlayer, scale(iWild * iNativeCulture), True)


# Filipino UP: Seven Thousand Islands - an archipelago that was never one land to be held, and
# whose cities all faced outward across water rather than inward at each other.
iFilipinoCulture = 2


@handler("BeginPlayerTurn")
def filipinoPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iPhilippines:
		return

	for city in cities.owner(iPlayer).coastal():
		city.changeCulture(iPlayer, scale(iFilipinoCulture), True)


# Israeli UP: Start-Up Nation - a state that spent its whole existence under threat and answered
# with research rather than mass, because it never had the mass.
iIsraeliGreatPeople = 3


@handler("BeginPlayerTurn")
def israeliPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iIsrael:
		return

	# innovation under pressure: the power only runs while the country is threatened
	if team(iPlayer).getAtWarCount(True) <= 0:
		return

	capital_city = capital(iPlayer)
	if capital_city:
		capital_city.changeGreatPeopleProgress(scale(iIsraeliGreatPeople))


# Taiwanese UP: the Economic Miracle - an export economy built on manufacturing, where what the
# factories made was sold abroad rather than consumed at home.
iTaiwaneseGoldPerProduction = 4


@handler("BeginPlayerTurn")
def taiwanesePower(iGameTurn, iPlayer):
	if civ(iPlayer) != iTaiwan:
		return

	iProduction = cities.owner(iPlayer).sum(lambda city: city.getYieldRate(YieldTypes.YIELD_PRODUCTION))
	if iProduction <= 0:
		return

	player(iPlayer).changeGold(scale(iProduction / iTaiwaneseGoldPerProduction))


# Singaporean UP: Entrepot - a port that produced almost nothing and grew rich entirely on what
# passed through it.
iSingaporeanGoldPerRoute = 8


@handler("BeginPlayerTurn")
def singaporeanPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iSingapore:
		return

	iRoutes = cities.owner(iPlayer).sum(lambda city: city.getTradeRoutes())
	if iRoutes <= 0:
		return

	player(iPlayer).changeGold(scale(iRoutes * iSingaporeanGoldPerRoute))


# Bangladeshi UP: Delta Labour - one of the densest populations on earth, on land that floods, and
# an economy built on the sheer number of hands available rather than on what they were given.
iBangladeshiProduction = 5


@handler("BeginPlayerTurn")
def bangladeshiPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iBangladesh:
		return

	for city in cities.owner(iPlayer):
		if city.getPopulation() >= iBangladeshiProduction:
			city.changeCulture(iPlayer, scale(city.getPopulation() / iBangladeshiProduction), True)


# Iraqi UP: Rentier State - an economy where the oil is refined at home and the revenue does the
# work that an industrial base would otherwise have to.
iIraqiProduction = 2


@handler("BeginPlayerTurn")
def iraqiPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iIraq:
		return

	iFields = player(iPlayer).getNumAvailableBonuses(iOil)
	if iFields <= 0:
		return

	for city in cities.owner(iPlayer):
		city.changeProduction(scale(iFields * iIraqiProduction))


# Nigerian UP: the Giant of Africa - not a rich country in 2000, but an enormous one, and a
# domestic market that size is worth something on its own.
iNigerianGoldPerPopulation = 12


@handler("BeginPlayerTurn")
def nigerianPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iNigeria:
		return

	iPopulation = player(iPlayer).getTotalPopulation()
	if iPopulation <= 0:
		return

	player(iPlayer).changeGold(scale(iPopulation / iNigerianGoldPerPopulation))


# Algerian UP: Guerre d'Algerie - a war fought in a country the occupier never controlled outside
# the cities. An army inside Algeria bleeds whether or not anyone gives battle.
iAlgerianAttrition = 4


@handler("BeginPlayerTurn")
def algerianPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iAlgeria:
		return

	tPlayer = team(iPlayer)

	for unit in units.all().where(lambda unit: plot(unit).getOwner() == iPlayer):
		iOwner = unit.getOwner()

		if iOwner == iPlayer or is_minor(iOwner):
			continue

		if not tPlayer.isAtWar(player(iOwner).getTeam()):
			continue

		# never lethal: attrition wears an occupier down, it does not win the battle for you
		unit.setDamage(min(80, unit.getDamage() + iAlgerianAttrition), iPlayer)


# Ukrainian UP: the Breadbasket - the black earth of the steppe, which fed empires that had no
# particular interest in the people farming it.
iUkrainianFood = 2


@handler("BeginPlayerTurn")
def ukrainianPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iUkraine:
		return

	for city in cities.owner(iPlayer):
		city.changeFood(scale(iUkrainianFood))


# Kazakh UP: Baikonur - the steppe held the Soviet launch complex and the uranium that fuelled the
# programme, and the expertise stayed after the state that built it went.
iKazakhGreatPeople = 2


@handler("BeginPlayerTurn")
def kazakhPower(iGameTurn, iPlayer):
	if civ(iPlayer) != iKazakhstan:
		return

	iOre = player(iPlayer).getNumAvailableBonuses(iUranium)
	if iOre <= 0:
		return

	capital_city = capital(iPlayer)
	if capital_city:
		capital_city.changeGreatPeopleProgress(scale(iOre * iKazakhGreatPeople))
