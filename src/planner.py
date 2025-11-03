"""Simple budget-based itinerary planner.

Given user inputs (budget, num_people, nights), produce a feasible itinerary that
selects transport, accommodation, and activities within budget. This is intentionally
heuristic and deterministic for the take-home prototype.
"""
from typing import Dict, Any, List, Optional, Tuple
from .data import TRANSPORT_OPTIONS, ACCOMMODATION_OPTIONS, ACTIVITIES
import logging

logger = logging.getLogger(__name__)


def choose_transport(budget_per_person: float) -> Dict[str, Any]:
    # Choose the cheapest transport that fits budget per person
    options = sorted(TRANSPORT_OPTIONS, key=lambda x: x["cost_per_person"])
    for opt in options:
        if opt["cost_per_person"] <= budget_per_person:
            return opt
    # fallback to cheapest
    return options[0]


def choose_accommodation(budget_per_night: float) -> Dict[str, Any]:
    options = sorted(ACCOMMODATION_OPTIONS, key=lambda x: x["cost_per_night"])
    for opt in options:
        if opt["cost_per_night"] <= budget_per_night:
            return opt
    return options[0]


def _get_upgrade_options(current: Dict[str, Any], pool: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """Return options in pool that are strictly better (more expensive) than current, sorted ascending."""
    return sorted([p for p in pool if p.get(key, 0) > current.get(key, 0)], key=lambda x: x.get(key, 0))


def choose_activities(remaining_budget: float, max_activities: int = 3, activity_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Choose activities considering budget, max count, and optionally preferred type."""
    # Filter by type if specified
    candidates = ACTIVITIES
    if activity_type:
        candidates = [a for a in candidates if a["type"] == activity_type]
    
    # Sort by score-to-cost ratio and absolute score
    candidates = sorted(candidates, key=lambda a: (-(a["score"] / (a["cost"] + 1)), -a["score"]))
    chosen = []
    total = 0
    
    for c in candidates:
        if len(chosen) >= max_activities:
            break
        if total + c["cost"] <= remaining_budget:
            chosen.append(c)
            total += c["cost"]
    
    return chosen


def plan_itinerary(budget: float, num_people: int = 1, nights: int = 2) -> Dict[str, Any]:
    """Return a dictionary with chosen transport, accommodation, activities and cost breakdown."""
    if budget <= 0 or num_people <= 0 or nights <= 0:
        raise ValueError("budget, num_people and nights must be positive")

    # Simple cost allocations (initial heuristic): 40% transport, 40% accommodation, 20% activities
    # But if that allocation yields infeasible plan, attempt cheaper combinations.
    def score_plan(transport: Dict[str, Any], accommodation: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        transport_cost = transport["cost_per_person"] * num_people
        accommodation_cost = accommodation["cost_per_night"] * nights
        remaining_for_activities = max(0, budget - (transport_cost + accommodation_cost))
        activities = choose_activities(remaining_for_activities, max_activities=3)
        activities_cost = sum(a["cost"] for a in activities)
        total_cost = transport_cost + accommodation_cost + activities_cost
        feasible = total_cost <= budget
        return feasible, {
            "transport": transport,
            "transport_cost": transport_cost,
            "accommodation": accommodation,
            "accommodation_cost": accommodation_cost,
            "activities": activities,
            "activities_cost": activities_cost,
            "total_cost": total_cost,
            "feasible": feasible,
        }

    # Initial picks based on heuristic pools
    transport_pool = budget * 0.4
    accommodation_pool = budget * 0.4
    budget_per_person_transport = transport_pool / num_people
    budget_per_night = accommodation_pool / nights
    transport_initial = choose_transport(budget_per_person_transport)
    accommodation_initial = choose_accommodation(budget_per_night)

    feasible, result = score_plan(transport_initial, accommodation_initial)
    if feasible:
        # If budget is generously larger than plan, try to upgrade transport/accommodation
        # without breaking budget. This prefers nicer options when budget allows.
        def try_upgrades(plan: Dict[str, Any]):
            current_t = plan["transport"]
            current_a = plan["accommodation"]
            # compute available headroom
            headroom = budget - plan["total_cost"]
            upgraded = False

            # Try upgrading accommodation first (comfort)
            accom_upgrades = _get_upgrade_options(current_a, ACCOMMODATION_OPTIONS, "cost_per_night")
            for a in accom_upgrades:
                extra = (a["cost_per_night"] - current_a["cost_per_night"]) * nights
                if extra <= headroom:
                    # attempt new plan with upgraded accommodation
                    feasible2, attempt2 = score_plan(current_t, a)
                    if feasible2 and attempt2["total_cost"] <= budget:
                        plan = attempt2
                        headroom = budget - plan["total_cost"]
                        current_a = a
                        upgraded = True
                        break

            # Then try upgrading transport
            transport_upgrades = _get_upgrade_options(current_t, TRANSPORT_OPTIONS, "cost_per_person")
            for t in transport_upgrades:
                extra = (t["cost_per_person"] - current_t["cost_per_person"]) * num_people
                if extra <= headroom:
                    feasible2, attempt2 = score_plan(t, current_a)
                    if feasible2 and attempt2["total_cost"] <= budget:
                        plan = attempt2
                        upgraded = True
                        break

            return plan, upgraded

        upgraded_plan, upgraded = try_upgrades(result)
        if upgraded:
            result = upgraded_plan

        # attach input meta
        result.update({"budget": budget, "num_people": num_people, "nights": nights})
        logger.info("Planned itinerary feasible: total_cost=%s", result.get("total_cost"))
        return result

    # If not feasible, try cheaper combinations (brute force over sorted options)
    transports_sorted = sorted(TRANSPORT_OPTIONS, key=lambda x: x["cost_per_person"])
    accom_sorted = sorted(ACCOMMODATION_OPTIONS, key=lambda x: x["cost_per_night"])

    best_attempt: Optional[Dict[str, Any]] = None
    for t in transports_sorted:
        for a in accom_sorted:
            feasible, attempt = score_plan(t, a)
            # prefer feasible plans; if none feasible, keep the lowest cost attempt
            if feasible:
                logger.info("Found feasible combination by search: transport=%s accommodation=%s total=%s", t.get('id'), a.get('id'), attempt.get('total_cost'))
                attempt.update({"budget": budget, "num_people": num_people, "nights": nights})
                return attempt
            if best_attempt is None or attempt["total_cost"] < best_attempt["total_cost"]:
                best_attempt = attempt

    # if nothing feasible, return the best attempt (least total cost) with feasible=False
    if best_attempt is not None:
        logger.info("No feasible plan found; returning best attempt with total_cost=%s", best_attempt.get('total_cost'))
        best_attempt.update({"budget": budget, "num_people": num_people, "nights": nights})
        return best_attempt

    # fallback (shouldn't happen)
    raise RuntimeError("Unable to construct any plan")


if __name__ == "__main__":
    import json
    example = plan_itinerary(25000, num_people=2, nights=3)
    print(json.dumps(example, indent=2))
