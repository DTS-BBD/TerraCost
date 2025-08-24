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
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const panel_1 = require("./webview/panel");
const viewProvider_1 = require("./webview/viewProvider");
const costProvider_1 = require("./providers/costProvider");
const ghostTextProvider_1 = require("./providers/ghostTextProvider");
let costProvider;
let ghostTextProvider;
function activate(context) {
    console.log('TerraCost extension is now active!');
    // Initialize providers
    costProvider = new costProvider_1.CostProvider();
    ghostTextProvider = new ghostTextProvider_1.GhostTextProvider(costProvider);
    // Register commands
    let openPanelCommand = vscode.commands.registerCommand('terracost.openPanel', () => {
        panel_1.TerraCostPanel.createOrShow(context.extensionUri);
    });
    let calculateCostsCommand = vscode.commands.registerCommand('terracost.calculateCosts', () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && activeEditor.document.languageId === 'terraform') {
            costProvider.calculateCostsForFile(activeEditor.document.uri);
        }
    });
    let getSuggestionsCommand = vscode.commands.registerCommand('terracost.getSuggestions', () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && activeEditor.document.languageId === 'terraform') {
            costProvider.getSuggestionsForFile(activeEditor.document.uri);
        }
    });
    let refreshCostsCommand = vscode.commands.registerCommand('terracost.refreshCosts', () => {
        costProvider.refreshAllCosts();
    });
    // Register webview view provider for sidebar
    const viewProvider = vscode.window.registerWebviewViewProvider('terracostPanel', new viewProvider_1.TerraCostViewProvider(context.extensionUri, costProvider));
    // Register ghost text provider
    const ghostTextDisposable = vscode.languages.registerInlayHintsProvider({ language: 'terraform' }, ghostTextProvider);
    // Register file watcher for .tf files
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.tf');
    fileWatcher.onDidChange((uri) => {
        if (vscode.workspace.getConfiguration('terracost').get('showGhostText')) {
            costProvider.calculateCostsForFile(uri);
        }
    });
    // Register workspace change listener
    const workspaceChangeListener = vscode.workspace.onDidChangeWorkspaceFolders(() => {
        costProvider.refreshAllCosts();
    });
    // Add commands to context
    context.subscriptions.push(openPanelCommand, calculateCostsCommand, getSuggestionsCommand, refreshCostsCommand, viewProvider, ghostTextDisposable, fileWatcher, workspaceChangeListener);
    // Auto-calculate costs for open .tf files
    vscode.workspace.textDocuments.forEach(doc => {
        if (doc.languageId === 'terraform') {
            costProvider.calculateCostsForFile(doc.uri);
        }
    });
    // Listen for new documents
    vscode.workspace.onDidOpenTextDocument((doc) => {
        if (doc.languageId === 'terraform') {
            costProvider.calculateCostsForFile(doc.uri);
        }
    });
}
exports.activate = activate;
function deactivate() {
    if (costProvider) {
        costProvider.dispose();
    }
    if (ghostTextProvider) {
        ghostTextProvider.dispose();
    }
}
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map