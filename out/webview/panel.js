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
exports.TerraCostPanel = void 0;
const vscode = __importStar(require("vscode"));
class TerraCostPanel {
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (TerraCostPanel.currentPanel) {
            TerraCostPanel.currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel(TerraCostPanel.viewType, 'TerraCost - Infrastructure Costs', column || vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [
                vscode.Uri.joinPath(extensionUri, 'out', 'webview')
            ]
        });
        TerraCostPanel.currentPanel = new TerraCostPanel(panel, extensionUri);
    }
    static revive(panel, extensionUri) {
        TerraCostPanel.currentPanel = new TerraCostPanel(panel, extensionUri);
    }
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._update();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.onDidReceiveMessage(message => {
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
        }, null, this._disposables);
    }
    dispose() {
        TerraCostPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
    async _update() {
        const webview = this._panel.webview;
        this._panel.title = 'TerraCost - Infrastructure Costs';
        // Add debugging
        console.log('Updating webview HTML...');
        const html = this._getHtmlForWebview(webview);
        console.log('HTML generated, length:', html.length);
        this._panel.webview.html = html;
        // Add error handling for webview loading
        this._panel.webview.onDidReceiveMessage(message => {
            console.log('Webview message received:', message);
        }, undefined, this._disposables);
    }
    _getHtmlForWebview(webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'webview', 'main.js'));
        const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'out', 'webview', 'style.css'));
        // Add debugging
        console.log('Script URI:', scriptUri.toString());
        console.log('Style URI:', styleUri.toString());
        console.log('Extension URI:', this._extensionUri.toString());
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TerraCost</title>
    <link rel="stylesheet" href="${styleUri}">
    <style>
        /* Fallback styles in case CSS fails to load */
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007acc; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ TerraCost</h1>
            <p>Infrastructure Cost Estimation & Optimization</p>
            <p style="color: green;">✅ Webview is loading!</p>
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
            <button class="tab-button active" data-tab="resources">📊 Resources & Costs</button>
            <button class="tab-button" data-tab="suggestions">🤖 AI Suggestions</button>
        </div>

        <div class="tab-content">
            <div id="resources-tab" class="tab-pane active">
                <div class="actions">
                    <button id="calculate-btn" class="btn btn-primary">Calculate Costs</button>
                    <button id="refresh-btn" class="btn btn-secondary">Refresh</button>
                </div>
                <div id="resources-content" class="content-area">
                    <div class="loading">Click "Calculate Costs" to analyze your infrastructure</div>
                </div>
            </div>

            <div id="suggestions-tab" class="tab-pane">
                <div class="actions">
                    <button id="suggestions-btn" class="btn btn-primary">Get AI Suggestions</button>
                </div>
                <div id="suggestions-content" class="content-area">
                    <div class="loading">Click "Get AI Suggestions" for optimization recommendations</div>
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
            // Execute TerraCost CLI command
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder found');
                return;
            }
            const terminal = vscode.window.createTerminal('TerraCost');
            terminal.show();
            terminal.sendText(`cd "${workspaceFolder.uri.fsPath}" && terracost plan -t ${timeframe} -f .`);
            // Send message back to webview to show loading state
            this._panel.webview.postMessage({
                command: 'costsCalculating',
                timeframe: timeframe
            });
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
            this._panel.webview.postMessage({
                command: 'suggestionsGenerating'
            });
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${error}`);
        }
    }
    async _handleRefreshCosts() {
        this._panel.webview.postMessage({
            command: 'costsRefreshing'
        });
        // Trigger a refresh of all cost calculations
        vscode.commands.executeCommand('terracost.refreshCosts');
    }
}
exports.TerraCostPanel = TerraCostPanel;
TerraCostPanel.viewType = 'terracostPanel';
//# sourceMappingURL=panel.js.map