"""Simple message bus and agents for multi-agent simulation.

This module provides a minimal publish/subscribe MessageBus and a few example
agents: WeatherAgent, EventAgent, BudgetAgent, and ItineraryAgent. The
ItineraryAgent listens for 'flight_delay' events and triggers replanning.
"""
from typing import Callable, Dict, Any, List
from threading import Thread
import time
from src.data import ACTIVITIES
import logging

logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        self.subscribers.setdefault(topic, []).append(callback)

    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        for cb in self.subscribers.get(topic, []):
            try:
                cb(message)
            except Exception:
                # swallow exceptions from callbacks in this simple demo
                pass


class WeatherAgent:
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def publish_weather(self, severity: str):
        self.bus.publish("weather", {"severity": severity})


class EventAgent:
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def publish_event(self, name: str, info: Dict[str, Any] = None):
        self.bus.publish("event", {"name": name, "info": info or {}})


class BudgetAgent:
    def __init__(self, bus: MessageBus):
        self.bus = bus

    def update_budget(self, budget: float):
        self.bus.publish("budget", {"budget": budget})


class ItineraryAgent:
    def __init__(self, bus: MessageBus, planner_callable, replanner_callable, *, replacement_score_delta: int = 1, replacement_cost_weight: float = 1.0):
        self.bus = bus
        self.planner = planner_callable
        self.replanner = replanner_callable
        self.current_plan = None
        # tuning parameters for activity replacement (weather-driven)
        # replacement_score_delta: allow replacements whose score >= outdoor_score - delta
        # replacement_cost_weight: weight applied to activity cost when computing ratio
        self.replacement_score_delta = replacement_score_delta
        self.replacement_cost_weight = replacement_cost_weight
        # subscribe to relevant topics
        bus.subscribe("event", self._on_event)
        bus.subscribe("flight_delay", self._on_flight_delay)
        bus.subscribe("weather", self._on_weather)
        bus.subscribe("budget", self._on_budget_update)

    def create_plan(self, budget: float, people: int = 1, nights: int = 2):
        self.current_plan = self.planner(budget, num_people=people, nights=nights)
        logger.info("ItineraryAgent created initial plan: budget=%s people=%s nights=%s total_cost=%s", budget, people, nights, self.current_plan.get("total_cost"))
        return self.current_plan

    def _on_event(self, message: Dict[str, Any]):
        # handle higher-level events like peak season
        name = message.get("name")
        if name == "peak_season":
            # annotate recommendation and suggest early booking
            if self.current_plan is not None:
                self.current_plan["recommendation"] = "Peak season detected: recommend early booking and price monitoring"
                self.bus.publish("plan_update", {"plan": self.current_plan})
        # other events may be handled here

    def _on_flight_delay(self, message: Dict[str, Any]):
        delay = message.get("delay_hours", 0)
        if self.current_plan is None:
            return
        logger.info("Received flight_delay event: %sh", delay)
        # run replanner and publish the result
        new_plan = self.replanner(self.current_plan, delay)
        logger.info("Replanner returned: feasible=%s total_cost=%s", new_plan.get("feasible"), new_plan.get("total_cost"))
        self.current_plan = new_plan
        self.bus.publish("plan_update", {"plan": new_plan})

    def _on_weather(self, message: Dict[str, Any]):
        # simple policy: if heavy weather, replace outdoor activities with indoor ones
        severity = message.get("severity", "normal")
        if self.current_plan is None:
            return
        if severity in ("heavy", "severe"):
            activities = list(self.current_plan.get("activities", []))
            # find indoor candidates from ACTIVITIES
            indoor_candidates = [a for a in ACTIVITIES if a.get("type") == "indoor"]
            # scoring: prefer indoor candidates with highest score-to-cost ratio (score/(cost+1))
            # scoring: prefer indoor candidates with highest score-to-cost ratio
            # apply replacement_cost_weight to control sensitivity to cost
            indoor_candidates_sorted = sorted(
                indoor_candidates,
                key=lambda x: (-(x.get("score", 0) / (self.replacement_cost_weight * x.get("cost", 0) + 1)), -x.get("score", 0)),
            )
            replaced = False
            new_activities = []
            used_ids = {a.get("id") for a in activities}
            # For each outdoor activity, try to pick the best available indoor candidate by ratio
            for a in activities:
                if a.get("type") == "outdoor":
                    replacement = None
                    for ic in indoor_candidates_sorted:
                        if ic.get("id") not in used_ids:
                            # similarity heuristic: prefer replacements with score >= outdoor_score - delta
                            if ic.get("score", 0) >= a.get("score", 0) - self.replacement_score_delta:
                                replacement = dict(ic)
                                used_ids.add(ic.get("id"))
                                break
                    if replacement:
                        replacement["status"] = "swapped_due_to_weather"
                        new_activities.append(replacement)
                        replaced = True
                    else:
                        # no suitable replacement available, mark as postponed
                        a2 = dict(a)
                        a2["status"] = "postponed_due_to_weather"
                        new_activities.append(a2)
                else:
                    new_activities.append(a)

            if replaced:
                self.current_plan["activities"] = new_activities
                self.current_plan["activities_cost"] = sum(x.get("cost", 0) for x in new_activities)
                # recalc total cost
                self.current_plan["total_cost"] = (
                    self.current_plan.get("transport_cost", 0)
                    + self.current_plan.get("accommodation_cost", 0)
                    + self.current_plan.get("activities_cost", 0)
                )
                self.current_plan["recommendation"] = "Weather alert: swapped outdoor activities to indoor alternatives (scored replacements)"
                logger.info("Weather alert: replaced outdoor activities, new total_cost=%s", self.current_plan["total_cost"])
                self.bus.publish("plan_update", {"plan": self.current_plan})

    def _on_budget_update(self, message: Dict[str, Any]):
        # When budget changes, re-run planner with new budget and publish update
        new_budget = message.get("budget")
        if new_budget is None:
            return
        # preserve people and nights if available
        people = self.current_plan.get("num_people", 1) if self.current_plan else 1
        nights = self.current_plan.get("nights", 2) if self.current_plan else 2
        new_plan = self.planner(new_budget, num_people=people, nights=nights)
        new_plan["recommendation"] = f"Budget updated to {new_budget}: replanned accordingly"
        self.current_plan = new_plan
        self.bus.publish("plan_update", {"plan": new_plan})

