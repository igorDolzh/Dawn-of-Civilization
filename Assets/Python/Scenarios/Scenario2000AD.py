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
		Control(plots.rectangle((120, 51), (123, 56)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iGreece: (
		Control(plots.rectangle((74, 50), (80, 53)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iIndia: (
		Control(plots.rectangle((108, 43), (110, 46)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iCelts: (
		# Ireland, not Aquitaine. Periods applies iPeriodInsularCelts at a 2000 start, whose core
		# area is ((52, 64), (56, 67)) with Dublin as capital; the generated rectangle sat in
		# south-west France and overlapped France's own homeland on every row.
		Control(plots.rectangle((61, 56), (63, 59)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iEthiopia: (
		Control(plots.rectangle((82, 33), (84, 36)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iKorea: (
		Control(plots.rectangle((130, 53), (132, 56)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iKhmer: (
		Control(plots.rectangle((120, 36), (121, 38)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iFrance: (
		Control(plots.rectangle((59, 60), (64, 60)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iMalays: (
		Control(plots.rectangle((121, 26), (121, 32)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iJapan: (
		Control(plots.rectangle((135, 51), (139, 54)).named(HOMELAND), at=2050),
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
		Control(plots.rectangle((55, 44), (59, 50)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iJava: (
		Control(plots.rectangle((125, 24), (127, 25)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSpain: (
		Control(plots.rectangle((56, 51), (59, 54)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iEngland: (
		Control(plots.rectangle((56, 63), (58, 66)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iHolyRome: (
		Control(plots.rectangle((65, 61), (68, 63)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iBurma: (
		Control(plots.rectangle((116, 40), (117, 43)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iVietnam: (
		Control(plots.rectangle((120, 42), (122, 43)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSwahili: (
		Control(plots.rectangle((83, 20), (85, 25)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iMisr: (
		Control(plots.rectangle((77, 41), (80, 45)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iHungary: (
		Control(plots.rectangle((72, 57), (74, 59)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iGeorgia: (
		Control(plots.rectangle((88, 54), (90, 56)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iPoland: (
		Control(plots.rectangle((72, 61), (75, 63)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iPortugal: (
		Control(plots.rectangle((54, 50), (55, 52)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iInca: (
		Control(plots.rectangle((29, 22), (32, 24)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iItaly: (
		Control(plots.rectangle((66, 54), (69, 57)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iMongols: (
		Control(plots.rectangle((116, 57), (122, 64)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iMughals: (
		Control(plots.rectangle((103, 45), (106, 48)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iThailand: (
		Control(plots.rectangle((118, 34), (119, 39)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iSweden: (
		Control(plots.rectangle((71, 70), (73, 72)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iRussia: (
		Control(plots.rectangle((82, 64), (87, 68)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iOttomans: (
		Control(plots.rectangle((81, 51), (83, 55)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iSwitzerland: (
		Control(plots.rectangle((64, 57), (66, 59)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iCongo: (
		Control(plots.rectangle((71, 24), (72, 27)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iIran: (
		Control(plots.rectangle((91, 48), (94, 50)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iNetherlands: (
		Control(plots.rectangle((62, 63), (63, 65)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iGermany: (
		Control(plots.rectangle((66, 64), (76, 65)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iSaudis: (
		Control(plots.rectangle((87, 39), (90, 42)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iAmerica: (
		Control(plots.rectangle((26, 53), (30, 57)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 4, by=2080),
		GoldAmount(60000, by=2070),
	),
	iHaiti: (
		Control(plots.rectangle((31, 42), (33, 43)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iArgentina: (
		Control(plots.rectangle((36, 13), (38, 15)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iMexico: (
		Control(plots.rectangle((16, 41), (18, 44)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iColombia: (
		Control(plots.rectangle((28, 32), (32, 38)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iBrazil: (
		Control(plots.rectangle((42, 19), (45, 24)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iBelgium: (
		Control(plots.rectangle((61, 61), (63, 62)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iAustralia: (
		Control(plots.rectangle((140, 10), (143, 15)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iSouthAfrica: (
		Control(plots.rectangle((72, 11), (74, 13)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iCanada: (
		Control(plots.rectangle((27, 59), (33, 63)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iPhilippines: (
		Control(plots.rectangle((129, 36), (131, 39)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iIraq: (
		Control(plots.rectangle((87, 46), (89, 50)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iIsrael: (
		Control(plots.rectangle((83, 44), (85, 45)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iTaiwan: (
		Control(plots.rectangle((127, 46), (128, 48)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iNigeria: (
		Control(plots.rectangle((63, 31), (66, 34)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iAlgeria: (
		Control(plots.rectangle((60, 45), (63, 48)).named(HOMELAND), at=2050),
		PopulationCount(45, by=2060),
		GoldAmount(15000, by=2070),
	),
	iSingapore: (
		Control(plots.rectangle((119, 28), (120, 31)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iBangladesh: (
		Control(plots.rectangle((112, 42), (113, 44)).named(HOMELAND), at=2050),
		PopulationCount(35, by=2060),
		GoldAmount(8000, by=2070),
	),
	iUAE: (
		Control(plots.rectangle((92, 40), (95, 41)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 3, by=2080),
		GoldAmount(40000, by=2070),
	),
	iUkraine: (
		Control(plots.rectangle((79, 60), (82, 64)).named(HOMELAND), at=2050),
		EraFirstDiscover(iSynthetic, 2, by=2080),
		GoldAmount(25000, by=2070),
	),
	iKazakhstan: (
		Control(plots.rectangle((100, 57), (105, 63)).named(HOMELAND), at=2050),
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


# Goals carry a title in the victory screen, and only HistoricalVictory decorates its own dGoals -
# a scenario table never passes through that loop, so these would render with no title at all.
# The per-civ TXT_KEY_VICTORY_TITLE_<IDENT><n> keys cannot be reused: they name each civilization's
# historical goals, which these are not. Every civ here has the same three goals in the same order,
# so three generic titles say the truth without inventing 180 new keys.
lGoalTitles2000 = [
	"TXT_KEY_VICTORY_TITLE_2000_HOMELAND",
	"TXT_KEY_VICTORY_TITLE_2000_DEVELOPMENT",
	"TXT_KEY_VICTORY_TITLE_2000_ECONOMY",
]

for iCiv, goals in dGoals2000.items():
	for index, goal in enumerate(goals):
		if index < len(lGoalTitles2000):
			goal.options["title_key"] = lGoalTitles2000[index]


# Every one of the 99 entries in WONDER_ORIGINAL_BUILDERS predates 2000, so expireWonders would
# mark all of them created - including the ten religious shrines, which are an income mechanic
# rather than a monument. The religions are already founded and spread across 271 cities on this
# map, so their shrines have to stay buildable or that income is unobtainable for the whole game.
# Itsukushima is deliberately absent: it is an actual historical building and should stay expired.
lUnexpiredWonders2000 = [
	iJewishShrine, iCatholicShrine, iOrthodoxShrine, iProtestantShrine, iIslamicShrine,
	iBuddhistShrine, iHinduShrine, iConfucianShrine, iTaoistShrine, iZoroastrianShrine,
]


# By 2000 there is no terra incognita. Rather than the per-civ-group tables the earlier scenarios
# use to model partial exploration, every group sees the whole world.
lAllLand = lEurope + lAsia + lAfrica + lAmerica + lOceania

# the water regions have no grouping list of their own; they occupy a contiguous block of ids
lAllWater = range(100, 100 + iNumWaterRegions)

tKnownWorld = Revealed(
	lLandRegions = lAllLand,
	lCoastRegions = lAllLand,
	lSeaRegions = lAllWater,
)

dRevealed2000 = dict((iCivGroup, tKnownWorld) for iCivGroup in range(iNumCivGroups))


scenario2000AD = Scenario(
	iStartYear = 2000,
	fileName = "RFC_2000AD",

	lCivilizations = lCivilizations,

	iCultureTurns = 150,

	lUnexpiredWonders = lUnexpiredWonders2000,
	dRevealed = dRevealed2000,

	dGoals = dGoals2000,
	updateData = updateData,
)
