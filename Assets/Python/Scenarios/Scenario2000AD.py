from Scenario import *
from Core import *


# The world as it stands in 2000. Only civilizations historically extant are present -
# roughly a third of the mod's roster is gone, and its land belongs to whoever actually holds it.
# Rus and the Zulu are deliberately omitted despite qualifying on dates alone: Russia and
# South Africa already occupy their territory and represent them.
lCivilizations = [
	Civilization(
		iChina,
		iGold=900,
		iStateReligion=iConfucianism,
		lCivics=[iStateParty, iTransparency, iTotalitarianism, iCentralPlanning, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iGreece,
		iGold=900,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(18),
	),
	Civilization(
		iIndia,
		iGold=500,
		iStateReligion=iHinduism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iCelts,
		iGold=900,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(18),
	),
	Civilization(
		iEthiopia,
		iGold=250,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iKorea,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iKhmer,
		iGold=250,
		iStateReligion=iBuddhism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iFrance,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iMalays,
		iGold=900,
		iStateReligion=iIslam,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iJapan,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iNorse,
		iGold=900,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iBulgaria,
		iGold=500,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(17),
	),
	Civilization(
		iMoors,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iJava,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iSpain,
		iGold=1500,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iEngland,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iHolyRome,
		iGold=500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iBurma,
		iGold=250,
		iStateReligion=iBuddhism,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iVietnam,
		iGold=500,
		lCivics=[iStateParty, iTransparency, iTotalitarianism, iCentralPlanning, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iSwahili,
		iGold=250,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iMisr,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iHungary,
		iGold=900,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(18),
	),
	Civilization(
		iGeorgia,
		iGold=500,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iPoland,
		iGold=900,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(18),
	),
	Civilization(
		iPortugal,
		iGold=900,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(18),
	),
	Civilization(
		iInca,
		iGold=500,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iItaly,
		iGold=1500,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iMongols,
		iGold=500,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iMughals,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iThailand,
		iGold=900,
		iStateReligion=iBuddhism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iSweden,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iRussia,
		iGold=900,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iOttomans,
		iGold=900,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iSwitzerland,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iCongo,
		iGold=250,
		iStateReligion=iCatholicism,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iIran,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iNetherlands,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iGermany,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iSaudis,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iAmerica,
		iGold=2000,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(20),
	),
	Civilization(
		iHaiti,
		iGold=250,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iArgentina,
		iGold=900,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iMexico,
		iGold=900,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iColombia,
		iGold=500,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iBrazil,
		iGold=900,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iBelgium,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iMultilateralism],
		techs=techs.column(19),
	),
	Civilization(
		iAustralia,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iSouthAfrica,
		iGold=900,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iCanada,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iPhilippines,
		iGold=500,
		iStateReligion=iCatholicism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iIraq,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iIsrael,
		iGold=1500,
		iStateReligion=iJudaism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iTaiwan,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iNigeria,
		iGold=250,
		iStateReligion=iProtestantism,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iAlgeria,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iSingapore,
		iGold=1500,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
	),
	Civilization(
		iBangladesh,
		iGold=250,
		iStateReligion=iIslam,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(16),
	),
	Civilization(
		iUkraine,
		iGold=900,
		iStateReligion=iOrthodoxy,
		lCivics=[iDemocracy, iConstitution, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(18),
	),
	Civilization(
		iKazakhstan,
		iGold=500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(17),
	),
	Civilization(
		iNative,
		iGold=600,
		techs=techs.column(12)
	),
	Civilization(
		iIndependent2,
		iGold=1200,
		techs=techs.column(16)
	),
	Civilization(
		iIndependent,
		iGold=1200,
		techs=techs.column(16)
	),
]


# Civilizations whose every historical goal deadline has already passed.
lAllGoalsFailed = [
	iAmerica, iArgentina, iAustralia, iBangladesh, iBelgium, iBulgaria,
	iBurma, iCanada, iColombia, iEthiopia, iFrance, iGeorgia,
	iHaiti, iHolyRome, iHungary, iInca, iIran, iIsrael,
	iItaly, iJava, iKhmer, iMalays, iMexico, iMisr,
	iMongols, iMoors, iMughals, iNetherlands, iNorse, iOttomans,
	iPhilippines, iPortugal, iRussia, iSaudis, iSingapore, iSouthAfrica,
	iSwahili, iSweden, iSwitzerland, iTaiwan, iThailand, iVietnam,
]


def setupGoals(iCiv, goals):
	"""Fail the individual goals whose deadline is in the past.

	lAllGoalsFailed is whole-civilization, so civs that still hold at least one live goal need
	their expired ones failed here. Goal expiry is event-driven on the exact deadline turn
	(Victory/Goals.py:303), so nothing retro-expires them - an unfailed 1800 goal would sit at
	POSSIBLE and remain winnable in 2050.
	"""
	if iCiv == iChina:
		goals[0].fail()
		goals[2].fail()
	elif iCiv == iIndia:
		goals[1].fail()
		goals[2].fail()
	elif iCiv == iCelts:
		goals[2].fail()
	elif iCiv == iKorea:
		goals[0].fail()
	elif iCiv == iJapan:
		goals[0].fail()
		goals[1].fail()
	elif iCiv == iSpain:
		goals[1].fail()
		goals[2].fail()
	elif iCiv == iEngland:
		goals[0].fail()
		goals[1].fail()
	elif iCiv == iPoland:
		goals[0].fail()
		goals[2].fail()
	elif iCiv == iCongo:
		goals[0].fail()
		goals[1].fail()
	elif iCiv == iGermany:
		goals[0].fail()
		goals[1].fail()
	elif iCiv == iBrazil:
		goals[0].fail()
		goals[2].fail()
	elif iCiv == iIraq:
		goals[0].fail()
	elif iCiv == iAlgeria:
		goals[0].fail()


def updateData():
	# every New World civilization has long since been contacted
	data.dFirstContactConquerors = dict((iCiv, True) for iCiv in lBioNewWorld)

	# the trading companies have run their course
	for iCiv in lTradingCompanyCivs:
		data.civs[iCiv].bTradingCompanyConquerors = False


scenario2000AD = Scenario(
	iStartYear = 2000,
	fileName = "RFC_2000AD",

	lCivilizations = lCivilizations,

	iCultureTurns = 150,

	lAllGoalsFailed = lAllGoalsFailed,
	setupGoals = setupGoals,
	updateData = updateData,
)
