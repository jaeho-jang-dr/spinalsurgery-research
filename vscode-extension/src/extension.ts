import * as vscode from 'vscode';
import { ResearchDashboardPanel } from './panels/ResearchDashboardPanel';
import { ClaudeIntegration } from './services/ClaudeIntegration';
import { ResearchProjectProvider } from './providers/ResearchProjectProvider';
import { DataExplorerProvider } from './providers/DataExplorerProvider';
import { BibliographyProvider } from './providers/BibliographyProvider';
import { AIAssistantProvider } from './providers/AIAssistantProvider';
import { ResearchAPI } from './api/ResearchAPI';

export function activate(context: vscode.ExtensionContext) {
    console.log('SpinalSurgery Research Platform is now active!');

    // Initialize API connection
    const api = new ResearchAPI(context);
    
    // Initialize Claude integration
    const claudeIntegration = new ClaudeIntegration(context);

    // Register tree data providers
    const projectProvider = new ResearchProjectProvider(api);
    const dataProvider = new DataExplorerProvider(api);
    const bibliographyProvider = new BibliographyProvider(api);
    const aiProvider = new AIAssistantProvider(claudeIntegration);

    vscode.window.createTreeView('spinalsurgery.projectExplorer', {
        treeDataProvider: projectProvider,
        showCollapseAll: true
    });

    vscode.window.createTreeView('spinalsurgery.dataExplorer', {
        treeDataProvider: dataProvider
    });

    vscode.window.createTreeView('spinalsurgery.bibliography', {
        treeDataProvider: bibliographyProvider
    });

    vscode.window.createTreeView('spinalsurgery.aiAssistant', {
        treeDataProvider: aiProvider
    });

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('spinalsurgery.openDashboard', () => {
            ResearchDashboardPanel.createOrShow(context.extensionUri, api);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('spinalsurgery.newResearch', async () => {
            const projectName = await vscode.window.showInputBox({
                prompt: 'Enter research project name',
                placeHolder: 'e.g., Lumbar Spine Surgery Outcomes Study'
            });

            if (projectName) {
                const projectType = await vscode.window.showQuickPick([
                    'Clinical Study',
                    'Literature Review',
                    'Meta-Analysis',
                    'Case Report',
                    'Research Protocol'
                ], {
                    placeHolder: 'Select project type'
                });

                if (projectType) {
                    try {
                        const project = await api.createProject({
                            name: projectName,
                            type: projectType,
                            description: ''
                        });

                        // Create project folder structure
                        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
                        if (workspaceFolder) {
                            const projectPath = vscode.Uri.joinPath(
                                workspaceFolder.uri,
                                'research-projects',
                                project.id
                            );

                            // Create directories
                            await vscode.workspace.fs.createDirectory(projectPath);
                            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectPath, 'data'));
                            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectPath, 'references'));
                            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectPath, 'drafts'));
                            await vscode.workspace.fs.createDirectory(vscode.Uri.joinPath(projectPath, 'figures'));

                            // Create initial files
                            const readme = `# ${projectName}\n\nType: ${projectType}\nCreated: ${new Date().toISOString()}\n\n## Overview\n\n## Objectives\n\n## Methods\n\n## Progress\n`;
                            await vscode.workspace.fs.writeFile(
                                vscode.Uri.joinPath(projectPath, 'README.md'),
                                Buffer.from(readme)
                            );

                            // Open the project
                            const doc = await vscode.workspace.openTextDocument(
                                vscode.Uri.joinPath(projectPath, 'README.md')
                            );
                            await vscode.window.showTextDocument(doc);

                            // Ask Claude for initial suggestions
                            const suggestions = await claudeIntegration.getProjectSuggestions(projectName, projectType);
                            if (suggestions) {
                                const suggestionsDoc = await vscode.workspace.openTextDocument({
                                    content: suggestions,
                                    language: 'markdown'
                                });
                                await vscode.window.showTextDocument(suggestionsDoc, vscode.ViewColumn.Beside);
                            }
                        }

                        projectProvider.refresh();
                        vscode.window.showInformationMessage(`Research project '${projectName}' created successfully!`);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Failed to create project: ${error}`);
                    }
                }
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('spinalsurgery.claudeChat', async () => {
            const editor = vscode.window.activeTextEditor;
            let initialText = '';

            if (editor && editor.selection && !editor.selection.isEmpty) {
                initialText = editor.document.getText(editor.selection);
            }

            const panel = vscode.window.createWebviewPanel(
                'claudeChat',
                'Claude AI Assistant',
                vscode.ViewColumn.Beside,
                {
                    enableScripts: true,
                    retainContextWhenHidden: true
                }
            );

            panel.webview.html = getClaudeChatHTML(panel.webview, context.extensionUri, initialText);

            // Handle messages from webview
            panel.webview.onDidReceiveMessage(
                async message => {
                    switch (message.command) {
                        case 'sendMessage':
                            const response = await claudeIntegration.sendMessage(message.text, message.context);
                            panel.webview.postMessage({
                                command: 'receiveMessage',
                                text: response
                            });
                            break;
                        case 'insertText':
                            if (editor) {
                                editor.edit(editBuilder => {
                                    editBuilder.insert(editor.selection.active, message.text);
                                });
                            }
                            break;
                    }
                },
                undefined,
                context.subscriptions
            );
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('spinalsurgery.searchPapers', async () => {
            const searchQuery = await vscode.window.showInputBox({
                prompt: 'Enter search keywords',
                placeHolder: 'e.g., lumbar spine surgery outcomes'
            });

            if (searchQuery) {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Searching academic papers...',
                    cancellable: true
                }, async (progress, token) => {
                    try {
                        const results = await api.searchPapers(searchQuery);
                        
                        // Display results in a new document
                        const content = formatSearchResults(results);
                        const doc = await vscode.workspace.openTextDocument({
                            content: content,
                            language: 'markdown'
                        });
                        await vscode.window.showTextDocument(doc);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Search failed: ${error}`);
                    }
                });
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('spinalsurgery.analyzeData', async () => {
            const dataFile = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectFolders: false,
                canSelectMany: false,
                filters: {
                    'Data Files': ['csv', 'xlsx', 'json'],
                    'All Files': ['*']
                }
            });

            if (dataFile && dataFile[0]) {
                // Open data analysis view
                const panel = vscode.window.createWebviewPanel(
                    'dataAnalysis',
                    'Data Analysis',
                    vscode.ViewColumn.Active,
                    {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    }
                );

                panel.webview.html = getDataAnalysisHTML(panel.webview, context.extensionUri, dataFile[0]);
            }
        })
    );

    // Auto-save functionality
    const autoSaveInterval = vscode.workspace.getConfiguration('spinalsurgery').get<number>('autoSaveInterval', 300);
    setInterval(() => {
        vscode.workspace.textDocuments.forEach(doc => {
            if (doc.isDirty && doc.fileName.includes('research-projects')) {
                doc.save();
            }
        });
    }, autoSaveInterval * 1000);

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(beaker) Research Mode';
    statusBarItem.tooltip = 'SpinalSurgery Research Platform Active';
    statusBarItem.command = 'spinalsurgery.openDashboard';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Language features for medical terms
    const medicalTermsProvider = vscode.languages.registerCompletionItemProvider(
        'markdown',
        {
            provideCompletionItems(document, position) {
                const linePrefix = document.lineAt(position).text.substr(0, position.character);
                if (!linePrefix.endsWith(' ')) {
                    return undefined;
                }

                // Medical terms suggestions
                const suggestions = [
                    'lumbar spine',
                    'cervical spine',
                    'thoracic spine',
                    'intervertebral disc',
                    'spinal stenosis',
                    'spondylolisthesis',
                    'herniated disc',
                    'spinal fusion',
                    'laminectomy',
                    'discectomy'
                ].map(term => {
                    const item = new vscode.CompletionItem(term, vscode.CompletionItemKind.Text);
                    item.detail = 'Medical term';
                    return item;
                });

                return suggestions;
            }
        },
        ' '
    );

    context.subscriptions.push(medicalTermsProvider);
}

