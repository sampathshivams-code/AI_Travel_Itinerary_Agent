import unittest
from src.planner import plan_itinerary


class PlannerTests(unittest.TestCase):
    def test_basic_feasible(self):
        plan = plan_itinerary(25000, num_people=1, nights=2)
        self.assertTrue(plan["feasible"])
        self.assertLessEqual(plan["total_cost"], 25000)

    def test_insufficient_budget(self):
        plan = plan_itinerary(1000, num_people=1, nights=2)
        self.assertFalse(plan["feasible"])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            plan_itinerary(0, num_people=1, nights=1)

    def test_multi_person_split(self):
        # two people sharing; budget should cover reasonable options
        plan = plan_itinerary(30000, num_people=2, nights=2)
        # planner should return a dict and non-negative costs
        self.assertIn("total_cost", plan)
        self.assertGreaterEqual(plan["total_cost"], 0)

    def test_low_budget_best_attempt(self):
        # extremely low budget should return feasible=False but still a best attempt
        plan = plan_itinerary(1000, num_people=1, nights=1)
        self.assertIn("feasible", plan)
        self.assertFalse(plan["feasible"]) 


if __name__ == "__main__":
    unittest.main()
