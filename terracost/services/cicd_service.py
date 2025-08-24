import json
import sys
from typing import Dict
from .aws_cost_service import AwsCostService
from .azure_cost_service import AzureCostService
from .gcp_cost_service import GCPCostService
from .terraform_file_parser import TerraformFileParser
from .progress_indicator import CostCalculationProgress

import json
import os
from typing import Dict


class CostGuard:
    """CI/CD guard for cost enforcement and warning"""

    @staticmethod
    def enforce_budget(
        total_cost: float,
        budget_limit: float,
        costs: Dict[str, float] = None,
        previous_cost_file: str = "cost_report.json",
        warning_threshold: float = 0.75,
        max_growth_rate: float = 0.50,
    ):
        """
        Run multiple cost checks:
        1. Global budget check
        2. Warning threshold check
        3. Per-resource sanity checks (e.g., no single resource > 50% of budget)
        4. Growth check compared to previous run
        """
        messages = []

        # --- Hard Budget Limit ---
        if total_cost > budget_limit:
            raise Exception(
                f"❌ Estimated cost (${total_cost:.2f}) exceeds budget limit (${budget_limit:.2f})"
            )
        else:
            messages.append(
                f"✅ Total cost (${total_cost:.2f}) is within budget (${budget_limit:.2f})"
            )

        # --- Warning Threshold ---
        if total_cost > warning_threshold * budget_limit:
            messages.append(
                f"⚠️ Cost is above {warning_threshold*100:.0f}% of budget (${total_cost:.2f} / ${budget_limit:.2f})"
            )

        # --- Per-resource sanity check ---
        if costs:
            for resource, cost in costs.items():
                if cost > 0.5 * budget_limit:
                    messages.append(
                        f"⚠️ Resource '{resource}' alone costs ${cost:.2f}, "
                        f"which exceeds 50% of budget"
                    )

        # --- Growth detection ---
        if os.path.exists(previous_cost_file):
            try:
                with open(previous_cost_file, "r") as f:
                    prev_total = json.load(f).get("total_estimated_cost", 0)

                if prev_total > 0:
                    growth = (total_cost - prev_total) / prev_total
                    if growth > max_growth_rate:
                        messages.append(
                            f"⚠️ Cost increased by {growth*100:.1f}% since last run "
                            f"(${prev_total:.2f} → ${total_cost:.2f})"
                        )
            except Exception:
                messages.append("⚠️ Could not read previous cost file for growth check.")

        try:
            report = {
                "resources": costs,
                "total_estimated_cost": total_cost
            }
            with open(previous_cost_file, "w") as f:
                json.dump(report, f, indent=2)
        except Exception:
            messages.append("⚠️ Failed to persist current cost for future comparisons.")

        for msg in messages:
            print(msg)

def run_pipeline_check(working_dir: str, budget_limit: float = 25.0):

    progress = CostCalculationProgress()
    parser = None
    
    try:
        progress.start()
        
        # Step 1: Parse Terraform files
        progress.next_step()
        parser = TerraformFileParser(working_dir)
        parsed = parser.parse_terraform_files(show_progress=True)

        if not parsed:
            print("❌ No AWS resources found in the specified directory")
            sys.exit(1)

        # Step 2: Extract resource information
        progress.next_step()
        resources = parsed['resources']
        
        # Step 3: Fetch cloud pricing data
        progress.next_step()
        
        # Step 4: Calculate cost estimates for all cloud providers
        progress.next_step()
        
        all_costs = {}
        total_monthly = 0.0
        
        # AWS costs
        if resources.get('aws'):
            aws_service = AwsCostService()
            aws_costs = aws_service.build_costs(resources['aws'])
            all_costs.update({f"aws.{k}": v for k, v in aws_costs.items()})
            total_monthly += sum(aws_costs.values())
        
        # Azure costs
        if resources.get('azure'):
            azure_service = AzureCostService()
            azure_costs = azure_service.build_costs(resources['azure'])
            all_costs.update({f"azure.{k}": v for k, v in azure_costs.items()})
            total_monthly += sum(azure_costs.values())
        
        # GCP costs
        if resources.get('gcp'):
            gcp_service = GCPCostService()
            gcp_costs = gcp_service.build_costs(resources['gcp'])
            all_costs.update({f"gcp.{k}": v for k, v in gcp_costs.items()})
            total_monthly += sum(gcp_costs.values())
        
        # Other/unknown resources
        if resources.get('other'):
            # Estimate costs for unknown resources
            other_costs = {f"other.{k}": 10.0 for k in resources['other'].keys()}
            all_costs.update(other_costs)
            total_monthly += sum(other_costs.values())
        
        
        progress.stop(True)

        CostGuard.enforce_budget(total_cost=total_monthly, costs=all_costs, budget_limit=budget_limit)

        return total_monthly
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        progress.stop(False)
        sys.exit(1)
    except Exception as e:
        progress.stop(False)
        raise e
