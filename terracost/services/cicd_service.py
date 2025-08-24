import json
import sys
from typing import Dict
from .aws_cost_service import AwsCostService
from .terraform_file_parser import TerraformFileParser

class CostReporter:
    """Generates cost estimation reports"""

    @staticmethod
    def generate_report(costs: Dict[str, float], total_cost: float, filepath: str = "cost_report.json"):
        """Save a JSON report with resource breakdown + total cost"""
        report = {
            "resources": costs,
            "total_estimated_cost": total_cost
        }
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        print(f"✅ Cost report generated at {filepath}")


class CostGuard:
    """CI/CD guard for cost enforcement"""

    @staticmethod
    def enforce_budget(total_cost: float, budget_limit: float):
        if total_cost > budget_limit:
            raise Exception(
                f"❌ Estimated cost (${total_cost:.2f}) exceeds budget limit (${budget_limit:.2f})"
            )
        print(f"✅ Estimated cost (${total_cost:.2f}) is within budget (${budget_limit:.2f})")


def run_pipeline_check(working_dir: str, budget_limit: float = 200.0):
    parser = TerraformFileParser(working_dir)
    parsed = parser.parse_terraform_files(show_progress=False)

    if not parsed:
        print("❌ No AWS resources found in the specified directory")
        sys.exit(1)

    infrastructure = parsed["resources"].get("aws", {})

    service = AwsCostService()

    costs = service.build_costs(infrastructure)
    total_cost = sum(costs.values())

    CostReporter.generate_report(costs, total_cost, filepath="cost_report.json")

    CostGuard.enforce_budget(total_cost, budget_limit)

    return total_cost
