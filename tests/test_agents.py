import unittest
from src.agents import MessageBus, ItineraryAgent
from src.planner import plan_itinerary
from src.replanner import replan_for_flight_delay


class AgentsTests(unittest.TestCase):
    def test_message_bus_and_itinerary_agent(self):
        bus = MessageBus()
        it_agent = ItineraryAgent(bus, planner_callable=plan_itinerary, replanner_callable=replan_for_flight_delay)
        # create a plan
        plan = it_agent.create_plan(budget=18000, people=1, nights=2)
        self.assertIsNotNone(plan)

        received = {}

        def on_update(msg):
            received['plan'] = msg.get('plan')

        bus.subscribe('plan_update', on_update)

        # publish a flight delay event
        bus.publish('flight_delay', {'delay_hours': 6})

        # callback should have been invoked and received updated plan
        self.assertIn('plan', received)
        self.assertIsInstance(received['plan'], dict)

    def test_weather_triggers_activity_swaps(self):
        bus = MessageBus()
        # set replacement_score_delta low to require closer match
        it_agent = ItineraryAgent(bus, planner_callable=plan_itinerary, replanner_callable=replan_for_flight_delay, replacement_score_delta=0, replacement_cost_weight=1.0)
        plan = it_agent.create_plan(budget=20000, people=1, nights=2)
        # ensure there is at least one outdoor activity to be swapped
        has_outdoor = any(a.get('type') == 'outdoor' for a in plan.get('activities', []))
        if not has_outdoor:
            # if none, force-add one outdoor activity for the test
            plan['activities'].append({'id': 'beach_visit', 'type': 'outdoor', 'cost': 0, 'score': 5})

        updates = {}

        def on_update(msg):
            updates['plan'] = msg.get('plan')

        bus.subscribe('plan_update', on_update)
        # publish heavy weather
        bus.publish('weather', {'severity': 'heavy'})
        self.assertIn('plan', updates)
        new_plan = updates['plan']
        # new_plan should include recommendation about weather and activities changed
        self.assertIn('recommendation', new_plan)
        self.assertTrue(any(a.get('status') in ('swapped_due_to_weather', 'postponed_due_to_weather') for a in new_plan.get('activities', [])))

    def test_budget_update_triggers_replan(self):
        bus = MessageBus()
        it_agent = ItineraryAgent(bus, planner_callable=plan_itinerary, replanner_callable=replan_for_flight_delay)
        initial = it_agent.create_plan(budget=15000, people=1, nights=2)
        updates = {}

        def on_update(msg):
            updates['plan'] = msg.get('plan')

        bus.subscribe('plan_update', on_update)
        # increase budget
        bus.publish('budget', {'budget': 28000})
        self.assertIn('plan', updates)
        new_plan = updates['plan']
        self.assertIn('recommendation', new_plan)
        self.assertIn('budget', new_plan)


if __name__ == '__main__':
    unittest.main()
