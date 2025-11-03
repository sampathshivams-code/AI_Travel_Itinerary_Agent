"""Small demo script to create a plan and run a replanning event."""
from src.planner import plan_itinerary
from src.replanner import replan_for_flight_delay
import json


def demo():
    plan = plan_itinerary(18000, num_people=1, nights=2)
    print("Original plan:\n", json.dumps(plan, indent=2))
    print("\nSimulating a 5-hour flight delay...\n")
    rp = replan_for_flight_delay(plan, delay_hours=5)
    print("Replanned:\n", json.dumps(rp, indent=2))


if __name__ == "__main__":
    demo()
