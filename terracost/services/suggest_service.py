from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

from .aws_cost_service import AwsCostService

service = AwsCostService()

def pretty_display(response):
    match = re.search(r"```json\n(.*?)```", response, re.DOTALL)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)


        print("\nConfig:")
        print(json.dumps(data["config"], indent=4))

        print(f"\nTotal Cost: ${data['total_cost']:.2f}")

        print("\nExplanation:")
        print(data["explanation"])
    else:
        print(response)

def display_with_breakdown(response):
    parts = response.content.split("### Cost Breakdown:")
    pretty_display(parts[0])

    if len(parts) > 1:
        print("\nCost Breakdown:")
        print(parts[1].strip())

def suggest_budget(budget, infrastructure):
    llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
    template = PromptTemplate.from_template("""
    You are an AWS cost optimization assistant.
    The current config is:
    {config}
    The current costs are:
    {costs}
    The user budget is ${budget}.

    Task:
    - Propose a modified configuration that fits within the budget.
    - Keep resources if possible, but downgrade where needed.
    - Output as JSON with 'config', 'total_cost', and 'explanation'.
    """)
    
    costs = service.build_costs(infrastructure)
    response = llm.invoke(template.format(config=infrastructure, costs=costs, budget=budget))
    display_with_breakdown(response)


def suggest_savings(infrastructure):
    llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )
    template = PromptTemplate.from_template("""
    Current config:
    {config}
    Current costs:
    {costs}

    Task:
    - Propose at least 3 alternative configs with different saving percentages.
    - Each alternative should include: config, total_cost, savings_percent, explanation.
    """)
    costs = service.build_costs(infrastructure)
    response = llm.invoke(template.format(config=infrastructure, costs=costs))
    display_with_breakdown(response)


def suggest_best_value(infrastructure):
    llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key
        )

    template = PromptTemplate.from_template("""
    Current config:
    {config}
    Current costs:
    {costs}

    Task:
    - Suggest a configuration that provides the best bang for the buck 
      (balancing cost with CPU/memory and database/storage needs).
    - Return JSON with 'config', 'total_cost', and 'explanation'.
    """)
    costs = service.build_costs(infrastructure)
    response = llm.invoke(template.format(config=infrastructure, costs=costs))
    display_with_breakdown(response)
