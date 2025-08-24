<div align="center">
  <img src="resources/icon.png" alt="TerraCost Logo" width="200" height="200">
</div>

# TerraCost

**Multi-cloud Terraform cost estimation and AI-powered optimization tool**

TerraCost is a comprehensive solution that scans your Terraform infrastructure files, estimates costs across AWS, Azure, and GCP, and provides AI-powered suggestions to optimize your cloud spending. Available as both a CLI tool and VS Code extension.

## ✨ Features

### 🌐 Multi-Cloud Support
- **AWS**: EC2, S3, Lambda, RDS, and more
- **Azure**: Virtual Machines, Storage Accounts, App Services
- **GCP**: Compute Engine, Cloud Storage, Cloud Functions
- **Unified Cost Analysis**: Compare costs across providers

### 🤖 AI-Powered Optimization
- **Budget Optimization**: Fit infrastructure within target budget
- **Cost Savings**: Conservative, moderate, and aggressive strategies
- **Best Value**: Optimal cost-performance balance
- **Smart Suggestions**: LLM-powered infrastructure recommendations

### 🚀 CI/CD Integration
- **Budget Enforcement**: Prevent pipeline execution if costs exceed limits
- **Cost Monitoring**: Track spending trends and growth rates
- **Automated Checks**: Integrate cost validation into your deployment pipeline

### 📊 Advanced Analytics
- **Cost Uncertainty Analysis**: Statistical confidence intervals
- **Timeframe Flexibility**: 1 month to 2 years projections
- **Resource Breakdown**: Detailed per-resource cost analysis
- **Real-time Updates**: Automatic refresh when files change

## 🛠️ Installation

### CLI Tool

