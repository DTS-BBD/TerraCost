# TerraCost VSCode Extension

A powerful VSCode extension that brings TerraCost's infrastructure cost estimation and optimization directly into your editor. Get real-time cost estimates, AI-powered optimization suggestions, and inline cost displays for your Terraform files.

## Features

### 🏗️ Sidebar Panel
- **Resources & Costs Tab**: View all infrastructure resources with their monthly costs
- **AI Suggestions Tab**: Get LLM-powered cost optimization recommendations
- **Timeframe Selector**: Choose from 1 month to 2 years for cost projections
- **Real-time Updates**: Automatically refreshes when Terraform files change

### 👻 Ghost Text in .tf Files
- **Inline Cost Display**: See monthly costs directly in your Terraform files
- **Non-intrusive**: Gray text that doesn't interfere with your code
- **Real-time Updates**: Costs update as you modify your infrastructure
- **Tooltips**: Hover for detailed cost breakdowns

### 🚀 Seamless Integration
- **CLI Integration**: Works with your existing TerraCost Python package
- **File Watching**: Automatically detects changes in .tf files
- **Context Menus**: Right-click on .tf files for quick cost calculations
- **Terminal Integration**: Opens dedicated terminal for TerraCost commands

## Installation

### Prerequisites
1. **TerraCost Python Package**: Must be installed in your environment
   ```bash
   cd /path/to/terracost
   pip install -e .
   ```

2. **Python**: Ensure Python is available in your PATH
3. **VSCode**: Version 1.74.0 or higher

### Extension Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Compile the extension:
   ```bash
   npm run compile
   ```
4. Press `F5` in VSCode to run the extension in development mode
5. Or package and install:
   ```bash
   npm run vscode:prepublish
   # Install the generated .vsix file
   ```

## Usage

### Opening the Panel
1. Click the TerraCost icon in the VSCode sidebar (🏗️)
2. The panel opens with two tabs: "Resources & Costs" and "AI Suggestions"

### Calculating Costs
1. **Select Timeframe**: Choose from 1m, 3m, 6m, 1y, or 2y
2. **Click "Calculate Costs"**: Executes `terracost plan` in your workspace
3. **View Results**: See total cost and per-resource breakdown
4. **Check Terminal**: Detailed output appears in the integrated terminal

### Getting AI Suggestions
1. **Click "Get AI Suggestions"**: Executes `terracost suggest --savings`
2. **View Options**: See conservative, moderate, and aggressive optimization strategies
3. **Understand Changes**: Each suggestion includes explanations and risk assessments

### Ghost Text Features
- **Automatic Display**: Cost estimates appear automatically in .tf files
- **Configuration**: Toggle ghost text on/off in VSCode settings
- **Customization**: Adjust colors and display options

## Configuration

### Extension Settings
```json
{
  "terracost.timeframe": "1m",
  "terracost.showGhostText": true,
  "terracost.ghostTextColor": "#6a737d",
  "terracost.pythonPath": "python"
}
```

### Environment Variables
Ensure these are set for full functionality:
```bash
export OPENAI_API_KEY="your-openai-api-key"  # For AI suggestions
export AWS_PROFILE="default"                  # For AWS pricing
export AWS_REGION="us-east-1"                # For AWS pricing
```

## Development

### Project Structure
```
terracost-vscode/
├── src/
│   ├── extension.ts              # Main extension logic
│   ├── webview/                  # Sidebar panel UI
│   │   ├── panel.ts             # Webview panel management
│   │   ├── main.js              # Frontend JavaScript
│   │   └── style.css            # Styling
│   └── providers/               # Core functionality
│       ├── costProvider.ts      # Cost calculation logic
│       └── ghostTextProvider.ts # Inline cost display
├── resources/
│   └── icon.svg                 # Extension icon
└── package.json                 # Extension manifest
```

### Building
```bash
# Development build with watch
npm run watch

# Production build
npm run compile

# Linting
npm run lint

# Testing
npm test
```

### Key Components

#### CostProvider
- Executes TerraCost CLI commands
- Parses output for cost information
- Manages cost caching
- Handles workspace changes

#### GhostTextProvider
- Implements VSCode's InlayHintsProvider
- Shows inline cost estimates
- Updates in real-time
- Configurable display options

#### TerraCostPanel
- Manages the sidebar webview
- Handles user interactions
- Communicates with extension
- Provides responsive UI

## Troubleshooting

### Common Issues

#### TerraCost Command Not Found
- Ensure TerraCost is installed: `pip install -e .`
- Check Python path in extension settings
- Verify workspace has Terraform files

#### No Cost Estimates Displayed
- Check if .tf files are in the workspace
- Verify AWS credentials are configured
- Look for errors in VSCode's Developer Console

#### Ghost Text Not Showing
- Enable ghost text in extension settings
- Ensure .tf files are open
- Check if costs have been calculated

#### AI Suggestions Not Working
- Verify OPENAI_API_KEY is set
- Check internet connectivity
- Ensure Terraform files contain AWS resources

### Debug Mode
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Run "Developer: Toggle Developer Tools"
3. Check Console for error messages
4. Use VSCode's built-in debugging features

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow TypeScript best practices
- Use VSCode's built-in formatting
- Maintain consistent naming conventions
- Add JSDoc comments for public APIs

## Roadmap

### Planned Features
- [ ] Multi-cloud support (Azure, GCP)
- [ ] Cost history tracking
- [ ] Budget alerts and notifications
- [ ] Integration with VSCode's Problems panel
- [ ] Cost comparison between different configurations
- [ ] Export cost reports to various formats

### Known Limitations
- Currently AWS-focused (following TerraCost CLI)
- Requires TerraCost Python package to be installed
- Ghost text updates may have slight delays
- Some complex Terraform configurations may not parse perfectly

## License

This extension is licensed under the MIT License, matching the TerraCost project.

## Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the TerraCost main project for CLI details
- **Community**: Join discussions in the TerraCost repository

---

**Note**: This extension requires the TerraCost Python package to be installed and accessible in your environment. Make sure to follow the main TerraCost project's installation instructions first.