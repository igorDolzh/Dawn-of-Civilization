from Revolutions import *
from unittest import *


class TestConstants(TestCase):

	def test_civics_are_real(self):
		for iCivic in lAncienRegime:
			self.assert_(0 <= iCivic < iNumCivics)

		for iCivic in (iLiberalGovernment, iLiberalLegitimacy, iSocialistEconomy, iSocialistGovernment):
			self.assert_(0 <= iCivic < iNumCivics)

	def test_neither_revolution_installs_what_it_overthrew(self):
		self.assert_(iLiberalGovernment not in lAncienRegime)
		self.assert_(iSocialistGovernment not in lAncienRegime)

	def test_the_two_kinds_have_different_outcomes(self):
		# the whole point of the split: 1917 must not produce a constitutional republic
		self.assertNotEqual(iLiberalGovernment, iSocialistGovernment)

	def test_techs_are_real(self):
		for iTech in lLiberalIdeas + [iSocialistIdea, iSocialistGovernmentTech]:
			self.assert_(0 <= iTech < iNumTechs)

	def test_suppression_penalty_is_negative(self):
		self.assert_(iSuppressionPenalty < 0)


class TestSocialistPrecedence(TestCase):
	"""A war-broken autocracy satisfies both. If liberal won, 1917 would stop at Kerensky."""

	def test_socialist_is_checked_before_liberal(self):
		import inspect
		source = inspect.getsource(checkRevolutions)

		self.assert_(source.index('isSocialistRipe') < source.index('isLiberalRipe'))

	def test_socialist_does_not_require_an_ancien_regime(self):
		# Russia in October was already a republic; February had seen to that
		import inspect
		source = inspect.getsource(isSocialistRipe)

		self.assert_('isAncienRegime' not in source)

	def test_liberal_does_require_an_ancien_regime(self):
		import inspect
		source = inspect.getsource(isLiberalRipe)

		self.assert_('isAncienRegime' in source)

	def test_socialist_requires_a_losing_long_war(self):
		import inspect
		source = inspect.getsource(isSocialistRipe)

		self.assert_('isLosingLongWar' in source)


class TestContagionIsBounded(TestCase):
	"""Without a ceiling, a decay and a cooldown, one revolution flips the whole world."""

	def test_pressure_has_a_ceiling(self):
		iPlayer = 0
		try:
			setPressure(iPlayer, iLiberal, iPressureCeiling + iPressurePerRevolution)
			self.assertEqual(pressure(iPlayer, iLiberal), iPressureCeiling)
		finally:
			setPressure(iPlayer, iLiberal, 0)

	def test_pressure_has_a_floor(self):
		iPlayer = 0
		try:
			setPressure(iPlayer, iLiberal, -100)
			self.assertEqual(pressure(iPlayer, iLiberal), 0)
		finally:
			setPressure(iPlayer, iLiberal, 0)

	def test_the_two_pressures_are_independent(self):
		# a liberal revolution must not make its neighbours communist
		iPlayer = 0
		try:
			setPressure(iPlayer, iLiberal, iPressurePerRevolution)

			self.assertEqual(pressure(iPlayer, iLiberal), iPressurePerRevolution)
			self.assertEqual(pressure(iPlayer, iSocialist), 0)
		finally:
			setPressure(iPlayer, iLiberal, 0)

	def test_decay_is_actually_positive(self):
		self.assert_(iPressureDecay > 0)

	def test_saturated_neighbourhood_is_not_a_certainty(self):
		# the roll is rand(100) < iBaseChance + pressure
		self.assert_(iBaseChance + iPressureCeiling < 100)

	def test_cooldown_is_longer_than_the_check_interval(self):
		self.assert_(iCooldown > iCheckInterval)


class TestPreconditions(TestCase):

	def test_years(self):
		self.assertEqual(iLiberalYear, 1789)
		self.assert_(iSocialistYear > iLiberalYear)

	def test_ancien_regime_membership(self):
		self.assert_(iRepublic not in lAncienRegime)
		self.assert_(iMonarchy in lAncienRegime)

	def test_vulnerable_stability_excludes_healthy_states(self):
		self.assert_(iVulnerableStability < iStabilityStable)

	def test_socialist_economy_alone_counts_as_communist(self):
		# Civics.isCommunist returns True on iEconomy == iCentralPlanning, which is what lets the
		# revolution succeed in the Industrial era and acquire its party-state later
		self.assertEqual(iSocialistEconomy, iCentralPlanning)


test_cases = [
	TestConstants,
	TestSocialistPrecedence,
	TestContagionIsBounded,
	TestPreconditions,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
