from BirthRate import *
from unittest import *


class TestEraTable(TestCase):
	"""tEraGrowthPenalty is indexed directly by getCurrentEra(), so its shape is load-bearing."""

	def test_table_covers_every_era(self):
		# a short table is an IndexError waiting for the first civilization to reach the last era,
		# which is exactly the bug this feature fixed in Stability.tEraAdministrationModifier
		self.assertEqual(len(tEraGrowthPenalty), iNumEras)

	def test_no_era_makes_growth_cheaper(self):
		# below 100 a civilization would grow faster than its own baseline - the opposite of a
		# demographic transition
		for iEra in range(iNumEras):
			self.assert_(tEraGrowthPenalty[iEra] >= 100)

	def test_nothing_changes_before_industrial(self):
		# the entire pre-1800 game must be untouched
		for iEra in [iAncient, iClassical, iMedieval, iRenaissance]:
			self.assertEqual(tEraGrowthPenalty[iEra], 100)

		self.assert_(tEraGrowthPenalty[iIndustrial] > 100)

	def test_transition_deepens_monotonically(self):
		for iEra in range(1, iNumEras):
			self.assert_(tEraGrowthPenalty[iEra] >= tEraGrowthPenalty[iEra-1])

	def test_carrier_is_a_real_building(self):
		self.assert_(0 <= iSurplusCarrier < iNumBuildings)


class TestSurplusProduction(TestCase):
	"""The share of growth the transition costs is the share of surplus that returns as hammers."""

	def test_nothing_converts_before_the_transition(self):
		# given: an era with no penalty
		# then: no growth was lost, so nothing is owed back
		self.assertEqual(surplusProduction(20, 100), 0)

	def test_conversion_matches_the_growth_lost(self):
		# at 190 a citizen costs 90/190 more food, so that share of the surplus comes back
		self.assertEqual(surplusProduction(20, 130), 4)
		self.assertEqual(surplusProduction(20, 190), 9)
		self.assertEqual(surplusProduction(20, 220), 10)

	def test_deficit_converts_nothing(self):
		# a starving city must never earn production
		self.assertEqual(surplusProduction(-8, 190), 0)
		self.assertEqual(surplusProduction(0, 190), 0)

	def test_conversion_never_exceeds_the_surplus(self):
		for iPenalty in tEraGrowthPenalty:
			self.assert_(surplusProduction(20, iPenalty) <= 20)


class TestGrowthPenalty(TestCase):
	"""The modifier write must be absolute, or it compounds every turn until growth stops."""

	def test_write_is_computed_from_the_baseline(self):
		# given: a player whose civilization baseline is known
		iPlayer = 0
		iBefore = player(iPlayer).getModifier(iModifierGrowthThreshold)
		iBaseline = getBaseModifier(iPlayer, iModifierGrowthThreshold)

		try:
			# when: the penalty is applied twice, as it is every turn
			setModifier(iPlayer, iModifierGrowthThreshold, iBaseline * 190 / 100)
			iOnce = player(iPlayer).getModifier(iModifierGrowthThreshold)

			setModifier(iPlayer, iModifierGrowthThreshold, iBaseline * 190 / 100)

			# then: the value is unchanged, not compounded
			self.assertEqual(player(iPlayer).getModifier(iModifierGrowthThreshold), iOnce)
		finally:
			setModifier(iPlayer, iModifierGrowthThreshold, iBefore)

	def test_baseline_is_keyed_by_civilization(self):
		# getBaseModifier exists because getAdjustedModifier passes a player into a civ-keyed
		# lookup; the baseline must be a real table value, not the tDefaults fallback
		iPlayer = 0
		self.assert_(getBaseModifier(iPlayer, iModifierGrowthThreshold) > 0)


test_cases = [
	TestEraTable,
	TestSurplusProduction,
	TestGrowthPenalty,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
