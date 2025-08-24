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
exports.TerraCostViewProvider = void 0;
const vscode = __importStar(require("vscode"));
class TerraCostViewProvider {
    constructor(_extensionUri, _costProvider) {
        this._extensionUri = _extensionUri;
        this._costProvider = _costProvider;
    }
    resolveWebviewView(webviewView, context, _token) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this._extensionUri, 'out', 'webview')
            ]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(message => {
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
        });
    }
    _getHtmlForWebview(webview) {
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
    async _handleCalculateCosts(timeframe) {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }
            const terminal = vscode.window.createTerminal('TerraCost');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && terracost plan -t ${timeframe} -f .`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to calculate costs: ${error}`);
        }
    }
    async _handleGetSuggestions() {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }
            const terminal = vscode.window.createTerminal('TerraCost');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && terracost suggest --savings`);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${error}`);
        }
    }
    async _handleRefreshCosts() {
        this._costProvider.refreshAllCosts();
    }
}
exports.TerraCostViewProvider = TerraCostViewProvider;
TerraCostViewProvider.viewType = 'terracostPanel';
//# sourceMappingURL=viewProvider.js.map