View details here: [terracost · PyPi](https://pypi.org/project/terracost/)

```bash
# Install from PyPI
pip install terracost

# Or install from source
git clone https://github.com/DTS-BBD/TerraCost.git
cd terracost
pip install -e .
```

**Requirements**: Python 3.8+

### VS Code Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "TerraCost"
4. Click Install
5. An icon will appear on the extension sidebar
6. Click the TerraCost icon to open the extension's panel
7. Enjoy!

Or visit: [TerraCost · VSCode Extension Marketplace](https://marketplace.visualstudio.com/items?itemName=shailyn1739.TerraCost)

## 🚀 Basic Usage

### Cost Estimation

```bash
# Estimate costs for your Terraform infrastructure
terracost plan -f infrastructure/

# Specify timeframe (1m, 3m, 6m, 1y, 2y)
terracost plan -f . -t 6m

# Detailed breakdown
terracost plan -f . --verbose

# Get help and a list of all commands
terracost --help
```

### AI-Powered Suggestions

```bash
# Get cost savings recommendations
terracost suggest --savings

# Fit infrastructure within budget
terracost suggest --budget 50.0

# Find best value configuration
terracost suggest --bestvalue
```

### CI/CD Budget Enforcement

```bash
# Check if costs exceed $2000/month limit
terracost budget --limit 2000 -f infrastructure/
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for AI suggestions
export OPENAI_API_KEY="your-openai-api-key"

# AWS credentials (optional, for enhanced pricing)
export AWS_PROFILE="default"
export AWS_REGION="us-east-1"

# Azure credentials (optional)
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"

# GCP credentials (optional)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 📁 Supported Infrastructure

### AWS Resources
- **Compute**: EC2 instances, Lambda functions, ECS services
- **Storage**: S3 buckets, EBS volumes, RDS databases
- **Networking**: VPC, Load Balancers, API Gateway
- **Security**: IAM roles, Security Groups, KMS keys

### Azure Resources
- **Compute**: Virtual Machines, App Services, Functions
- **Storage**: Storage Accounts, Blob Containers, SQL Databases
- **Networking**: Virtual Networks, Load Balancers, Application Gateway
- **Security**: Key Vault, Network Security Groups

### GCP Resources
- **Compute**: Compute Engine, Cloud Functions, App Engine
- **Storage**: Cloud Storage, Cloud SQL, BigQuery
- **Networking**: VPC, Load Balancing, Cloud Armor
- **Security**: IAM, Cloud KMS, Security Command Center

## 🎯 AI Suggestion Types

### Budget Optimization (`--budget`)
- Analyzes current infrastructure costs
- Suggests modifications to fit within target budget
- Provides risk assessment for each change
- Includes cost estimates for alternatives

### Cost Savings (`--savings`)
- **Conservative**: Safe changes with minimal risk
- **Moderate**: Balanced optimization with some risk
- **Aggressive**: Maximum savings with higher risk
- Detailed explanations for each strategy

### Best Value (`--bestvalue`)
- Optimizes cost-performance ratio
- Considers reliability and scalability
- Balances upfront vs. ongoing costs
- Recommends resource sizing optimizations

## 🔄 CI/CD Integration

### Pipeline Budget Check

```bash
# In your CI/CD pipeline
terracost budget --limit 2000 -f infrastructure/
if [ $? -ne 0 ]; then
    echo "❌ Costs exceed budget limit!"
    exit 1
fi
```

### Cost Growth Monitoring

The tool automatically:
- Tracks cost changes between pipeline runs
- Warns about excessive cost growth (>50% by default)
- Provides detailed cost breakdowns
- Saves cost reports for historical analysis

## 🎨 VS Code Extension Features

### Sidebar Panel
- **Costs Tab**: View infrastructure costs with timeframe selection
- **AI Tab**: Get optimization suggestions directly in VS Code

## 📊 Example Output

### Cost Estimation
```
📊 Infrastructure Analysis
   📁 Directory: ./infrastructure
   🔧 Total Resources: 15
   [AWS] AWS: 8 resources
   [AZURE] AZURE: 4 resources
   [GCP] GCP: 3 resources

💰 Total Cost: $247.83/month
📈 Cost Uncertainty Analysis:
   📊 68% Confidence: $235.12 - $260.54
   📊 95% Confidence: $222.41 - $273.25
   📊 Volatility: 8.2% monthly variation
```

### AI Suggestions
```
🤖 AI-Powered Cost Optimization Suggestions

📋 Conservative Strategy (Low Risk):
   💰 Estimated Savings: 15-20%
   🔧 Changes: Instance type optimization, storage tier adjustments
   ⚠️ Risk: Minimal impact on performance

📋 Moderate Strategy (Balanced):
   💰 Estimated Savings: 25-35%
   🔧 Changes: Reserved instances, auto-scaling policies
   ⚠️ Risk: Some performance variability

📋 Aggressive Strategy (High Risk):
   💰 Estimated Savings: 40-50%
   🔧 Changes: Spot instances, aggressive scaling
   ⚠️ Risk: Potential downtime during scaling
```

## 🏗️ Architecture

### Core Components
- **Terraform Parser**: Extracts resources from .tf files
- **Cost Services**: Provider-specific pricing calculations
- **AI Service**: OpenAI integration for suggestions
- **Progress Tracking**: Real-time operation monitoring
- **CI/CD Service**: Pipeline budget enforcement

### Supported Providers
- **AWS**: Boto3 integration for pricing
- **Azure**: Azure SDK for cost estimation
- **GCP**: Google Cloud client libraries
- **Multi-cloud**: Unified cost analysis across providers

## 🚧 Requirements

### CLI Tool
- Python 3.8+
- Terraform files (.tf) in your project
- OpenAI API key (for AI suggestions)
- Cloud provider credentials (optional, for enhanced pricing)

### VS Code Extension
- VS Code 1.103.0+

## 🔍 Troubleshooting

### Common Issues

#### No Cost Estimates Displayed
- Verify .tf files are in the specified directory
- Check if Terraform configuration is valid
- Ensure cloud provider credentials are configured

#### AI Suggestions Not Working
- Verify `OPENAI_API_KEY` is set
- Check internet connectivity
- Ensure Terraform files contain cloud resources

#### CI/CD Pipeline Fails
- Check budget limits are reasonable
- Verify cost estimation is working locally
- Review cost growth warnings

### Debug Mode
```bash
# Enable verbose output
terracost plan -f . --verbose

# Check version
terracost --version
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/yourusername/terracost.git
cd terracost
pip install -e .
npm install  # For VS Code extension
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on [GitHub](https://github.com/yourusername/terracost/issues)
- **Documentation**: Check the [Wiki](https://github.com/yourusername/terracost/wiki) for detailed guides
- **Community**: Join discussions in the [GitHub Discussions](https://github.com/yourusername/terracost/discussions)

---

**Made with ❤️ by the TerraCost team**

Members:
- Daniël van Zyl
- Shailyn Ramsamy Moodley
- Tevlen Naidoo

*TerraCost helps you build cost-effective cloud infrastructure without compromising on performance or reliability.*
