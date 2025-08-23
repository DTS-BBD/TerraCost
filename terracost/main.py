import argparse
import sys
import re
from typing import List
from pydantic import BaseModel, Field
from terracost.services.aws_cost_service import AwsCostService
from terracost.services.azure_cost_service import AzureCostService
from terracost.services.terraform_executor import TerraformExecutor
from terracost.services.progress_indicator import CostCalculationProgress
from terracost.services.terraform_parser import detect_provider, parse_infrastructure, parse_azure_infrastructure
from terracost.services.suggest_service import suggest_best_value, suggest_budget, suggest_savings

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
    uncertainty_analysis: dict = None

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

def estimate_cost_from_plan(months: float, verbose: bool, working_dir: str) -> CostEstimate:
    """
    Estimate costs by running terraform plan and analyzing the output
    """
    progress = CostCalculationProgress()
    progress.start()
    
    try:
        # Step 1: Run terraform plan
        progress.next_step()
        executor = TerraformExecutor(working_dir)
        plan_result = executor.run_terraform_plan(show_progress=False)
        
        # Step 2: Parse infrastructure changes
        progress.next_step()
        resources = plan_result['resources']
        
        # Step 3: Fetch cloud pricing data
        progress.next_step()
        
        # Determine provider and get cost service
        provider = "aws"  # Default, will be updated based on resources
        if resources.get('azure'):
            provider = "azure"
        elif resources.get('gcp'):
            provider = "gcp"
        
        if provider == "azure":
            service = AzureCostService()
            infrastructure = resources.get('azure', {})
        elif provider == "gcp":
            # TODO: Implement GCP cost service
            raise NotImplementedError("GCP cost estimation not yet implemented")
        else:
            service = AwsCostService()
            infrastructure = resources.get('aws', {})
        
        # Step 4: Calculate cost estimates
        progress.next_step()
        costs = service.build_costs(infrastructure)
        
        breakdown = [ResourceCost(name=r, monthly_cost=c) for r, c in costs.items()]
        total_monthly = sum(rc.monthly_cost for rc in breakdown)
        total_cost = total_monthly * months
        
        # Step 5: Generate uncertainty analysis
        progress.next_step()
        uncertainty = service.estimate_uncertainty(total_monthly, months)
        
        estimate = CostEstimate(
            timeframe_months=months,
            total_cost=total_cost,
            breakdown=breakdown,
            uncertainty_analysis=uncertainty
        )
        
        progress.stop(True)
        
        # Display results
        _display_cost_estimate(estimate, verbose, plan_result['summary'])
        
        return estimate
        
    except Exception as e:
        progress.stop(False)
        raise e

def _display_cost_estimate(estimate: CostEstimate, verbose: bool, plan_summary: dict):
    """Display the cost estimate with uncertainty analysis"""
    print(f"\n📊 Cost Estimate for {estimate.timeframe_months:.1f} month(s)")
    print("=" * 50)
    
    # Display plan summary
    if plan_summary:
        print(f"📋 Infrastructure Changes:")
        print(f"   ➕ Add: {plan_summary.get('add', 0)} resources")
        print(f"   🔄 Change: {plan_summary.get('change', 0)} resources")
        print(f"   🗑️  Destroy: {plan_summary.get('destroy', 0)} resources")
        print()
    
    # Display cost breakdown
    print(f"💰 Total Cost: ${estimate.total_cost:.2f}")
    
    # Display uncertainty analysis
    if estimate.uncertainty_analysis:
        uncertainty = estimate.uncertainty_analysis
        print(f"📈 Cost Uncertainty Analysis:")
        print(f"   📊 68% Confidence: ${uncertainty['confidence_68_lower']:.2f} - ${uncertainty['confidence_68_upper']:.2f}")
        print(f"   📊 95% Confidence: ${uncertainty['confidence_95_lower']:.2f} - ${uncertainty['confidence_95_upper']:.2f}")
        print(f"   📈 Volatility: {uncertainty['volatility']*100:.1f}% monthly variation")
        print()
    
    if verbose:
        print("📋 Detailed Breakdown (per resource):")
        for rc in estimate.breakdown:
            print(f"   - {rc.name:40} ${rc.monthly_cost:.2f}/month")
        print()

def estimate_cost(months: float, verbose: bool, infrastructure: dict, provider: str) -> CostEstimate:
    """
    Legacy cost estimation (kept for backward compatibility)
    """
    if provider == "azure":
        service = AzureCostService()
    else:
        service = AwsCostService()

    costs = service.build_costs(infrastructure)

    breakdown = [ResourceCost(name=r, monthly_cost=c * months) for r, c in costs.items()]
    total = sum(rc.monthly_cost for rc in breakdown)

    estimate = CostEstimate(
        timeframe_months=months,
        total_cost=total,
        breakdown=breakdown
    )

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
    plan_parser.add_argument(
        "-f", "--file", type=str, default=".",
        help="Folder location with your Terraform infrastructure (default: current directory)"
    )
    plan_parser.add_argument(
        "--legacy", action="store_true",
        help="Use legacy parsing (parse .tf files directly instead of running terraform plan)"
    )

    # ---- suggest ----
    suggest_parser = subparsers.add_parser("suggest", help="Suggest cost optimizations")
    suggest_parser.add_argument(
        "-t", "--timeframe", type=str, default="1m",
        help="Timeframe for cost estimation (Xd, Xm, Xy). Default: 1m"
    )
    suggest_parser.add_argument(
        "-f", "--file", type=str, default=".", help="Folder location with your infrastructure (default: current directory)"
    )
    suggest_parser.add_argument(
        "--budget", type=float,
        help="Suggests infrastructure combination based on provided budget"
    )
    suggest_parser.add_argument(
        "--savings", action="store_true",
        help="Suggest infrastructure combinations at different saving levels"
    )
    suggest_parser.add_argument(
        "--bestvalue", action="store_true",
        help="Suggest infrastructure that offers the best bang for your buck"
    )

    args = parser.parse_args()

    # ---- handle version ----
    if args.version and not args.command:
        print(f"TerraCost v{__version__}")
        sys.exit(0)

    # ---- plan ----
    if args.command == "plan":
        months = parse_timeframe(args.timeframe)
        infrastructure_file = args.file
        
        if args.legacy:
            # Use legacy parsing method
            provider = detect_provider(infrastructure_file)
            if provider == "azure":
                infrastructure = parse_azure_infrastructure(infrastructure_file)
            else:
                infrastructure = parse_infrastructure(infrastructure_file)
            estimate_cost(months=months, verbose=args.verbose, 
                         infrastructure=infrastructure, provider=provider)
        else:
            # Use new terraform plan method
            try:
                estimate_cost_from_plan(months=months, verbose=args.verbose, 
                                      working_dir=infrastructure_file)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("💡 Try using --legacy flag for basic .tf file parsing")
                sys.exit(1)

    # ---- suggest ----
    elif args.command == "suggest":
        months = parse_timeframe(args.timeframe)
        infrastructure_file = args.file
        provider = detect_provider(infrastructure_file)
        
        if provider == "azure":
            infrastructure = parse_azure_infrastructure(infrastructure_file)
        else:
            infrastructure = parse_azure_infrastructure(infrastructure_file)
            
        if args.budget:
            suggest_budget(args.budget, infrastructure)
        elif args.savings:
            suggest_savings(infrastructure)
        elif args.bestvalue:
            suggest_best_value(infrastructure)
        else:
            print("⚠️ Please provide one option: --budget, --savings, or --best-value")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
