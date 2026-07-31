from Scenario import *
from Core import *

# The goal vocabulary used by dGoals2000 below. This import MUST come after Core: Definitions
# redefines `plots` as an AreaArgumentFactory, and that is the type the Requirement classes expect -
# Core's PlotFactory builds a different object and Control would not accept it. Nothing above this
# line uses `plots`, and name resolution is per module, so Scenario.py keeps Core's version.
from Definitions import *

# Area name shown in goal descriptions. Declared here rather than imported from HistoricalVictory,
# which owns the master list: ReligiousVictory.py declares its own the same way, and importing that
# module would pull in every historical goal in the game for the sake of one string.
HOMELAND = "TXT_KEY_VICTORY_NAME_HOMELAND"


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
		iUAE,
		iGold=1500,
		iStateReligion=iIslam,
		lCivics=[iStateParty, iBureaucracy, iEgalitarianism, iFreeEnterprise, iSecularism, iNationhood],
		techs=techs.column(19),
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


# Goals for a 2000 AD start. The historical set is unusable here - almost every deadline in it
# expired centuries ago - so this scenario supplies its own, all of them looking forward into the
# century the game actually covers. Every other scenario keeps the historical goals untouched.
#
# Each civilization gets the same shape: hold your homeland, reach a demographic or economic
# mark scaled to where you stood in 2000, and one goal of quality rather than quantity.
dGoals2000 = {
	iChina: (
		Control(plots.rectangle((120, 51), (126, 56)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iGreece: (
		Control(plots.rectangle((74, 49), (80, 53)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iIndia: (
		Control(plots.rectangle((105, 44), (111, 46)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iCelts: (
		Control(plots.rectangle((59, 56), (63, 61)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iEthiopia: (
		Control(plots.rectangle((82, 33), (85, 36)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iKorea: (
		Control(plots.rectangle((130, 53), (132, 56)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iKhmer: (
		Control(plots.rectangle((120, 36), (122, 38)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iFrance: (
		Control(plots.rectangle((59, 57), (63, 62)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iMalays: (
		Control(plots.rectangle((119, 26), (121, 31)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iJapan: (
		Control(plots.rectangle((135, 52), (140, 55)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iNorse: (
		Control(plots.rectangle((65, 67), (68, 75)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iBulgaria: (
		Control(plots.rectangle((76, 56), (79, 58)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iMoors: (
		Control(plots.rectangle((56, 44), (61, 50)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iJava: (
		Control(plots.rectangle((125, 24), (128, 25)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSpain: (
		Control(plots.rectangle((54, 51), (59, 54)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iEngland: (
		Control(plots.rectangle((56, 63), (59, 67)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iHolyRome: (
		Control(plots.rectangle((64, 59), (70, 63)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iBurma: (
		Control(plots.rectangle((116, 38), (117, 43)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iVietnam: (
		Control(plots.rectangle((120, 41), (122, 43)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSwahili: (
		Control(plots.rectangle((83, 19), (85, 27)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iMisr: (
		Control(plots.rectangle((76, 40), (81, 45)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iHungary: (
		Control(plots.rectangle((72, 57), (75, 60)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iGeorgia: (
		Control(plots.rectangle((88, 54), (90, 56)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iPoland: (
		Control(plots.rectangle((72, 61), (76, 64)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iPortugal: (
		Control(plots.rectangle((54, 50), (55, 52)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iInca: (
		Control(plots.rectangle((28, 22), (32, 24)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iItaly: (
		Control(plots.rectangle((65, 54), (70, 57)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iMongols: (
		Control(plots.rectangle((116, 57), (126, 66)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iMughals: (
		Control(plots.rectangle((102, 45), (107, 48)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iThailand: (
		Control(plots.rectangle((118, 34), (120, 39)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iSweden: (
		Control(plots.rectangle((71, 69), (73, 73)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iRussia: (
		Control(plots.rectangle((81, 65), (90, 70)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iOttomans: (
		Control(plots.rectangle((79, 51), (84, 55)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iSwitzerland: (
		Control(plots.rectangle((64, 57), (67, 59)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iCongo: (
		Control(plots.rectangle((71, 24), (74, 27)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iIran: (
		Control(plots.rectangle((91, 48), (94, 52)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iNetherlands: (
		Control(plots.rectangle((62, 63), (63, 65)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iGermany: (
		Control(plots.rectangle((65, 62), (76, 66)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iSaudis: (
		Control(plots.rectangle((86, 38), (90, 42)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iAmerica: (
		Control(plots.rectangle((25, 54), (32, 58)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 4, by=2080),
		GoldAmount(60000, by=2070),
	),
	iHaiti: (
		Control(plots.rectangle((31, 42), (32, 43)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iArgentina: (
		Control(plots.rectangle((35, 13), (38, 16)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iMexico: (
		Control(plots.rectangle((14, 41), (19, 44)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iColombia: (
		Control(plots.rectangle((26, 34), (35, 38)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iBrazil: (
		Control(plots.rectangle((42, 19), (47, 25)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iBelgium: (
		Control(plots.rectangle((61, 61), (63, 63)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iAustralia: (
		Control(plots.rectangle((139, 9), (143, 13)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iSouthAfrica: (
		Control(plots.rectangle((72, 11), (75, 13)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iCanada: (
		Control(plots.rectangle((26, 59), (37, 62)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iPhilippines: (
		Control(plots.rectangle((128, 35), (130, 39)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iIraq: (
		Control(plots.rectangle((87, 46), (91, 50)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iIsrael: (
		Control(plots.rectangle((83, 44), (85, 46)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iTaiwan: (
		Control(plots.rectangle((128, 46), (128, 47)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iNigeria: (
		Control(plots.rectangle((61, 29), (65, 33)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iAlgeria: (
		Control(plots.rectangle((59, 45), (65, 48)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSingapore: (
		Control(plots.rectangle((120, 29), (121, 30)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iBangladesh: (
		Control(plots.rectangle((112, 42), (114, 44)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iUAE: (
		Control(plots.rectangle((93, 40), (95, 42)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iUkraine: (
		Control(plots.rectangle((78, 60), (83, 64)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iKazakhstan: (
		Control(plots.rectangle((98, 57), (106, 63)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
}




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

	dGoals = dGoals2000,
	updateData = updateData,
)
