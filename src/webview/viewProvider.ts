import * as vscode from 'vscode';
import { CostProvider } from '../providers/costProvider';

export class TerraCostViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'terracostPanel';

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _costProvider: CostProvider
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this._extensionUri, 'out', 'webview')
            ]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'calculateCosts':
                        this._handleCalculateCosts(message.timeframe);
                        return;
                    case 'getSuggestions':
                        this._handleGetSuggestions();
                        return;
                    case 'refreshCosts':
                        this._handleRefreshCosts();
                        return;
                }
            }
        );
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'webview', 'main.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'webview', 'style.css'));

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TerraCost</title>
    <link rel="stylesheet" href="${styleUri}">
    <style>
        /* Fallback styles in case CSS fails to load */
        body { font-family: Arial, sans-serif; margin: 10px; }
        .container { max-width: 100%; }
        .header { text-align: center; margin-bottom: 20px; }
        .btn { padding: 8px 16px; margin: 3px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .btn-primary { background: #007acc; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .timeframe-selector { margin-bottom: 15px; }
        .timeframe-selector select { width: 100%; padding: 5px; }
        .tabs { display: flex; margin-bottom: 15px; }
        .tab-button { flex: 1; padding: 8px; border: 1px solid #ccc; background: #f8f9fa; cursor: pointer; }
        .tab-button.active { background: #007acc; color: white; }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        .content-area { min-height: 100px; border: 1px solid #ddd; padding: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🏗️ TerraCost</h2>
            <p style="font-size: 12px; margin: 0;">Infrastructure Cost Estimation</p>
        </div>

        <div class="timeframe-selector">
            <label for="timeframe">Timeframe:</label>
            <select id="timeframe">
                <option value="1m">1 Month</option>
                <option value="3m">3 Months</option>
                <option value="6m">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
            </select>
        </div>

        <div class="tabs">
            <button class="tab-button active" data-tab="resources">📊 Costs</button>
            <button class="tab-button" data-tab="suggestions">🤖 AI</button>
        </div>

        <div class="tab-content">
            <div id="resources-tab" class="tab-pane active">
                <div class="actions">
                    <button id="calculate-btn" class="btn btn-primary">Calculate</button>
                    <button id="refresh-btn" class="btn btn-secondary">Refresh</button>
                </div>
                <div id="resources-content" class="content-area">
                    <div style="text-align: center; color: #666;">Click "Calculate" to analyze infrastructure</div>
                </div>
            </div>

            <div id="suggestions-tab" class="tab-pane">
                <div class="actions">
                    <button id="suggestions-btn" class="btn btn-primary">Get Suggestions</button>
                </div>
                <div id="suggestions-content" class="content-area">
                    <div style="text-align: center; color: #666;">Click for optimization tips</div>
                </div>
            </div>
        </div>
    </div>

    <script src="${scriptUri}"></script>
</body>
</html>`;
    }

    private async _handleCalculateCosts(timeframe: string) {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            const terminal = vscode.window.createTerminal('TerraCost');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && terracost plan -t ${timeframe} -f .`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to calculate costs: ${error}`);
        }
    }

    private async _handleGetSuggestions() {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }

            const terminal = vscode.window.createTerminal('TerraCost');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && terracost suggest --savings`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${error}`);
        }
    }

    private async _handleRefreshCosts() {
        this._costProvider.refreshAllCosts();
    }
}
