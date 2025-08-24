import * as vscode from 'vscode';
import { TerraCostViewProvider } from './webview/viewProvider';

export function activate(context: vscode.ExtensionContext) {
    const provider = new TerraCostViewProvider(context.extensionUri);
    
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(TerraCostViewProvider.viewType, provider)
    );
}



export function deactivate() {}