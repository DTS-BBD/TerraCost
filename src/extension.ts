import * as vscode from 'vscode';
import { TerraCostPanel } from './webview/panel';
import { TerraCostViewProvider } from './webview/viewProvider';
import { CostProvider } from './providers/costProvider';
import { GhostTextProvider } from './providers/ghostTextProvider';

let costProvider: CostProvider;
let ghostTextProvider: GhostTextProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('TerraCost extension is now active!');

    // Initialize providers
    costProvider = new CostProvider();
    ghostTextProvider = new GhostTextProvider(costProvider);

    // Register commands
    let openPanelCommand = vscode.commands.registerCommand('terracost.openPanel', () => {
        TerraCostPanel.createOrShow(context.extensionUri);
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
    const viewProvider = vscode.window.registerWebviewViewProvider(
        'terracostPanel',
        new TerraCostViewProvider(context.extensionUri, costProvider)
    );

    // Register ghost text provider
    const ghostTextDisposable = vscode.languages.registerInlayHintsProvider(
        { language: 'terraform' },
        ghostTextProvider
    );

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
    context.subscriptions.push(
        openPanelCommand,
        calculateCostsCommand,
        getSuggestionsCommand,
        refreshCostsCommand,
        viewProvider,
        ghostTextDisposable,
        fileWatcher,
        workspaceChangeListener
    );

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

export function deactivate() {
    if (costProvider) {
        costProvider.dispose();
    }
    if (ghostTextProvider) {
        ghostTextProvider.dispose();
    }
}
