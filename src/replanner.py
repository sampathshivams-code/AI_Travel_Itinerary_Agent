"""Dynamic re-planning logic for the itinerary when runtime events occur.

This module implements a small, deterministic replanner that accepts an existing
plan (from `planner.plan_itinerary`) and an event (e.g., flight delay) and
produces an adjusted plan. The replanner is intentionally simple:

- If flight is delayed and delay <= 3 hours: shift activities where possible.
- If delay > 3 hours: try to add an extra night (if budget allows).
- If adding a night would exceed the budget, cancel low value paid activities
  until the plan fits the original budget.
- If plan still doesn't fit, return an adjusted plan with `feasible=False` and
  a `recommendation` string (e.g., "consider rescheduling trip").

This demonstrates dynamic re-planning behavior for the advanced use case.
"""
from typing import Dict, Any, List
from src.data import TRANSPORT_OPTIONS


def replan_for_flight_delay(plan: Dict[str, Any], delay_hours: float) -> Dict[str, Any]:
    """Return an adjusted plan given a flight delay in hours.

    The input `plan` is expected to be the output of `planner.plan_itinerary`.
    The returned dict contains updated costs and feasibility.
    """
    # shallow copy metadata
    new_plan = dict(plan)

    # no change if already infeasible
    if not plan.get("feasible", True):
        new_plan["recommendation"] = "original plan already infeasible"
        return new_plan

    # Case 1: small delay => shift activities within available time (no cost change)
    if delay_hours <= 3:
        new_plan["recommendation"] = f"Delay {delay_hours}h: shift activities where possible; no cost change"
        # we simulate shifting by marking activities as 'rescheduled'
        new_activities = []
        for a in plan.get("activities", []):
            a2 = dict(a)
            a2["status"] = "rescheduled"
            new_activities.append(a2)
        new_plan["activities"] = new_activities
        return new_plan

    # Case 2: larger delay => try to add one extra night
    nights = new_plan.get("nights", 1)
    accommodation = new_plan.get("accommodation", {})
    acost_per_night = accommodation.get("cost_per_night", 0)

    extra_night_cost = acost_per_night
    budget = new_plan.get("budget", 0)
    total_cost = new_plan.get("total_cost", 0)

    # If we can afford to add a night staying within budget, do it
    if total_cost + extra_night_cost <= budget:
        new_plan["nights"] = nights + 1
        new_plan["accommodation_cost"] = new_plan.get("accommodation_cost", 0) + extra_night_cost
        new_plan["total_cost"] = total_cost + extra_night_cost
        new_plan["feasible"] = True
        new_plan["recommendation"] = f"Delay {delay_hours}h: added 1 extra night to accommodate delay"
        return new_plan

    # Otherwise, attempt to cancel paid activities (lowest score-to-cost first)
    activities = list(plan.get("activities", []))
    # compute score-to-cost ratio; treat zero-cost activities as high priority (don't cancel)
    cancellable = [a for a in activities if a.get("cost", 0) > 0]
    cancellable_sorted = sorted(cancellable, key=lambda a: (a.get("cost", 0) / (a.get("score", 1) + 0.1)), reverse=True)

    removed = []
    running_total = total_cost
    for a in cancellable_sorted:
        if running_total <= budget:
            break
        running_total -= a.get("cost", 0)
        removed.append(a)

    if running_total <= budget:
        # produce new activities list excluding removed ones
        remaining = [a for a in activities if a not in removed]
        new_plan["activities"] = remaining
        new_plan["activities_cost"] = sum(a.get("cost", 0) for a in remaining)
        new_plan["total_cost"] = running_total
        new_plan["feasible"] = True
        new_plan["recommendation"] = (
            f"Delay {delay_hours}h: cancelled {len(removed)} paid activities to meet budget"
        )
        return new_plan

    # Still not feasible: return best-effort (removed all paid activities) and recommend reschedule
    remaining = [a for a in activities if a.get("cost", 0) == 0]
    new_plan["activities"] = remaining
    new_plan["activities_cost"] = sum(a.get("cost", 0) for a in remaining)
    new_plan["total_cost"] = sum([
        new_plan.get("transport_cost", 0),
        new_plan.get("accommodation_cost", 0),
        new_plan.get("activities_cost", 0),
    ])
    new_plan["feasible"] = False
    new_plan["recommendation"] = (
        f"Delay {delay_hours}h: cannot satisfy budget; recommend rescheduling or increasing budget"
    )
    # As a last attempt, try switching to faster transport options (if any) to avoid multi-night add
    # Find current transport and look for faster options with shorter duration; prefer ones that
    # reduce duration and still can bring total cost <= budget (after optionally cancelling activities)
    current_transport = plan.get("transport", {})
    current_duration = current_transport.get("duration_hours", None)

    if current_duration is not None:
        # candidate transports sorted by duration ascending (faster first)
        faster_candidates = [t for t in TRANSPORT_OPTIONS if t.get("duration_hours", 0) < current_duration]
        faster_candidates = sorted(faster_candidates, key=lambda t: t.get("duration_hours", 0))
        for t in faster_candidates:
            # recalc costs with this transport
            transport_cost = t.get("cost_per_person", 0) * new_plan.get("num_people", 1)
            # keep accommodation and activities as in original plan
            accommodation_cost = new_plan.get("accommodation_cost", 0)
            activities_cost = new_plan.get("activities_cost", 0)
            total_with_switch = transport_cost + accommodation_cost + activities_cost
            if total_with_switch <= budget:
                new_plan["transport"] = t
                new_plan["transport_cost"] = transport_cost
                new_plan["total_cost"] = total_with_switch
                new_plan["feasible"] = True
                new_plan["recommendation"] = (
                    f"Delay {delay_hours}h: switched to faster transport '{t.get('id')}' to avoid further disruption"
                )
                return new_plan

    return new_plan


if __name__ == "__main__":
    # small demo when run directly
    from src.planner import plan_itinerary
    import json

    p = plan_itinerary(25000, num_people=1, nights=2)
    print("Original plan:\n", json.dumps(p, indent=2))
    rp = replan_for_flight_delay(p, delay_hours=5)
    print("Replanned:\n", json.dumps(rp, indent=2))
