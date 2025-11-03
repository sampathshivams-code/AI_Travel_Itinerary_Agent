"""Demo that runs a small multi-agent simulation and shows the itinerary agent reacting to events."""
from src.agents import MessageBus, EventAgent, ItineraryAgent, WeatherAgent
from src.planner import plan_itinerary
from src.replanner import replan_for_flight_delay
import time
import json


def run_demo(replacement_score_delta: int = 1, replacement_cost_weight: float = 1.0):
    bus = MessageBus()
    event_agent = EventAgent(bus)
    weather_agent = WeatherAgent(bus)
    itinerary_agent = ItineraryAgent(
        bus,
        planner_callable=plan_itinerary,
        replanner_callable=replan_for_flight_delay,
        replacement_score_delta=replacement_score_delta,
        replacement_cost_weight=replacement_cost_weight,
    )

    # create initial plan
    plan = itinerary_agent.create_plan(budget=18000, people=1, nights=2)
    print("Initial plan:\n", json.dumps(plan, indent=2))

    # subscribe to plan updates
    def on_update(msg):
        print("\n[Bus] Received plan update:")
        print(json.dumps(msg.get("plan"), indent=2))

    bus.subscribe("plan_update", on_update)

    # Simulate a weather event then a flight delay
    print("\nSimulating weather alert (heavy rain)...")
    weather_agent.publish_weather("heavy")
    time.sleep(0.5)

    print("\nSimulating peak season event...")
    event_agent.publish_event("peak_season")
    time.sleep(0.5)

    print("\nSimulating flight delay: 6 hours")
    bus.publish("flight_delay", {"delay_hours": 6})
    time.sleep(0.5)

    print("\nSimulating budget increase to allow upgrades...")
    bus.publish("budget", {"budget": 30000})
    time.sleep(0.5)


if __name__ == "__main__":
    run_demo()
