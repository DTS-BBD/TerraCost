from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
import re

from .aws_cost_service import AwsCostService
from .progress_indicator import ProgressIndicator
from terracost.services.azure_cost_service import AzureCostService
from terracost.services.gcp_cost_service import GCPCostService

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def show_llm_loading(message: str = "🤖 Generating AI suggestions..."):
    """Show a loading animation for LLM operations"""
    progress = ProgressIndicator(message)
    progress.start()
    return progress

def pretty_display(response):
    """Extract and display JSON response from LLM"""
    match = re.search(r"```json\n(.*?)```", response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            data = json.loads(json_str)

            if isinstance(data, dict):
                print("\n📋 Suggested Configuration:")
                print(json.dumps(data["config"], indent=4))

                try:
                    cost = float(alt.get("total_cost", 0))
                    print(f"💰 Estimated Cost: ${cost:.2f}")
                except (ValueError, TypeError):
                    print(f"💰 Estimated Cost: {alt.get('total_cost', 'N/A')}")

                print(f"\n💡 Explanation:")
                print(data["explanation"])

            elif isinstance(data, list):
                print("\n📋 Suggested Configurations (Alternatives):")
                for i, alt in enumerate(data, start=1):
                    print(f"\n--- Alternative {i} ---")
                    print(json.dumps(alt["config"], indent=4))

                    try:
                        cost = float(alt.get("total_cost", 0))
                        print(f"💰 Estimated Cost: ${cost:.2f}")
                    except (ValueError, TypeError):
                        print(f"💰 Estimated Cost: {alt.get('total_cost', 'N/A')}")

                    print(f"💾 Savings: {alt.get('savings_percent', 'N/A')}%")
                    print("💡 Explanation:")
                    print(alt["explanation"])
            else:
                print("⚠️ Unexpected JSON structure")
                print(data)

        except json.JSONDecodeError:
            print("⚠️ Could not parse LLM response as JSON")
            print(response)
    else:
        print(response)

def suggest_budget(budget: float, resources: dict):
    """Suggest infrastructure modifications to fit within budget"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    total_monthly = 0.0
    
    # AWS costs
    if resources.get('aws'):
        aws_service = AwsCostService()
        aws_costs = aws_service.build_costs(resources['aws'])
        total_monthly += sum(aws_costs.values())
    
    # Azure costs
    if resources.get('azure'):
        azure_service = AzureCostService()
        azure_costs = azure_service.build_costs(resources['azure'])
        total_monthly += sum(azure_costs.values())
    
    # GCP costs
    if resources.get('gcp'):
        gcp_service = GCPCostService()
        gcp_costs = gcp_service.build_costs(resources['gcp'])
        total_monthly += sum(gcp_costs.values())
    
    # Other/unknown resources
    if resources.get('other'):
        # Estimate costs for unknown resources
        other_costs = {f"other.{k}": 10.0 for k in resources['other'].keys()}
        total_monthly += sum(other_costs.values())

    print(f"🎯 Budget Optimization Suggestions (Target: ${budget:.2f})")
    print("=" * 60)
    
    # Show loading animation
    progress = show_llm_loading("🤖 Analyzing infrastructure for budget optimization...")
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
        
        template = PromptTemplate.from_template("""
        You are a cloud solutions cost optimization expert. Help reduce infrastructure costs to fit within budget.
        
        Current infrastructure: {infrastructure}
        Current monthly cost: ${current_cost:.2f}
        Target budget: ${budget:.2f}
        
        Task: Propose a modified configuration that fits within the ${budget:.2f} budget.
        - Keep essential resources but downgrade where possible
        - Suggest alternative instance types, storage classes, etc.
        - Focus on AWS, Azure and GCP optimizations
        
        Output as JSON with:
        - "config": modified infrastructure configuration
        - "total_cost": estimated monthly cost
        - "explanation": detailed explanation of changes and savings
        """)
        
        response = llm.invoke(template.format(
            infrastructure=resources, 
            current_cost=total_monthly, 
            budget=budget
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")

def suggest_savings(resources: dict):
    """Suggest infrastructure combinations at different saving levels"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    total_monthly = 0.0
    
    # AWS costs
    if resources.get('aws'):
        aws_service = AwsCostService()
        aws_costs = aws_service.build_costs(resources['aws'])
        total_monthly += sum(aws_costs.values())
    
    # Azure costs
    if resources.get('azure'):
        azure_service = AzureCostService()
        azure_costs = azure_service.build_costs(resources['azure'])
        total_monthly += sum(azure_costs.values())
    
    # GCP costs
    if resources.get('gcp'):
        gcp_service = GCPCostService()
        gcp_costs = gcp_service.build_costs(resources['gcp'])
        total_monthly += sum(gcp_costs.values())
    
    # Other/unknown resources
    if resources.get('other'):
        # Estimate costs for unknown resources
        other_costs = {f"other.{k}": 10.0 for k in resources['other'].keys()}
        total_monthly += sum(other_costs.values())
    
    print(f"💡 Cost Savings Suggestions (Current: ${total_monthly:.2f}/month)")
    print("=" * 60)
    
    # Show loading animation
    progress = show_llm_loading("🤖 Generating cost savings alternatives...")
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
        
        template = PromptTemplate.from_template("""
        You are an cloud solutions cost optimization expert. Suggest 3 alternative configurations with different savings levels.
        
        Current infrastructure: {infrastructure}
        Current monthly cost: ${current_cost:.2f}
        
        Task: Propose 3 alternatives:
        1. Conservative (10-20% savings): Minor optimizations, minimal risk
        2. Moderate (20-40% savings): Balanced optimizations, some risk
        3. Aggressive (40-60% savings): Major changes, higher risk
        
        For each alternative, provide:
        - "config": modified infrastructure
        - "total_cost": estimated monthly cost
        - "savings_percent": percentage saved
        - "explanation": changes made and risks
        
        Output as JSON array with these 3 alternatives.
        """)
        
        response = llm.invoke(template.format(
            infrastructure=resources, 
            current_cost=total_monthly
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")

def suggest_best_value(resources: dict):
    """Suggest configuration that provides best bang for buck"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    total_monthly = 0.0
    
    # AWS costs
    if resources.get('aws'):
        aws_service = AwsCostService()
        aws_costs = aws_service.build_costs(resources['aws'])
        total_monthly += sum(aws_costs.values())
    
    # Azure costs
    if resources.get('azure'):
        azure_service = AzureCostService()
        azure_costs = azure_service.build_costs(resources['azure'])
        total_monthly += sum(azure_costs.values())
    
    # GCP costs
    if resources.get('gcp'):
        gcp_service = GCPCostService()
        gcp_costs = gcp_service.build_costs(resources['gcp'])
        total_monthly += sum(gcp_costs.values())
    
    # Other/unknown resources
    if resources.get('other'):
        # Estimate costs for unknown resources
        other_costs = {f"other.{k}": 10.0 for k in resources['other'].keys()}
        total_monthly += sum(other_costs.values())
    
    print(f"⭐ Best Value Configuration Suggestions")
    print("=" * 60)
    
    # Show loading animation
    progress = show_llm_loading("🤖 Analyzing infrastructure for best value...")
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
        
        template = PromptTemplate.from_template("""
        You are an cloud solutions cost optimization expert. Suggest the best value configuration.
        
        Current infrastructure: {infrastructure}
        Current monthly cost: ${current_cost:.2f}
        
        Task: Propose a configuration that provides the best bang for buck by:
        - Balancing cost with performance needs
        - Using appropriate instance types for workloads
        - Optimizing storage and database choices
        - Considering reserved instances for long-term savings
        - Focus on AWS, Azure and GCP optimizations
        
        Output as JSON with:
        - "config": optimized infrastructure configuration
        - "total_cost": estimated monthly cost
        - "explanation": why this provides best value
        """)
        
        response = llm.invoke(template.format(
            infrastructure=resources, 
            current_cost=total_monthly
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")
