"""Run planner for multiple budgets and print results.

Usage:
  python src/run_budgets.py              # runs default budgets
  python src/run_budgets.py 5000 15000   # run with custom budgets
  python src/run_budgets.py --csv out.csv 5000 10000
"""
import argparse
import csv
import json
import sys
from typing import List

from src.planner import plan_itinerary


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Run planner for multiple budgets")
    p.add_argument("budgets", nargs="*", type=int, help="Budgets to run (integers)")
    p.add_argument("--csv", dest="csvfile", help="Optional CSV output file")
    return p.parse_args(argv)


def budgets_from_args(args) -> List[int]:
    if args.budgets:
        return args.budgets
    return [5000, 10000, 18000, 30000]


def main(argv: List[str]):
    args = parse_args(argv)
    budgets = budgets_from_args(args)
    rows = []

    for b in budgets:
        plan = plan_itinerary(b, num_people=1, nights=2)
        print("BUDGET:", b)
        print(json.dumps(plan, indent=2))
        print("-" * 60)
        rows.append({
            "budget": b,
            "total_cost": plan.get("total_cost"),
            "feasible": plan.get("feasible"),
            "transport": plan.get("transport", {}).get("id"),
            "accommodation": plan.get("accommodation", {}).get("id"),
            "activities": ";".join(a.get("id") for a in plan.get("activities", [])),
        })

    if args.csvfile:
        with open(args.csvfile, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["budget", "total_cost", "feasible", "transport", "accommodation", "activities"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        print(f"Wrote CSV to {args.csvfile}")


if __name__ == "__main__":
    main(sys.argv[1:])