function getClaudeChatHTML(webview: vscode.Webview, extensionUri: vscode.Uri, initialText: string): string {
    const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'claude-chat.js'));
    const styleUri = webview.asWebviewUri(vscode.Uri.joinPath(extensionUri, 'media', 'claude-chat.css'));

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="${styleUri}" rel="stylesheet">
        <title>Claude AI Assistant</title>
    </head>
    <body>
        <div id="chat-container">
            <div id="messages"></div>
            <div id="input-container">
                <textarea id="message-input" placeholder="Ask Claude for help with your research...">${initialText}</textarea>
                <button id="send-button">Send</button>
            </div>
        </div>
        <script src="${scriptUri}"></script>
    </body>
    </html>`;
}

function getDataAnalysisHTML(webview: vscode.Webview, extensionUri: vscode.Uri, dataFile: vscode.Uri): string {
    // Implementation for data analysis view
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Data Analysis</title>
    </head>
    <body>
        <h1>Data Analysis View</h1>
        <p>Analyzing: ${dataFile.fsPath}</p>
    </body>
    </html>`;
}

function formatSearchResults(results: any[]): string {
    let content = '# Paper Search Results\n\n';
    results.forEach((paper, index) => {
        content += `## ${index + 1}. ${paper.title}\n`;
        content += `**Authors**: ${paper.authors}\n`;
        content += `**Journal**: ${paper.journal}\n`;
        content += `**Year**: ${paper.year}\n`;
        content += `**Abstract**: ${paper.abstract}\n\n`;
        content += `[View Paper](${paper.url})\n\n---\n\n`;
    });
    return content;
}

export function deactivate() {}