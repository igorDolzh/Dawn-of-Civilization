from Revolutions import *
from unittest import *


class TestConstants(TestCase):

	def test_civics_are_real(self):
		for iCivic in lAncienRegime:
			self.assert_(0 <= iCivic < iNumCivics)

		self.assert_(0 <= iRevolutionaryGovernment < iNumCivics)
		self.assert_(0 <= iRevolutionaryLegitimacy < iNumCivics)

	def test_revolution_does_not_install_what_it_overthrew(self):
		self.assert_(iRevolutionaryGovernment not in lAncienRegime)

	def test_ideas_are_real_techs(self):
		for iTech in lRevolutionaryIdeas:
			self.assert_(0 <= iTech < iNumTechs)

	def test_suppression_penalty_is_negative(self):
		self.assert_(iSuppressionPenalty < 0)


class TestContagionIsBounded(TestCase):
	"""Without a ceiling, a decay and a cooldown, one revolution flips the whole world."""

	def test_pressure_has_a_ceiling(self):
		# given: a civilization already at the ceiling
		iPressure = iPressureCeiling

		# when: another revolution happens next door
		iPressure = min(iPressureCeiling, iPressure + iPressurePerRevolution)

		# then: it does not climb further
		self.assertEqual(iPressure, iPressureCeiling)

	def test_pressure_decays_to_zero_and_stops(self):
		iPressure = iPressureCeiling
		for _ in range(1000):
			iPressure = max(0, iPressure - iPressureDecay)

		self.assertEqual(iPressure, 0)

	def test_decay_is_actually_positive(self):
		# a decay of zero would make pressure permanent
		self.assert_(iPressureDecay > 0)

	def test_ceiling_leaves_room_below_certainty(self):
		# the roll is rand(100) < iBaseChance + pressure, so a saturated neighbourhood must still
		# not be a guaranteed revolution every single check
		self.assert_(iBaseChance + iPressureCeiling < 100)

	def test_cooldown_is_longer_than_the_check_interval(self):
		# otherwise the same civilization could revolt on consecutive checks
		self.assert_(iCooldown > iCheckInterval)


class TestPreconditions(TestCase):

	def test_nothing_before_the_revolution_year(self):
		self.assertEqual(iRevolutionYear, 1789)

	def test_ancien_regime_membership(self):
		# a republic is not vulnerable; a monarchy is
		self.assert_(iRepublic not in lAncienRegime)
		self.assert_(iMonarchy in lAncienRegime)

	def test_vulnerable_stability_excludes_healthy_states(self):
		# only shaky or worse
		self.assert_(iVulnerableStability < iStabilityStable)


test_cases = [
	TestConstants,
	TestContagionIsBounded,
	TestPreconditions,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
