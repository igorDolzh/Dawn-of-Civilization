from FutureRules import *
from unittest import *


class TestModifierRules(TestCase):
	"""apply() writes absolute values, so every rule must be idempotent."""

	def test_rule_sets_absolute_value(self):
		# given: a player with the default distance maintenance modifier
		iPlayer = 0
		iBefore = player(iPlayer).getModifier(iModifierDistanceMaintenance)

		try:
			# when: the rule is applied
			apply(iPlayer, iNeuralUplink)

			# then: distance no longer costs anything
			self.assertEqual(player(iPlayer).getModifier(iModifierDistanceMaintenance), 0)
			self.assertEqual(player(iPlayer).getModifier(iModifierColonyMaintenance), 0)
		finally:
			setModifier(iPlayer, iModifierDistanceMaintenance, iBefore)

	def test_applying_twice_does_not_stack(self):
		# given: a player who has already received the rule
		iPlayer = 0
		iBefore = player(iPlayer).getModifier(iModifierBuildingCost)

		try:
			apply(iPlayer, iNanoassembly)
			iOnce = player(iPlayer).getModifier(iModifierBuildingCost)

			# when: it fires again, as it would on load
			apply(iPlayer, iNanoassembly)

			# then: the value is unchanged, not compounded
			self.assertEqual(player(iPlayer).getModifier(iModifierBuildingCost), iOnce)
		finally:
			setModifier(iPlayer, iModifierBuildingCost, iBefore)

	def test_unknown_tech_changes_nothing(self):
		# given: a technology with no rule attached
		iPlayer = 0
		iBefore = player(iPlayer).getModifier(iModifierResearchCost)

		# when: it is applied
		apply(iPlayer, iPottery)

		# then: nothing happens
		self.assertEqual(player(iPlayer).getModifier(iModifierResearchCost), iBefore)

	def test_every_rule_names_a_real_modifier(self):
		# guards against a typo silently doing nothing
		for iTech, rules in dModifierRules.items():
			for iModifier, iValue in rules:
				self.assert_(0 <= iModifier < iNumModifiers)
				self.assert_(iValue >= 0)


class TestPlagueImmunity(TestCase):

	def test_synthetic_genomics_ends_plague(self):
		# given: a player currently able to catch plague
		iPlayer = 0
		iBefore = data.players[iPlayer].iPlagueCountdown

		try:
			# when: they discover synthetic genomics
			apply(iPlayer, iSyntheticGenomics)

			# then: the countdown is pushed far enough back that it never returns
			self.assert_(data.players[iPlayer].iPlagueCountdown < 0)
		finally:
			data.players[iPlayer].iPlagueCountdown = iBefore


test_cases = [
	TestModifierRules,
	TestPlagueImmunity,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
