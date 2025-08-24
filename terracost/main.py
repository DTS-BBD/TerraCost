import argparse
import sys
import re
import platform
from typing import List
from pydantic import BaseModel, Field
from terracost.services.aws_cost_service import AwsCostService
from terracost.services.azure_cost_service import AzureCostService
from terracost.services.gcp_cost_service import GCPCostService
from terracost.services.terraform_file_parser import TerraformFileParser
from terracost.services.progress_indicator import CostCalculationProgress
from terracost.services.suggest_progress import SuggestStepTracker
from terracost.services.suggest_service import suggest_budget, suggest_savings, suggest_best_value
from terracost.services.cicd_service import run_pipeline_check

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

def get_symbol(symbol_name: str) -> str:
    """Get platform-appropriate symbol for output"""
    if platform.system() == "Windows":
        symbols = {
            "check": "[OK]",
            "cross": "[ERROR]",
            "folder": "[DIR]",
            "wrench": "[TOOL]",
            "package": "[PKG]",
            "search": "[SEARCH]",
            "list": "[LIST]",
            "rocket": "[ROCKET]",
            "target": "[TARGET]",
            "gear": "[GEAR]",
            "box": "[BOX]",
            "clipboard": "[CLIP]",
            "checklist": "[CHECKLIST]",
            "tada": "[SUCCESS]",
            "warning": "[WARN]",
            "chart": "[CHART]"
        }
        return symbols.get(symbol_name, "[INFO]")
    else:
        symbols = {
            "check": "✅",
            "cross": "❌",
            "folder": "📁",
            "wrench": "🔧",
            "package": "📦",
            "search": "🔍",
            "list": "📋",
            "rocket": "🚀",
            "target": "🎯",
            "gear": "⚙️",
            "box": "📦",
            "clipboard": "📋",
            "checklist": "📋",
            "tada": "🎉",
            "warning": "⚠️"
        }
        return symbols.get(symbol_name, "ℹ️")

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
        
        breakdown = [ResourceCost(name=r, monthly_cost=c) for r, c in all_costs.items()]
        total_cost = total_monthly * months
        
        # Step 5: Generate uncertainty analysis (use AWS service as default)
        progress.next_step()
        service = AwsCostService()  # Default service for uncertainty calculation
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
    print(f"\n{get_symbol('chart')} Cost Estimate for {estimate.timeframe_months:.1f} month(s)")
    print("=" * 50)
    
    # Display infrastructure summary
    if plan_summary:
        print(f"{get_symbol('checklist')} Infrastructure Summary:")
        print(f"   {get_symbol('folder')} Total Terraform files: {plan_summary.get('modules_count', 0) + 1}")
        print(f"   {get_symbol('wrench')} Total resources: {plan_summary.get('total_resources', 0)}")
        print(f"   {get_symbol('package')} Modules: {plan_summary.get('modules_count', 0)}")
        
        # Show provider breakdown
        provider_counts = plan_summary.get('provider_counts', {})
        for provider, count in provider_counts.items():
            if count > 0:
                if provider == "aws":
                    provider_symbol = "[AWS]"
                elif provider == "azure":
                    provider_symbol = "[AZURE]"
                elif provider == "gcp":
                    provider_symbol = "[GCP]"
                else:
                    provider_symbol = "[OTHER]"
                print(f"   {provider_symbol} {provider.upper()} resources: {count}")
        print()
    
    # Display cost breakdown
    print(f"[COST] Total Cost: ${estimate.total_cost:.2f}")
    
    # Display uncertainty analysis
    if estimate.uncertainty_analysis:
        uncertainty = estimate.uncertainty_analysis
        print(f"{get_symbol('chart')} Cost Uncertainty Analysis:")
        print(f"   {get_symbol('chart')} 68% Confidence: ${uncertainty['confidence_68_lower']:.2f} - ${uncertainty['confidence_68_upper']:.2f}")
        print(f"   {get_symbol('chart')} 95% Confidence: ${uncertainty['confidence_95_lower']:.2f} - ${uncertainty['confidence_95_upper']:.2f}")
        print(f"   {get_symbol('chart')} Volatility: {uncertainty['volatility']*100:.1f}% monthly variation")
        print()
    
    if verbose:
        print(f"{get_symbol('checklist')} Detailed Breakdown (per resource):")
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

    budget_parser = subparsers.add_parser("budget", help="Generate a cost breakdown budget and check cost limit")
    budget_parser.add_argument(
        "--budget", type=float,
        help="Specify budget limit"
    )
    budget_parser.add_argument(
        "-f", "--file", type=str, default=".", 
        help="Folder location with your infrastructure (default: current directory)"
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
            print(f"{get_symbol('cross')} Error: {str(e)}")
            print(f"\n{get_symbol('wrench')} Troubleshooting Tips:")
            print("   • Check if you're in the right directory with Terraform files")
            print("   • Verify your Terraform configuration is valid")
            print("   • Check if .tf files are readable and properly formatted")
            sys.exit(1)

    # ---- suggest ----
    elif args.command == "suggest":
        months = parse_timeframe(args.timeframe)
        infrastructure_file = args.file
        
        try:
            # Initialize progress tracking
            progress_tracker = SuggestStepTracker()
            progress_tracker.start_analysis()
            
            # Parse infrastructure to get current resources
            parser = TerraformFileParser(infrastructure_file)
            parse_result = parser.parse_terraform_files(show_progress=False)
            all_resources = parse_result['resources']
            
            # Check if any cloud resources exist
            total_resources = sum(len(resources) for resources in all_resources.values())
            if total_resources == 0:
                progress_tracker.progress.stop(False)
                print(f"{get_symbol('cross')} No cloud resources found in the specified directory")
                sys.exit(1)
            
            # Report infrastructure parsing completion
            file_count = parse_result.get('summary', {}).get('modules_count', 0) + 1
            progress_tracker.infrastructure_parsed(file_count, total_resources)
            
            # Get current cost estimate for all providers
            all_costs = {}
            current_total = 0.0
            
            # AWS costs
            if all_resources.get('aws'):
                aws_service = AwsCostService()
                aws_costs = aws_service.build_costs(all_resources['aws'])
                all_costs.update(aws_costs)
                aws_total = sum(aws_costs.values())
                current_total += aws_total
                progress_tracker.provider_costs_calculated("AWS", len(all_resources['aws']), aws_total)
            
            # Azure costs
            if all_resources.get('azure'):
                azure_service = AzureCostService()
                azure_costs = azure_service.build_costs(all_resources['azure'])
                all_costs.update(azure_costs)
                azure_total = sum(azure_costs.values())
                current_total += azure_total
                progress_tracker.provider_costs_calculated("Azure", len(all_resources['azure']), azure_total)
            
            # GCP costs
            if all_resources.get('gcp'):
                gcp_service = GCPCostService()
                gcp_costs = gcp_service.build_costs(all_resources['gcp'])
                all_costs.update(gcp_costs)
                gcp_total = sum(gcp_costs.values())
                current_total += gcp_total
                progress_tracker.provider_costs_calculated("GCP", len(all_resources['gcp']), gcp_total)
            
            # Start AI generation phase (this is separate from cost calculation)
            progress_tracker.ai_generation_started()
            
            # Display infrastructure summary
            print(f"\n{get_symbol('chart')} Current Infrastructure Analysis")
            print(f"   {get_symbol('folder')} Directory: {infrastructure_file}")
            print(f"   {get_symbol('wrench')} Total Resources: {total_resources}")
            
            # Show provider breakdown
            for provider, resources in all_resources.items():
                if resources:
                    if provider == "aws":
                        provider_symbol = "[AWS]"
                    elif provider == "azure":
                        provider_symbol = "[AZURE]"
                    elif provider == "gcp":
                        provider_symbol = "[GCP]"
                    else:
                        provider_symbol = "[OTHER]"
                    print(f"   {provider_symbol} {provider.upper()}: {len(resources)} resources")
            
            print(f"   [COST] Current monthly cost: ${current_total:.2f}")
            print()
            
            # Start optimization processing phase
            progress_tracker.optimization_processing()
            
            if args.budget:
                progress_tracker.progress.update_message(f"Generating AI-powered budget optimization suggestions (target: ${args.budget}/month)...")
                suggest_budget(args.budget, all_resources)
            elif args.savings:
                progress_tracker.progress.update_message("Generating AI-powered cost savings suggestions...")
                suggest_savings(all_resources)
            elif args.bestvalue:
                progress_tracker.progress.update_message("Generating AI-powered best value recommendations...")
                suggest_best_value(all_resources)
            else:
                progress_tracker.progress.stop(False)
                print(f"{get_symbol('warning')} Please provide one option: --budget, --savings, or --bestvalue")
                print("\nExamples:")
                print("   terracost suggest --budget 20.0    # Fit within $20/month budget")
                print("   terracost suggest --savings        # Get savings suggestions")
                print("   terracost suggest --bestvalue      # Get best value suggestions")
                sys.exit(1)
            
            # Complete the process
            result = progress_tracker.complete(True)
                
        except Exception as e:
            if 'progress_tracker' in locals():
                progress_tracker.progress.stop(False)
            print(f"{get_symbol('cross')} Error: {str(e)}")
            print(f"\n{get_symbol('wrench')} Troubleshooting Tips:")
            print("   • Check if you're in the right directory with Terraform files")
            print("   • Verify your Terraform configuration is valid")
            print("   • Make sure OPENAI_API_KEY is set for LLM suggestions")
            sys.exit(1)

    elif args.command == "budget":
        infrastructure_file = args.file
        budget = args.budget
        try:
            run_pipeline_check(infrastructure_file, budget)
        except Exception as e:
            print(f"❌ Error: {str(e)}")      
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
