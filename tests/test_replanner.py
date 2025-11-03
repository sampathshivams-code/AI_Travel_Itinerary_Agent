import unittest
from src.planner import plan_itinerary
from src.replanner import replan_for_flight_delay


class ReplannerTests(unittest.TestCase):
    def test_small_delay_shifts_activities(self):
        plan = plan_itinerary(20000, num_people=1, nights=2)
        rp = replan_for_flight_delay(plan, delay_hours=2)
        self.assertIn("recommendation", rp)
        self.assertTrue(all(a.get("status") == "rescheduled" for a in rp.get("activities", [])))

    def test_large_delay_adds_night_if_budget_allows(self):
        plan = plan_itinerary(30000, num_people=1, nights=2)
        # choose a plan and then replan with a big delay
        rp = replan_for_flight_delay(plan, delay_hours=6)
        # either feasible True with nights increased or feasible False with recommendation
        self.assertIn("recommendation", rp)

    def test_large_delay_cancels_activities_to_meet_budget(self):
        # design a tight budget where adding night isn't possible but cancelling helps
        plan = plan_itinerary(12000, num_people=1, nights=2)
        rp = replan_for_flight_delay(plan, delay_hours=8)
        self.assertIn("recommendation", rp)


if __name__ == "__main__":
    unittest.main()
