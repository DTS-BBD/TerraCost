import * as vscode from 'vscode';
import { CostProvider, ResourceCost } from './costProvider';

export class GhostTextProvider implements vscode.InlayHintsProvider {
    private costProvider: CostProvider;
    private showGhostText: boolean;

    constructor(costProvider: CostProvider) {
        this.costProvider = costProvider;
        this.showGhostText = vscode.workspace.getConfiguration('terracost').get('showGhostText', true);
        
        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('terracost.showGhostText')) {
                this.showGhostText = vscode.workspace.getConfiguration('terracost').get('showGhostText', true);
                // Trigger refresh of inlay hints
                this.refreshInlayHints();
            }
        });
    }

    public async provideInlayHints(
        document: vscode.TextDocument,
        range: vscode.Range,
        token: vscode.CancellationToken
    ): Promise<vscode.InlayHint[]> {
        if (!this.showGhostText || document.languageId !== 'terraform') {
            return [];
        }

        const hints: vscode.InlayHint[] = [];
        const text = document.getText(range);
        const lines = text.split('\n');

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const resourceMatch = this.findResourceDefinition(line);
            
            if (resourceMatch) {
                const costHint = await this.createCostHint(
                    document,
                    range.start.line + i,
                    resourceMatch.resourceType,
                    resourceMatch.resourceName
                );
                
                if (costHint) {
                    hints.push(costHint);
                }
            }
        }

        return hints;
    }

    private findResourceDefinition(line: string): { resourceType: string; resourceName: string } | null {
        // Match Terraform resource definitions
        // e.g., "resource "aws_instance" "web_server" {"
        const resourcePattern = /resource\s+"([^"]+)"\s+"([^"]+)"/;
        const match = line.match(resourcePattern);
        
        if (match) {
            return {
                resourceType: match[1],
                resourceName: match[2]
            };
        }

        // Also match data sources
        const dataPattern = /data\s+"([^"]+)"\s+"([^"]+)"/;
        const dataMatch = line.match(dataPattern);
        
        if (dataMatch) {
            return {
                resourceType: dataMatch[1],
                resourceName: dataMatch[2]
            };
        }

        return null;
    }

    private async createCostHint(
        document: vscode.TextDocument,
        line: number,
        resourceType: string,
        resourceName: string
    ): Promise<vscode.InlayHint | null> {
        try {
            // Get cached costs for this file
            const costEstimate = this.costProvider.getCachedCosts(document.uri);
            
            if (!costEstimate) {
                return null;
            }

            // Find the resource cost
            const resourceCost = costEstimate.resources.find(r => 
                r.name === `${resourceType}.${resourceName}` ||
                r.name === resourceName
            );

            if (!resourceCost) {
                return null;
            }

            // Create the inlay hint
            const position = new vscode.Position(line, document.lineAt(line).text.length);
            const hint = new vscode.InlayHint(
                position,
                ` 💰 $${resourceCost.monthlyCost.toFixed(2)}/month`
            );

            // Style the hint
            hint.paddingLeft = true;
            hint.paddingRight = true;

            // Add tooltip with more details
            hint.tooltip = new vscode.MarkdownString(
                `**${resourceType}.${resourceName}**\n\n` +
                `Monthly Cost: $${resourceCost.monthlyCost.toFixed(2)}\n` +
                `Resource Type: ${resourceType}\n\n` +
                `*Cost estimate for ${costEstimate.timeframe} timeframe*`
            );

            return hint;
        } catch (error) {
            console.error('Error creating cost hint:', error);
            return null;
        }
    }

    private refreshInlayHints(): void {
        // Trigger a refresh of inlay hints for all visible editors
        vscode.window.visibleTextEditors.forEach(editor => {
            if (editor.document.languageId === 'terraform') {
                // Force refresh by triggering a document change event
                // This is a workaround since VSCode doesn't provide a direct API to refresh inlay hints
                const range = editor.document.lineAt(0).range;
                editor.revealRange(range, vscode.TextEditorRevealType.AtTop);
            }
        });
    }

    public dispose(): void {
        // Cleanup if needed
    }
}
