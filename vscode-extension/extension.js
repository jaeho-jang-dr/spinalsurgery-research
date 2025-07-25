const vscode = require('vscode');
const { Anthropic } = require('@anthropic-ai/sdk');
const axios = require('axios');

let anthropic;
let outputChannel;

function activate(context) {
    console.log('Claude Code for Spinal Surgery Research is now active!');
    
    // Create output channel
    outputChannel = vscode.window.createOutputChannel('Claude Code');
    
    // Initialize Anthropic client
    const apiKey = vscode.workspace.getConfiguration('claudeCode').get('apiKey');
    if (apiKey) {
        anthropic = new Anthropic({ apiKey });
    }
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('claudeCode.askQuestion', askQuestion),
        vscode.commands.registerCommand('claudeCode.generatePaperDraft', generatePaperDraft),
        vscode.commands.registerCommand('claudeCode.analyzeData', analyzeData),
        vscode.commands.registerCommand('claudeCode.reviewCode', reviewCode),
        vscode.commands.registerCommand('claudeCode.searchPapers', searchPapers)
    );
    
    // Create status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(hubot) Claude';
    statusBarItem.tooltip = 'Claude AI Assistant';
    statusBarItem.command = 'claudeCode.askQuestion';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    
    // Watch for configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('claudeCode.apiKey')) {
                const newApiKey = vscode.workspace.getConfiguration('claudeCode').get('apiKey');
                if (newApiKey) {
                    anthropic = new Anthropic({ apiKey: newApiKey });
                }
            }
        })
    );
}

async function askQuestion() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const selection = editor.document.getText(editor.selection);
    const question = await vscode.window.showInputBox({
        prompt: 'Ask Claude a question about your research',
        placeHolder: 'e.g., How to analyze spine fusion success rates?'
    });
    
    if (!question) return;
    
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Claude is thinking...',
            cancellable: false
        }, async () => {
            const response = await callClaude(question, selection);
            showResponse(response);
        });
    } catch (error) {
        vscode.window.showErrorMessage(`Claude error: ${error.message}`);
    }
}

async function generatePaperDraft() {
    const title = await vscode.window.showInputBox({
        prompt: 'Enter paper title',
        placeHolder: 'e.g., Long-term outcomes of spinal fusion surgery'
    });
    
    if (!title) return;
    
    const keywords = await vscode.window.showInputBox({
        prompt: 'Enter keywords (comma-separated)',
        placeHolder: 'e.g., spine surgery, fusion, outcomes'
    });
    
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating paper draft...',
            cancellable: false
        }, async () => {
            const prompt = `Generate a research paper draft with title: "${title}" and keywords: ${keywords}. Include abstract, introduction, methods, results, discussion, and conclusion sections.`;
            const response = await callClaude(prompt);
            
            // Create new document with the draft
            const doc = await vscode.workspace.openTextDocument({
                content: response,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc);
        });
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to generate draft: ${error.message}`);
    }
}

async function analyzeData() {
    const uri = vscode.window.activeTextEditor?.document.uri;
    if (!uri) return;
    
    // For CSV/Excel files, read and analyze
    vscode.window.showInformationMessage('Data analysis feature coming soon!');
}

async function reviewCode() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    
    const code = editor.document.getText();
    const language = editor.document.languageId;
    
    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Reviewing code...',
            cancellable: false
        }, async () => {
            const prompt = `Review this ${language} code for a medical research platform. Focus on:
1. Security and HIPAA compliance
2. Data handling best practices
3. Code quality and maintainability
4. Potential bugs or issues

Code:
${code}`;
            
            const response = await callClaude(prompt);
            showResponse(response, 'Code Review');
        });
    } catch (error) {
        vscode.window.showErrorMessage(`Review failed: ${error.message}`);
    }
}

async function searchPapers() {
    const query = await vscode.window.showInputBox({
        prompt: 'Enter search query for papers',
        placeHolder: 'e.g., spine fusion long-term outcomes'
    });
    
    if (!query) return;
    
    try {
        // Call local backend API
        const response = await axios.post('http://localhost:8000/api/v1/papers/search', {
            query,
            sources: ['pubmed'],
            limit: 10
        });
        
        const papers = response.data;
        const quickPick = vscode.window.createQuickPick();
        quickPick.items = papers.map(paper => ({
            label: paper.title,
            description: paper.authors,
            detail: paper.abstract?.substring(0, 200) + '...'
        }));
        quickPick.placeholder = 'Select a paper to view details';
        quickPick.onDidChangeSelection(selection => {
            if (selection[0]) {
                const paper = papers.find(p => p.title === selection[0].label);
                showResponse(JSON.stringify(paper, null, 2), 'Paper Details');
            }
        });
        quickPick.show();
    } catch (error) {
        vscode.window.showErrorMessage(`Search failed: ${error.message}`);
    }
}

async function callClaude(prompt, context = '') {
    if (!anthropic) {
        throw new Error('Claude API key not configured');
    }
    
    const config = vscode.workspace.getConfiguration('claudeCode');
    const model = config.get('model');
    const maxTokens = config.get('maxTokens');
    const temperature = config.get('temperature');
    
    const fullPrompt = context ? `Context:\n${context}\n\nQuestion: ${prompt}` : prompt;
    
    const response = await anthropic.messages.create({
        model,
        max_tokens: maxTokens,
        temperature,
        messages: [{
            role: 'user',
            content: fullPrompt
        }]
    });
    
    return response.content[0].text;
}

function showResponse(content, title = 'Claude Response') {
    outputChannel.clear();
    outputChannel.appendLine(`=== ${title} ===`);
    outputChannel.appendLine('');
    outputChannel.appendLine(content);
    outputChannel.show();
}

function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};