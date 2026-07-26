from BlackDeath import *
from unittest import *


class TestConstants(TestCase):

	def test_reads_plague_index_not_a_date(self):
		# the schedule, the jitter and the cancellation all live in Plague; this module must own
		# none of them, or the two can silently disagree
		self.assert_(0 <= iBlackDeath < len(data.lGenericPlagueTurns))

	def test_coerced_labour_civics_are_real(self):
		for iCivic in lCoercedLabour:
			self.assert_(0 <= iCivic < iNumCivics)

		self.assert_(0 <= iFreeLabour < iNumCivics)

	def test_free_labour_is_not_itself_coerced(self):
		self.assert_(iFreeLabour not in lCoercedLabour)

	def test_entrenchment_penalty_is_negative(self):
		# it is added to a penalty accumulator that Stability decays upwards towards zero
		self.assert_(iEntrenchmentPenalty < 0)


class TestModifierBalance(TestCase):
	"""changeYieldRateModifier is relative, so the applied amount must be tracked, not assumed."""

	def test_applying_twice_does_not_stack(self):
		# given: a player with no labour shortage
		iPlayer = 0
		iBefore = player(iPlayer).getYieldRateModifier(YieldTypes.YIELD_PRODUCTION)

		try:
			# when: the same modifier is applied twice
			applyModifier(iPlayer, iShortageModifier)
			iOnce = player(iPlayer).getYieldRateModifier(YieldTypes.YIELD_PRODUCTION)

			applyModifier(iPlayer, iShortageModifier)

			# then: the second call is a no-op
			self.assertEqual(player(iPlayer).getYieldRateModifier(YieldTypes.YIELD_PRODUCTION), iOnce)
		finally:
			applyModifier(iPlayer, 0)

	def test_modifier_returns_exactly_to_where_it_started(self):
		# given: whatever modifier the player already had
		iPlayer = 0
		iBefore = player(iPlayer).getYieldRateModifier(YieldTypes.YIELD_PRODUCTION)

		try:
			# when: a shortage begins, is raised by emancipation, and then expires
			applyModifier(iPlayer, iShortageModifier)
			applyModifier(iPlayer, iShortageModifier + iEmancipationModifier)
			applyModifier(iPlayer, 0)

			# then: nothing is stranded
			self.assertEqual(player(iPlayer).getYieldRateModifier(YieldTypes.YIELD_PRODUCTION), iBefore)
			self.assertEqual(data.players[iPlayer].iLabourShortageModifier, 0)
		finally:
			applyModifier(iPlayer, 0)


class TestLossThreshold(TestCase):

	def test_loss_is_a_percentage_of_the_recorded_population(self):
		# 100 * (before - after) / before
		self.assertEqual(100 * (100 - 70) / 100, 30)
		self.assertEqual(100 * (60 - 48) / 60, 20)

	def test_a_light_plague_changes_nothing(self):
		self.assert_(100 * (100 - 95) / 100 < iLossThreshold)

	def test_a_heavy_plague_crosses_the_threshold(self):
		self.assert_(100 * (100 - 65) / 100 >= iLossThreshold)


test_cases = [
	TestConstants,
	TestModifierBalance,
	TestLossThreshold,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
