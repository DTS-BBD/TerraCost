# TerraCost

A powerful tool for estimating Terraform infrastructure costs with advanced uncertainty analysis and cost optimization suggestions.

## Features

- **🚀 Direct Terraform File Parsing**: Parses `.tf` files directly without needing `terraform plan`
- **📊 Cost Uncertainty Analysis**: Uses Monte Carlo simulation to provide confidence intervals and volatility estimates
- **🔄 Progress Indicators**: Real-time loading animations and progress tracking during operations
- **☁️ AWS Cost Estimation**: Real-time pricing from AWS Pricing API
- **💡 AI-Powered Suggestions**: LLM-based cost optimization recommendations using OpenAI
- **📈 Timeframe Flexibility**: Support for days, months, and years with automatic conversion
- **🔧 Module Support**: Recursively processes Terraform modules for complete cost analysis

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd TerraCost

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Usage

### Basic Cost Estimation

```bash
# Estimate costs for 1 month (default)
terracost plan -f /path/to/terraform/directory

# Estimate costs for 6 months
terracost plan -f /path/to/terraform/directory -t 6m

# Estimate costs for 2 years with detailed breakdown
terracost plan -f /path/to/terraform/directory -t 2y --verbose
```

### AI-Powered Cost Optimization Suggestions

```bash
# Get budget-based suggestions (fit within $20/month budget)
terracost suggest -f /path/to/terraform/directory --budget 20.0

# Get savings-focused suggestions (3 levels: conservative, moderate, aggressive)
terracost suggest -f /path/to/terraform/directory --savings

# Get best value suggestions (optimal cost-performance balance)
terracost suggest -f /path/to/terraform/directory --bestvalue
```

### Timeframe Options

- **Days**: `-t 30d` (30 days)
- **Months**: `-t 6m` (6 months) - default
- **Years**: `-t 2y` (2 years)

## How It Works

### 1. Direct Terraform File Parsing
When you run `terracost plan`, the tool:
- Scans for all `.tf` files in the specified directory
- Parses Terraform configuration directly without executing `terraform plan`
- Recursively processes modules to extract complete resource information
- Provides real-time progress updates during parsing

### 2. Cost Estimation
- Fetches real-time pricing from AWS Pricing API
- Calculates monthly costs for each resource based on configuration
- Applies timeframe multipliers for long-term estimates
- Generates detailed cost breakdowns with uncertainty analysis

### 3. AI-Powered Cost Optimization
When you run `terracost suggest`, the tool:
- Analyzes current infrastructure and costs
- Uses OpenAI's GPT-4 to generate optimization suggestions
- Provides budget-based, savings-focused, and best-value recommendations
- Outputs structured suggestions with explanations

### 4. Progress Tracking & Error Handling
- Shows loading animations during operations
- Provides step-by-step progress updates
- Handles errors gracefully with user-friendly troubleshooting tips

## Architecture

```
TerraCost/
├── main.py                 # CLI entry point
├── services/
│   ├── base_cost_service.py    # Base class for cost services
│   ├── aws_cost_service.py     # AWS-specific cost calculations
│   ├── progress_indicator.py   # Loading animations and progress
│   └── terraform_file_parser.py # Direct .tf file parsing
├── pyproject.toml         # Package configuration
├── setup.py               # Package setup
└── requirements.txt       # Dependencies
```

## Supported Resources

### AWS
- EC2 instances
- RDS databases
- S3 buckets
- More coming soon...

### Azure
- Virtual Machines
- SQL Databases
- Storage Accounts
- More coming soon...

## Configuration

### Environment Variables
```bash
# Required for AI-powered cost suggestions
export OPENAI_API_KEY="your-openai-api-key-here"

# Optional AWS configuration (uses default profile if not set)
export AWS_PROFILE="default"
export AWS_REGION="us-east-1"
```

### Getting an OpenAI API Key
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Set it in your environment: `export OPENAI_API_KEY="sk-..."`

## Error Handling

The tool provides comprehensive error handling:
- **File Parsing Errors**: Clear messages when Terraform files can't be parsed
- **API Errors**: Retry logic and fallback mechanisms for AWS Pricing API
- **LLM Errors**: Helpful messages when OpenAI API is unavailable or misconfigured
- **Resource Errors**: Guidance when no AWS resources are found

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
mypy .
```

### Adding New Cloud Providers
1. Create a new service class inheriting from `BaseCostService`
2. Implement the required abstract methods
3. Update the main CLI to handle the new provider
4. Add provider detection logic in the file parser

## Members

- Daniël van Zyl
- Shailyn Ramsamy Moodley  
- Tevlen Naidoo