import * as vscode from 'vscode';
import * as path from 'path';

export class TerraCostPanel {
    public static currentPanel: TerraCostPanel | undefined;
    public static readonly viewType = 'terracostPanel';

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (TerraCostPanel.currentPanel) {
            TerraCostPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            TerraCostPanel.viewType,
            'TerraCost - Infrastructure Costs',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'out', 'webview')
                ]
            }
        );

        TerraCostPanel.currentPanel = new TerraCostPanel(panel, extensionUri);
    }

    public static revive(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        TerraCostPanel.currentPanel = new TerraCostPanel(panel, extensionUri);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._update();

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
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
            },
            null,
            this._disposables
        );
    }

    public dispose() {
        TerraCostPanel.currentPanel = undefined;

        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private async _update() {
        const webview = this._panel.webview;
        this._panel.title = 'TerraCost - Infrastructure Costs';
        
        // Add debugging
        console.log('Updating webview HTML...');
        const html = this._getHtmlForWebview(webview);
        console.log('HTML generated, length:', html.length);
        
        this._panel.webview.html = html;
        
        // Add error handling for webview loading
        this._panel.webview.onDidReceiveMessage(
            message => {
                console.log('Webview message received:', message);
            },
            undefined,
            this._disposables
        );
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
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

    private async _handleCalculateCosts(timeframe: string) {
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
            
            this._panel.webview.postMessage({ 
                command: 'suggestionsGenerating' 
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${error}`);
        }
    }

    private async _handleRefreshCosts() {
        this._panel.webview.postMessage({ 
            command: 'costsRefreshing' 
        });
        
        // Trigger a refresh of all cost calculations
        vscode.commands.executeCommand('terracost.refreshCosts');
    }
}
