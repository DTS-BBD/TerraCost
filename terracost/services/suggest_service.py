from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

from .aws_cost_service import AwsCostService
from .progress_indicator import ProgressIndicator

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
            
            print("\n📋 Suggested Configuration:")
            print(json.dumps(data["config"], indent=4))
            print(f"\n💰 Estimated Cost: ${data['total_cost']:.2f}")
            print(f"\n💡 Explanation:")
            print(data["explanation"])
        except json.JSONDecodeError:
            print("⚠️ Could not parse LLM response as JSON")
            print(response)
    else:
        print(response)

def suggest_budget(budget: float, infrastructure: dict):
    """Suggest infrastructure modifications to fit within budget"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    service = AwsCostService()
    current_costs = service.build_costs(infrastructure)
    current_total = sum(current_costs.values())
    
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
        You are an AWS cost optimization expert. Help reduce infrastructure costs to fit within budget.
        
        Current infrastructure: {infrastructure}
        Current monthly cost: ${current_cost:.2f}
        Target budget: ${budget:.2f}
        
        Task: Propose a modified configuration that fits within the ${budget:.2f} budget.
        - Keep essential resources but downgrade where possible
        - Suggest alternative instance types, storage classes, etc.
        - Focus on AWS-specific optimizations
        
        Output as JSON with:
        - "config": modified infrastructure configuration
        - "total_cost": estimated monthly cost
        - "explanation": detailed explanation of changes and savings
        """)
        
        response = llm.invoke(template.format(
            infrastructure=infrastructure, 
            current_cost=current_total, 
            budget=budget
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")

def suggest_savings(infrastructure: dict):
    """Suggest infrastructure combinations at different saving levels"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    service = AwsCostService()
    current_costs = service.build_costs(infrastructure)
    current_total = sum(current_costs.values())
    
    print(f"💡 Cost Savings Suggestions (Current: ${current_total:.2f}/month)")
    print("=" * 60)
    
    # Show loading animation
    progress = show_llm_loading("🤖 Generating cost savings alternatives...")
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
        
        template = PromptTemplate.from_template("""
        You are an AWS cost optimization expert. Suggest 3 alternative configurations with different savings levels.
        
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
            infrastructure=infrastructure, 
            current_cost=current_total
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")

def suggest_best_value(infrastructure: dict):
    """Suggest configuration that provides best bang for buck"""
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set it in your environment.")
        return
    
    service = AwsCostService()
    current_costs = service.build_costs(infrastructure)
    current_total = sum(current_costs.values())
    
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
        You are an AWS cost optimization expert. Suggest the best value configuration.
        
        Current infrastructure: {infrastructure}
        Current monthly cost: ${current_cost:.2f}
        
        Task: Propose a configuration that provides the best bang for buck by:
        - Balancing cost with performance needs
        - Using appropriate instance types for workloads
        - Optimizing storage and database choices
        - Considering reserved instances for long-term savings
        
        Output as JSON with:
        - "config": optimized infrastructure configuration
        - "total_cost": estimated monthly cost
        - "explanation": why this provides best value
        """)
        
        response = llm.invoke(template.format(
            infrastructure=infrastructure, 
            current_cost=current_total
        ))
        
        progress.stop("✅ AI suggestions generated!")
        pretty_display(response.content)
        
    except Exception as e:
        progress.stop("❌ Failed to generate suggestions")
        print(f"⚠️ Error: {str(e)}")
        print("💡 Try checking your OpenAI API key and internet connection")
