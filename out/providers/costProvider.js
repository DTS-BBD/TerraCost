"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CostProvider = void 0;
const vscode = __importStar(require("vscode"));
const cp = __importStar(require("child_process"));
class CostProvider {
    constructor() {
        this.costCache = new Map();
        this.pythonPath = vscode.workspace.getConfiguration('terracost').get('pythonPath', 'python');
    }
    async calculateCostsForFile(uri) {
        try {
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
            if (!workspaceFolder) {
                return null;
            }
            const cacheKey = `${workspaceFolder.uri.fsPath}_${uri.fsPath}`;
            if (this.costCache.has(cacheKey)) {
                return this.costCache.get(cacheKey) || null;
            }
            // Execute TerraCost CLI
            const result = await this.executeTerraCostCommand(workspaceFolder.uri.fsPath, 'plan', ['-f', '.']);
            if (result) {
                const costEstimate = this.parseTerraCostOutput(result);
                this.costCache.set(cacheKey, costEstimate);
                return costEstimate;
            }
            return null;
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to calculate costs: ${error}`);
            return null;
        }
    }
    async getSuggestionsForFile(uri) {
        try {
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
            if (!workspaceFolder) {
                return [];
            }
            // Execute TerraCost suggestions command
            const result = await this.executeTerraCostCommand(workspaceFolder.uri.fsPath, 'suggest', ['--savings']);
            if (result) {
                return this.parseSuggestionsOutput(result);
            }
            return [];
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${error}`);
            return [];
        }
    }
    async refreshAllCosts() {
        this.costCache.clear();
        // Recalculate costs for all open .tf files
        const openDocuments = vscode.workspace.textDocuments.filter(doc => doc.languageId === 'terraform');
        for (const doc of openDocuments) {
            await this.calculateCostsForFile(doc.uri);
        }
    }
    getCachedCosts(uri) {
        const workspaceFolder = vscode.workspace.getWorkspaceFolder(uri);
        if (!workspaceFolder) {
            return null;
        }
        const cacheKey = `${workspaceFolder.uri.fsPath}_${uri.fsPath}`;
        return this.costCache.get(cacheKey) || null;
    }
    async executeTerraCostCommand(workspacePath, command, args) {
        return new Promise((resolve, reject) => {
            const fullCommand = `${this.pythonPath} -m terracost ${command} ${args.join(' ')}`;
            const childProcess = cp.exec(fullCommand, {
                cwd: workspacePath,
                timeout: 60000,
                env: { ...process.env }
            });
            let stdout = '';
            let stderr = '';
            childProcess.stdout?.on('data', (data) => {
                stdout += data.toString();
            });
            childProcess.stderr?.on('data', (data) => {
                stderr += data.toString();
            });
            childProcess.on('close', (code) => {
                if (code === 0) {
                    resolve(stdout);
                }
                else {
                    reject(new Error(`TerraCost command failed with code ${code}: ${stderr}`));
                }
            });
            childProcess.on('error', (error) => {
                reject(new Error(`Failed to execute TerraCost command: ${error.message}`));
            });
        });
    }
    parseTerraCostOutput(output) {
        // Parse the CLI output to extract cost information
        // This is a simplified parser - you might want to enhance it based on actual output format
        const lines = output.split('\n');
        const resources = [];
        let totalCost = 0;
        let timeframe = '1m';
        // Look for cost breakdown patterns
        for (const line of lines) {
            // Parse resource costs (e.g., "aws_instance.web_server: $15.20/month")
            const resourceMatch = line.match(/^([^:]+):\s*\$([\d.]+)\/month/);
            if (resourceMatch) {
                const resourceName = resourceMatch[1].trim();
                const monthlyCost = parseFloat(resourceMatch[2]);
                if (!isNaN(monthlyCost)) {
                    const resourceType = this.extractResourceType(resourceName);
                    resources.push({
                        name: resourceName,
                        monthlyCost: monthlyCost,
                        resourceType: resourceType
                    });
                    totalCost += monthlyCost;
                }
            }
            // Parse total cost
            const totalMatch = line.match(/Total Cost:\s*\$([\d.]+)/);
            if (totalMatch) {
                totalCost = parseFloat(totalMatch[1]);
            }
            // Parse timeframe
            const timeframeMatch = line.match(/for\s+([\d.]+)\s+month\(s\)/);
            if (timeframeMatch) {
                timeframe = timeframeMatch[1] + 'm';
            }
        }
        return {
            totalCost: totalCost,
            resources: resources,
            timeframe: timeframe
        };
    }
    parseSuggestionsOutput(output) {
        // Parse AI suggestions output
        const suggestions = [];
        const lines = output.split('\n');
        let currentSuggestion = {};
        let inSuggestion = false;
        for (const line of lines) {
            // Look for suggestion patterns
            if (line.includes('Option') && line.includes(':')) {
                if (inSuggestion && Object.keys(currentSuggestion).length > 0) {
                    suggestions.push(currentSuggestion);
                }
                currentSuggestion = {};
                inSuggestion = true;
                const optionMatch = line.match(/Option\s+(\d+):\s*(.+)/);
                if (optionMatch) {
                    currentSuggestion.type = optionMatch[2].trim();
                }
            }
            // Parse savings percentage
            const savingsMatch = line.match(/Estimated Savings:\s*(\d+)%/);
            if (savingsMatch) {
                currentSuggestion.savingsPercent = parseInt(savingsMatch[1]);
            }
            // Parse new cost
            const costMatch = line.match(/New Monthly Cost:\s*\$([\d.]+)/);
            if (costMatch) {
                currentSuggestion.newCost = parseFloat(costMatch[1]);
            }
            // Parse explanation
            if (line.includes('Explanation:')) {
                const explanationStart = line.indexOf('Explanation:') + 'Explanation:'.length;
                currentSuggestion.explanation = line.substring(explanationStart).trim();
            }
        }
        // Add the last suggestion
        if (inSuggestion && Object.keys(currentSuggestion).length > 0) {
            suggestions.push(currentSuggestion);
        }
        return suggestions;
    }
    extractResourceType(resourceName) {
        // Extract resource type from Terraform resource name
        // e.g., "aws_instance.web_server" -> "aws_instance"
        const parts = resourceName.split('.');
        return parts[0] || 'unknown';
    }
    dispose() {
        this.costCache.clear();
    }
}
exports.CostProvider = CostProvider;
//# sourceMappingURL=costProvider.js.map