from Migration import *
from unittest import *


# far enough apart to be distinct, close enough to be within iMaxMigrationDistance
tSourceLocation = (57, 35)
tTargetLocation = (59, 35)


class TestEmigrationValue(TestCase):
	"""getEmigrationValue is a pure function of a city, so it can be tested directly.

	The scoring adds rand(0, 2) of jitter once the value is positive, so assertions
	either target the deterministic early returns or use bounds rather than equality.
	"""

	def test_small_city_never_emigrates(self):
		# given: a city at or below the minimum size
		city = player(0).initCity(*tSourceLocation)
		city.setPopulation(iMinSourcePopulation)

		try:
			# then: it is disqualified outright, with no jitter applied
			self.assertEqual(getEmigrationValue(city), 0)
		finally:
			city.kill()

	def test_content_city_does_not_push(self):
		# given: a reasonably sized city with no active push factor
		city = player(0).initCity(*tSourceLocation)
		city.setPopulation(6)

		try:
			# then: it stays below the threshold at which anyone leaves
			self.assertTrue(getEmigrationValue(city) < iMinEmigrationValue)
		finally:
			city.kill()

	def test_plague_increases_pressure(self):
		# given: the same city with and without plague
		city = player(0).initCity(*tSourceLocation)
		city.setPopulation(6)

		try:
			iBefore = getEmigrationValue(city)
			city.setHasRealBuilding(iPlague, True)
			iAfter = getEmigrationValue(city)

			# then: plague pushes the score up by more than the jitter range
			self.assertTrue(iAfter > iBefore)
		finally:
			city.setHasRealBuilding(iPlague, False)
			city.kill()

	def test_occupation_increases_pressure(self):
		# given: the same city with and without an occupation timer
		city = player(0).initCity(*tSourceLocation)
		city.setPopulation(6)

		try:
			iBefore = getEmigrationValue(city)
			city.setOccupationTimer(5)
			iAfter = getEmigrationValue(city)

			# then: occupied cities are worse places to live
			self.assertTrue(iAfter > iBefore)
		finally:
			city.setOccupationTimer(0)
			city.kill()


class TestImmigrationValue(TestCase):

	def test_plagued_city_attracts_nobody(self):
		# given: an otherwise fine city that is plagued
		city = player(0).initCity(*tTargetLocation)
		city.setPopulation(6)
		city.setHasRealBuilding(iPlague, True)

		try:
			# then: it is disqualified outright
			self.assertEqual(getImmigrationValue(city), 0)
		finally:
			city.setHasRealBuilding(iPlague, False)
			city.kill()

	def test_occupied_city_attracts_nobody(self):
		# given: a city under occupation
		city = player(0).initCity(*tTargetLocation)
		city.setPopulation(6)
		city.setOccupationTimer(5)

		try:
			# then: it is disqualified outright
			self.assertEqual(getImmigrationValue(city), 0)
		finally:
			city.setOccupationTimer(0)
			city.kill()

	def test_value_is_never_negative(self):
		# given: any city
		city = player(0).initCity(*tTargetLocation)
		city.setPopulation(4)

		try:
			# then: the pull score is used in comparisons and must not go below zero
			self.assertTrue(getImmigrationValue(city) >= 0)
		finally:
			city.kill()


class TestMigrate(TestCase):

	def test_transfer_is_one_to_one(self):
		# given: two cities of the same owner
		sourceCity = player(0).initCity(*tSourceLocation)
		targetCity = player(0).initCity(*tTargetLocation)
		sourceCity.setPopulation(8)
		targetCity.setPopulation(4)

		try:
			# when: one migration happens
			migrate(sourceCity, targetCity)

			# then: exactly one population point moved, and the total is conserved
			self.assertEqual(sourceCity.getPopulation(), 7)
			self.assertEqual(targetCity.getPopulation(), 5)
		finally:
			sourceCity.kill()
			targetCity.kill()

	def test_shrinking_does_not_create_population(self):
		# given: a city whose food box is nearly full
		city = player(0).initCity(*tSourceLocation)
		city.setPopulation(10)
		city.setFood(city.growthThreshold() - 1)

		try:
			# when: it loses a population point to emigration
			shrink(city)

			# then: the food box is rescaled below the new, lower growth threshold, so the
			# city does not immediately grow back and manufacture population from nothing
			self.assertEqual(city.getPopulation(), 9)
			self.assertTrue(city.getFood() < city.growthThreshold())
		finally:
			city.kill()

	def test_destination_must_be_clearly_better(self):
		# given: two equally attractive cities
		sourceCity = player(0).initCity(*tSourceLocation)
		targetCity = player(0).initCity(*tTargetLocation)
		sourceCity.setPopulation(6)
		targetCity.setPopulation(6)

		try:
			candidates = players.major().existing().cities()
			dImmigration = dict((location(c), getImmigrationValue(c)) for c in candidates)

			# when: looking for somewhere better to go
			destination = findDestination(sourceCity, candidates, dImmigration, [])

			# then: nobody moves, so population cannot oscillate between the two
			self.assertEqual(destination, None)
		finally:
			sourceCity.kill()
			targetCity.kill()

	def test_source_is_excluded_as_destination(self):
		# given: a single city, which is both the origin and the only candidate
		sourceCity = player(0).initCity(*tSourceLocation)
		sourceCity.setPopulation(6)

		try:
			candidates = players.major().existing().cities()
			dImmigration = dict((location(c), getImmigrationValue(c)) for c in candidates)

			# when: looking for a destination
			destination = findDestination(sourceCity, candidates, dImmigration, [])

			# then: a city is never its own destination
			self.assertEqual(destination, None)
		finally:
			sourceCity.kill()


test_cases = [
	TestEmigrationValue,
	TestImmigrationValue,
	TestMigrate,
]

suite = TestSuite([makeSuite(case) for case in test_cases])
TextTestRunner(verbosity=2).run(suite)
