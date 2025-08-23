# TerraCost

A powerful tool for estimating Terraform infrastructure costs with advanced uncertainty analysis and cost optimization suggestions.

## Features

- **🚀 Terraform Plan Integration**: Automatically runs `terraform plan` and analyzes the output for accurate cost estimation
- **📊 Cost Uncertainty Analysis**: Uses Monte Carlo simulation to provide confidence intervals and volatility estimates
- **🔄 Progress Indicators**: Real-time loading animations and progress tracking during long operations
- **☁️ Multi-Cloud Support**: AWS, Azure, and GCP (coming soon) cost estimation
- **💡 AI-Powered Suggestions**: LLM-based cost optimization recommendations
- **📈 Timeframe Flexibility**: Support for days, months, and years with automatic conversion
- **🔧 Legacy Mode**: Fallback to direct .tf file parsing when needed

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

# Use legacy parsing (parse .tf files directly)
terracost plan -f /path/to/terraform/directory --legacy
```

### Cost Optimization Suggestions

```bash
# Get budget-based suggestions
terracost suggest -f /path/to/terraform/directory --budget 500

# Get savings-focused suggestions
terracost suggest -f /path/to/terraform/directory --savings

# Get best value suggestions
terracost suggest -f /path/to/terraform/directory --bestvalue
```

### Timeframe Options

- **Days**: `-t 30d` (30 days)
- **Months**: `-t 6m` (6 months) - default
- **Years**: `-t 2y` (2 years)

## How It Works

### 1. Terraform Plan Execution
When you run `terracost plan`, the tool:
- Executes `terraform plan` in the background
- Captures the output to a temporary JSON file
- Parses the plan to extract resource information
- Provides real-time progress updates

### 2. Cost Estimation
- Fetches real-time pricing from cloud provider APIs
- Calculates monthly costs for each resource
- Applies timeframe multipliers
- Generates detailed cost breakdowns

### 3. Uncertainty Analysis
- Uses Monte Carlo simulation to model cost variations
- Provides 68% and 95% confidence intervals
- Estimates monthly volatility based on timeframe
- Accounts for long-term cost uncertainty

### 4. Progress Tracking
- Shows loading animations during operations
- Provides step-by-step progress updates
- Handles errors gracefully with user-friendly messages

## Architecture

```
TerraCost/
├── main.py                 # CLI entry point
├── services/
│   ├── base_cost_service.py    # Base class for cost services
│   ├── aws_cost_service.py     # AWS-specific cost calculations
│   ├── azure_cost_service.py   # Azure-specific cost calculations
│   ├── terraform_executor.py   # Terraform plan execution
│   ├── progress_indicator.py   # Loading animations and progress
│   ├── terraform_parser.py     # Legacy .tf file parsing
│   └── suggest_service.py      # LLM-based cost suggestions
└── requirements.txt        # Dependencies
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
# For LLM suggestions
export OPENAI_API_KEY="your-api-key-here"

# For AWS (optional, uses default profile)
export AWS_PROFILE="default"
export AWS_REGION="us-east-1"

# For Azure (optional)
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

## Error Handling

The tool provides comprehensive error handling:
- **Terraform Errors**: Clear messages when `terraform plan` fails
- **API Errors**: Retry logic and fallback mechanisms for cloud pricing APIs
- **File Errors**: Helpful suggestions when infrastructure files can't be parsed
- **Legacy Mode**: Automatic fallback to basic parsing when needed

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
3. Add provider detection logic in `terraform_executor.py`
4. Update the main CLI to handle the new provider

## Members

- Daniël van Zyl
- Shailyn Ramsamy Moodley  
- Tevlen Naidoo