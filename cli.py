"""Command-line runner for the budget-based itinerary planner.

Supports running the replanner on the generated plan via `--delay`.
"""
from src.planner import plan_itinerary
from src.replanner import replan_for_flight_delay
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser(description="Budget-based Itinerary Planner")
    p.add_argument("--budget", type=float, required=True, help="Total budget (INR)")
    p.add_argument("--people", type=int, default=1, help="Number of people")
    p.add_argument("--nights", type=int, default=2, help="Number of nights")
    p.add_argument("--delay", type=float, default=None, help="Simulate a flight delay (hours) and run replanner")
    p.add_argument("--demo", action="store_true", help="Run the replanning demo after planning")
    p.add_argument("--replacement-score-delta", type=int, default=1, help="Delta allowed when matching replacement activity score (default 1)")
    p.add_argument("--replacement-cost-weight", type=float, default=1.0, help="Weight applied to activity cost when scoring replacements (default 1.0)")
    args = p.parse_args()

    # configure logging for CLI/demo runs
    try:
        from src.logging_config import configure_logging

        configure_logging()
    except Exception:
        pass

    plan = plan_itinerary(args.budget, num_people=args.people, nights=args.nights)
    print("Generated plan:")
    print(json.dumps(plan, indent=2))

    if args.delay is not None:
        try:
            delay_hours = float(args.delay)
        except Exception:
            print("Invalid --delay value", file=sys.stderr)
            sys.exit(2)
        replanned = replan_for_flight_delay(plan, delay_hours=delay_hours)
        print("\nReplanned (after delay=", delay_hours, "hours):")
        print(json.dumps(replanned, indent=2))

    if args.demo:
        # lazy import to avoid coupling when not used
        from src.agent_demo import run_demo

        print("\nRunning demo...\n")
        run_demo(replacement_score_delta=args.replacement_score_delta, replacement_cost_weight=args.replacement_cost_weight)


if __name__ == "__main__":
    main()
