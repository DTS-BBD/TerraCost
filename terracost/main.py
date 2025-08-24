import argparse
import sys
import re
from typing import List
from pydantic import BaseModel, Field
from terracost.services.aws_cost_service import AwsCostService
from terracost.services.terraform_file_parser import TerraformFileParser
from terracost.services.progress_indicator import CostCalculationProgress
from terracost.services.suggest_service import suggest_budget, suggest_savings, suggest_best_value

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

def estimate_cost_from_files(months: float, verbose: bool, working_dir: str) -> CostEstimate:
    """
    Estimate costs by parsing Terraform files directly
    """
    progress = CostCalculationProgress()
    parser = None
    
    try:
        progress.start()
        
        # Step 1: Parse Terraform files
        progress.next_step()
        parser = TerraformFileParser(working_dir)
        parse_result = parser.parse_terraform_files(show_progress=True)
        
        # Step 2: Extract resource information
        progress.next_step()
        resources = parse_result['resources']
        
        # Step 3: Fetch cloud pricing data
        progress.next_step()
        
        # Use AWS cost service (currently only AWS is supported)
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
        _display_cost_estimate(estimate, verbose, parse_result['summary'])
        
        return estimate
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        progress.stop(False)
        sys.exit(1)
    except Exception as e:
        progress.stop(False)
        raise e

def _display_cost_estimate(estimate: CostEstimate, verbose: bool, plan_summary: dict):
    """Display the cost estimate with uncertainty analysis"""
    print(f"\n📊 Cost Estimate for {estimate.timeframe_months:.1f} month(s)")
    print("=" * 50)
    
    # Display infrastructure summary
    if plan_summary:
        print(f"📋 Infrastructure Summary:")
        print(f"   📁 Total Terraform files: {plan_summary.get('modules_count', 0) + 1}")
        print(f"   🔧 Total resources: {plan_summary.get('total_resources', 0)}")
        print(f"   📦 Modules: {plan_summary.get('modules_count', 0)}")
        
        # Show provider breakdown
        provider_counts = plan_summary.get('provider_counts', {})
        for provider, count in provider_counts.items():
            if count > 0:
                provider_emoji = "☁️" if provider == "aws" else "🔷" if provider == "azure" else "🔶"
                print(f"   {provider_emoji} {provider.upper()} resources: {count}")
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

    # ---- suggest ----
    suggest_parser = subparsers.add_parser("suggest", help="Get LLM-based cost optimization suggestions")
    suggest_parser.add_argument(
        "-t", "--timeframe", type=str, default="1m",
        help="Timeframe for cost estimation (Xd, Xm, Xy). Default: 1m"
    )
    suggest_parser.add_argument(
        "-f", "--file", type=str, default=".", 
        help="Folder location with your infrastructure (default: current directory)"
    )
    suggest_parser.add_argument(
        "--budget", type=float,
        help="Suggest infrastructure modifications to fit within budget"
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
    elif args.command == "plan":
        months = parse_timeframe(args.timeframe)
        infrastructure_file = args.file
        
        try:
            estimate_cost_from_files(months=months, verbose=args.verbose, 
                                  working_dir=infrastructure_file)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("\n🔧 Troubleshooting Tips:")
            print("   • Check if you're in the right directory with Terraform files")
            print("   • Verify your Terraform configuration is valid")
            print("   • Check if .tf files are readable and properly formatted")
            sys.exit(1)

    # ---- suggest ----
    elif args.command == "suggest":
        months = parse_timeframe(args.timeframe)
        infrastructure_file = args.file
        
        try:
            # Parse infrastructure to get current resources
            parser = TerraformFileParser(infrastructure_file)
            parse_result = parser.parse_terraform_files(show_progress=False)
            infrastructure = parse_result['resources'].get('aws', {})
            
            if not infrastructure:
                print("❌ No AWS resources found in the specified directory")
                sys.exit(1)
            
            # Get current cost estimate for context
            service = AwsCostService()
            current_costs = service.build_costs(infrastructure)
            current_total = sum(current_costs.values())
            
            print(f"📊 Current Infrastructure Analysis")
            print(f"   📁 Directory: {infrastructure_file}")
            print(f"   🔧 Resources: {sum(len(resources) for resources in infrastructure.values())}")
            print(f"   💰 Current monthly cost: ${current_total:.2f}")
            print()
            
            if args.budget:
                suggest_budget(args.budget, infrastructure)
            elif args.savings:
                suggest_savings(infrastructure)
            elif args.bestvalue:
                suggest_best_value(infrastructure)
            else:
                print("⚠️ Please provide one option: --budget, --savings, or --bestvalue")
                print("\nExamples:")
                print("   terracost suggest --budget 20.0    # Fit within $20/month budget")
                print("   terracost suggest --savings        # Get savings suggestions")
                print("   terracost suggest --bestvalue      # Get best value suggestions")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("\n🔧 Troubleshooting Tips:")
            print("   • Check if you're in the right directory with Terraform files")
            print("   • Verify your Terraform configuration is valid")
            print("   • Make sure OPENAI_API_KEY is set for LLM suggestions")
            sys.exit(1)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
