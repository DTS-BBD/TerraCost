import argparse
import sys
import re
from typing import List
from pydantic import BaseModel, Field

__version__ = "0.1.0"

# =====================
# Pydantic Models
# =====================

class ResourceCost(BaseModel):
    name: str
    monthly_cost: float = Field(ge=0, description="Cost per month in USD")

class CostEstimate(BaseModel):
    timeframe_months: float
    total_cost: float
    breakdown: List[ResourceCost]

# =====================
# Helper Functions
# =====================

def parse_timeframe(tf: str) -> float:
    """
    Parse timeframe string (Xd, Xm, Xy) into months (float).
    """
    match = re.match(r"(\d+)([dmy])", tf)
    if not match:
        raise ValueError(f"Invalid timeframe format: {tf}")

    value, unit = int(match.group(1)), match.group(2)

    if unit == "d":   # days → months (~30 days)
        return value / 30
    elif unit == "m": # months
        return value
    elif unit == "y": # years → months
        return value * 12
    else:
        raise ValueError(f"Invalid timeframe unit: {unit}")

def estimate_cost(months: float, verbose: bool) -> CostEstimate:
    """
    Dummy cost estimation (to be replaced with Terraform parsing + cloud pricing).
    """
    # Example hardcoded monthly costs
    costs = {
        "aws_instance.web_server": 95,
        "aws_s3_bucket.logs": 22,
        "aws_rds_instance.prod_db": 395,
    }

    breakdown = [ResourceCost(name=r, monthly_cost=c * months) for r, c in costs.items()]
    total = sum(rc.monthly_cost for rc in breakdown)

    estimate = CostEstimate(
        timeframe_months=months,
        total_cost=total,
        breakdown=breakdown
    )

    # Print to console
    print(f"\nEstimated Cost for {months:.1f} month(s): ${estimate.total_cost:.2f}\n")
    if verbose:
        print("Breakdown (per resource):")
        for rc in estimate.breakdown:
            print(f"- {rc.name:30} ${rc.monthly_cost:.2f}")

    return estimate

def suggest_cost_optimizations(months: float):
    """
    Dummy cost optimization suggestions (later: LLM or rule-based).
    """
    print(f"\nEstimated cost for {months:.1f} month(s): $4,200 (dummy)\n")
    print("Cost Optimization Suggestions:")
    print("- Consider using t3.medium instead of t2.large for web_server (saves ~$30/mo).")
    print("- Use S3 infrequent access for logs (saves ~50%).")
    print("- Reserved RDS instance could save ~35% long term.\n")

# =====================
# CLI Entrypoint
# =====================

def main():
    parser = argparse.ArgumentParser(
        prog="terracost",
        description="TerraCost - Terraform Cost Estimation Tool"
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Display version of TerraCost"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ---- plan ----
    plan_parser = subparsers.add_parser("plan", help="Estimate Terraform plan cost")
    plan_parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed breakdown per resource"
    )
    plan_parser.add_argument(
        "-t", "--timeframe", type=str, default="1m",
        help="Timeframe for cost estimation (Xd, Xm, Xy). Default: 1m"
    )

    # ---- suggest ----
    suggest_parser = subparsers.add_parser("suggest", help="Suggest cost optimizations")
    suggest_parser.add_argument(
        "-t", "--timeframe", type=str, default="1m",
        help="Timeframe for cost estimation (Xd, Xm, Xy). Default: 1m"
    )

    args = parser.parse_args()

    # ---- handle version ----
    if args.version and not args.command:
        print(f"TerraCost v{__version__}")
        sys.exit(0)

    # ---- plan ----
    if args.command == "plan":
        months = parse_timeframe(args.timeframe)
        estimate_cost(months=months, verbose=args.verbose)

    # ---- suggest ----
    elif args.command == "suggest":
        months = parse_timeframe(args.timeframe)
        suggest_cost_optimizations(months=months)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
