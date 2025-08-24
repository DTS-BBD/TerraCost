/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ([
/* 0 */
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


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
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(__webpack_require__(1));
const viewProvider_1 = __webpack_require__(2);
function activate(context) {
    const provider = new viewProvider_1.TerraCostViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(viewProvider_1.TerraCostViewProvider.viewType, provider));
}
function deactivate() { }


/***/ }),
/* 1 */
/***/ ((module) => {

module.exports = require("vscode");

/***/ }),
/* 2 */
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


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
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.TerraCostViewProvider = void 0;
const vscode = __importStar(__webpack_require__(1));
class TerraCostViewProvider {
    _extensionUri;
    static viewType = 'terracostPanel';
    _webviewView;
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView, context, _token) {
        this._webviewView = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(message => {
            try {
                switch (message.command) {
                    case 'calculateCosts':
                        this._handleCalculateCosts(message.timeframe);
                        return;
                    case 'getSuggestions':
                        this._handleGetSuggestions(message.suggestionType, message.apiKey);
                        return;
                }
            }
            catch (error) {
                vscode.window.showErrorMessage(`Command failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        });
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TerraCost</title>
    <style>
        body { font-family: var(--vscode-font-family); margin: 10px; color: var(--vscode-foreground); }
        .header { text-align: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--vscode-panel-border); }
        .header h2 { color: var(--vscode-textLink-foreground); margin-bottom: 8px; }
        .timeframe-selector { margin-bottom: 15px; }
        .timeframe-selector select { width: 100%; padding: 6px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
        .tabs { display: flex; margin-bottom: 15px; border-bottom: 1px solid var(--vscode-panel-border); }
        .tab-button { flex: 1; padding: 12px; border: none; background: none; cursor: pointer; color: var(--vscode-descriptionForeground); border-bottom: 2px solid transparent; }
        .tab-button.active { color: var(--vscode-textLink-foreground); border-bottom-color: var(--vscode-textLink-foreground); }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        .actions { margin-bottom: 15px; }
        .btn { padding: 8px 16px; margin: 3px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .btn-primary { background: var(--vscode-button-background); color: var(--vscode-button-foreground); }
        .content-area { min-height: 100px; border: 1px solid var(--vscode-panel-border); padding: 10px; background: var(--vscode-editor-background); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2><img src="${webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'icon.png'))}" alt="TerraCost" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;">TerraCost</h2>
            <p style="font-size: 12px; margin: 0;">Infrastructure Cost Estimation</p>
        </div>

        <div class="tabs">
            <button class="tab-button active" data-tab="resources">📊 Costs</button>
            <button class="tab-button" data-tab="suggestions">🤖 AI</button>
        </div>

        <div class="tab-content">
            <div id="resources-tab" class="tab-pane active">
                <div class="timeframe-selector" style="margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <label for="timeframe" style="white-space: nowrap;">Timeframe:</label>
                    <select id="timeframe" style="flex: 1;">
                        <option value="1m">1 Month</option>
                        <option value="3m">3 Months</option>
                        <option value="6m">6 Months</option>
                        <option value="1y">1 Year</option>
                        <option value="2y">2 Years</option>
                    </select>
                </div>
                <div class="actions">
                    <button id="calculate-btn" class="btn btn-primary" style="width: 100%;">Calculate</button>
                </div>

            </div>

            <div id="suggestions-tab" class="tab-pane">
                <div class="suggestion-selector" style="margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <div style="min-width: 120px;">
                        <label for="api-key" style="white-space: nowrap;">API Key 🔑:</label>
                    </div>
                    <input type="password" id="api-key" placeholder="sk-..." style="flex: 1; padding: 6px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border);">
                </div>
                <div class="suggestion-selector" style="margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                    <div style="min-width: 120px;">
                        <label for="suggestion-type" style="white-space: nowrap;">Suggestion Type:</label>
                    </div>
                    <select id="suggestion-type" style="flex: 1; padding: 6px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border);">
                        <option value="--savings">💰 Cost Savings Opportunities</option>
                        <option value="--bestvalue">🎯 Best Value Configuration</option>
                        <option value="--budget">💵 Budget Optimization</option>
                    </select>
                </div>
                <div class="budget-input" id="budget-input" style="display: none; margin-bottom: 15px;">
                    <label for="budget-amount">Monthly Budget ($):</label>
                    <input type="number" id="budget-amount" placeholder="50.0" step="0.01" min="0" style="width: 100%; padding: 6px; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border);">
                </div>
                <div class="actions">
                    <button id="suggestions-btn" class="btn btn-primary" style="width: 100%;">Get Suggestions</button>
                </div>
                <div id="suggestions-content" class="content-area">
                    <div style="text-align: center; color: #666;">
                        <p><strong>🤖 AI Suggestions Ready</strong></p>
                        <p>Enter your OpenAI API key above and select a suggestion type to get started.</p>
                        <p style="font-size: 11px; margin-top: 10px;">Your API key is only used for this session and is not stored.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        // Restore active tab from state
        const state = vscode.getState();
        const activeTab = state?.activeTab || 'resources';
        
        // Set initial active tab
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
        
        const activeButton = document.querySelector('[data-tab="' + activeTab + '"]');
        const activePane = document.getElementById(activeTab + '-tab');
        
        if (activeButton && activePane) {
            activeButton.classList.add('active');
            activePane.classList.add('active');
        } else {
            // Fallback to resources tab if something goes wrong
            document.querySelector('[data-tab="resources"]').classList.add('active');
            document.getElementById('resources-tab').classList.add('active');
        }
        
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Update active tab
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
                document.getElementById(targetTab + '-tab').classList.add('active');
                
                // Save active tab to state
                vscode.setState({ ...state, activeTab: targetTab });
            });
        });

        document.getElementById('calculate-btn').addEventListener('click', () => {
            const timeframe = document.getElementById('timeframe').value;
            vscode.postMessage({ command: 'calculateCosts', timeframe: timeframe });
        });

        // Handle suggestion type change to show/hide budget input
        document.getElementById('suggestion-type').addEventListener('change', () => {
            const suggestionType = document.getElementById('suggestion-type').value;
            const budgetInput = document.getElementById('budget-input');
            if (suggestionType === '--budget') {
                budgetInput.style.display = 'block';
            } else {
                budgetInput.style.display = 'none';
            }
        });

        document.getElementById('suggestions-btn').addEventListener('click', () => {
            const apiKey = document.getElementById('api-key').value.trim();
            if (!apiKey) {
                alert('Please enter your OpenAI API key');
                return;
            }
            
            const suggestionType = document.getElementById('suggestion-type').value;
            let args = suggestionType;
            
            if (suggestionType === '--budget') {
                const budgetAmount = document.getElementById('budget-amount').value;
                if (budgetAmount) {
                    args = suggestionType + ' ' + budgetAmount;
                }
            }
            
            vscode.postMessage({ 
                command: 'getSuggestions', 
                suggestionType: args,
                apiKey: apiKey
            });
        });


    </script>
</body>
</html>`;
    }
    async _handleCalculateCosts(timeframe) {
        try {
            const workspaceFolder = this.getWorkspaceFolder();
            const sanitizedTimeframe = this.sanitizeTimeframe(timeframe);
            const terraformDir = this.getTerraformDir(workspaceFolder);
            const terracostPath = this.getTerracostExecutable();
            const terminal = vscode.window.createTerminal('TerraCost Terminal');
            terminal.show();
            terminal.sendText(`chcp 65001; & "${terracostPath}" plan -t ${sanitizedTimeframe} -f .`);
        }
        catch (error) {
            const errorMsg = `Failed to calculate costs: ${error instanceof Error ? error.message : 'Unknown error'}`;
            vscode.window.showErrorMessage(errorMsg);
        }
    }
    async _handleGetSuggestions(suggestionType = '--savings', apiKey) {
        try {
            const workspaceFolder = this.getWorkspaceFolder();
            const terraformDir = this.getTerraformDir(workspaceFolder);
            const terracostPath = this.getTerracostExecutable();
            const terminal = vscode.window.createTerminal('TerraCost Terminal');
            terminal.show();
            // Set the API key and run the command in a single session
            if (apiKey) {
                terminal.sendText(`chcp 65001; $env:OPENAI_API_KEY = "${apiKey}"; echo "API key set successfully"; & "${terracostPath}" suggest ${suggestionType}`);
            }
            else {
                terminal.sendText(`chcp 65001; echo "No API key provided"; & "${terracostPath}" suggest ${suggestionType}`);
            }
        }
        catch (error) {
            const errorMsg = `Failed to get suggestions: ${error instanceof Error ? error.message : 'Unknown error'}`;
            vscode.window.showErrorMessage(errorMsg);
        }
    }
    getWorkspaceFolder() {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            throw new Error('No workspace folder found');
        }
        return workspaceFolder;
    }
    sanitizeTimeframe(timeframe) {
        const validTimeframes = ['1m', '3m', '6m', '1y', '2y'];
        if (!validTimeframes.includes(timeframe)) {
            throw new Error(`Invalid timeframe: ${timeframe}`);
        }
        return timeframe;
    }
    getTerraformDir(workspaceFolder) {
        return workspaceFolder.uri.fsPath;
    }
    getTerracostExecutable() {
        return vscode.Uri.joinPath(this._extensionUri, 'python', 'windows', 'terracost.exe').fsPath;
    }
}
exports.TerraCostViewProvider = TerraCostViewProvider;


/***/ })
/******/ 	]);
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = __webpack_require__(0);
/******/ 	module.exports = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=extension.js.map