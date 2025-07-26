import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export class ClaudeIntegration {
    private context: vscode.ExtensionContext;
    private claudeCodePath: string = 'claude-code';
    private isAuthenticated: boolean = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.checkAuthentication();
    }

    private async checkAuthentication() {
        try {
            const { stdout } = await execAsync(`${this.claudeCodePath} status`);
            this.isAuthenticated = stdout.includes('Authenticated');
        } catch (error) {
            this.isAuthenticated = false;
        }
    }

    async authenticate() {
        const terminal = vscode.window.createTerminal('Claude Authentication');
        terminal.show();
        terminal.sendText(`${this.claudeCodePath} login`);
        
        // Wait for user to complete authentication
        const result = await vscode.window.showInformationMessage(
            'Please complete the authentication in the terminal',
            'Done', 'Cancel'
        );

        if (result === 'Done') {
            await this.checkAuthentication();
            if (this.isAuthenticated) {
                vscode.window.showInformationMessage('Successfully authenticated with Claude!');
                return true;
            }
        }
        return false;
    }

    async sendMessage(message: string, context?: string): Promise<string> {
        if (!this.isAuthenticated) {
            const shouldAuth = await vscode.window.showWarningMessage(
                'Not authenticated with Claude. Would you like to login?',
                'Yes', 'No'
            );
            
            if (shouldAuth === 'Yes') {
                const success = await this.authenticate();
                if (!success) {
                    return 'Authentication failed. Please try again.';
                }
            } else {
                return 'Authentication required to use Claude.';
            }
        }

        try {
            const fullMessage = context ? `Context: ${context}\n\nQuestion: ${message}` : message;
            const { stdout, stderr } = await execAsync(
                `${this.claudeCodePath} chat "${fullMessage.replace(/"/g, '\\"')}"`,
                { maxBuffer: 1024 * 1024 * 10 } // 10MB buffer
            );

            if (stderr) {
                console.error('Claude error:', stderr);
            }

            return stdout || 'No response from Claude';
        } catch (error: any) {
            console.error('Claude integration error:', error);
            return `Error: ${error.message}`;
        }
    }

    async getProjectSuggestions(projectName: string, projectType: string): Promise<string> {
        const prompt = `I'm starting a new medical research project:
Title: ${projectName}
Type: ${projectType}

Please provide:
1. Suggested research objectives
2. Recommended methodology
3. Key variables to consider
4. Potential challenges
5. Timeline estimate
6. Required resources

Format the response in markdown.`;

        return await this.sendMessage(prompt);
    }

    async reviewText(text: string, reviewType: 'grammar' | 'scientific' | 'clarity'): Promise<string> {
        const prompts = {
            grammar: 'Review this text for grammar, spelling, and punctuation errors:',
            scientific: 'Review this text for scientific accuracy and suggest improvements:',
            clarity: 'Review this text for clarity and suggest ways to make it more concise:'
        };

        const prompt = `${prompts[reviewType]}\n\n${text}`;
        return await this.sendMessage(prompt);
    }

    async generateSection(sectionType: string, context: string): Promise<string> {
        const prompts: { [key: string]: string } = {
            abstract: 'Generate an abstract based on the following research information:',
            introduction: 'Write an introduction section based on the following context:',
            methods: 'Write a methods section based on the following study design:',
            discussion: 'Write a discussion section based on the following results:',
            conclusion: 'Write a conclusion based on the following findings:'
        };

        const prompt = `${prompts[sectionType] || 'Generate content based on:'}\n\n${context}`;
        return await this.sendMessage(prompt);
    }

    async suggestReferences(topic: string, existingRefs?: string[]): Promise<string> {
        let prompt = `Suggest relevant academic references for research on: ${topic}`;
        
        if (existingRefs && existingRefs.length > 0) {
            prompt += `\n\nExisting references:\n${existingRefs.join('\n')}`;
            prompt += '\n\nPlease suggest additional complementary references.';
        }

        return await this.sendMessage(prompt);
    }

    async analyzeData(dataDescription: string, analysisType: string): Promise<string> {
        const prompt = `Analyze the following data and provide ${analysisType} analysis:\n\n${dataDescription}`;
        return await this.sendMessage(prompt);
    }

    async generateVisualization(data: string, vizType: string): Promise<string> {
        const prompt = `Generate Python code to create a ${vizType} visualization for the following data:\n\n${data}\n\nInclude necessary imports and make the code ready to run.`;
        return await this.sendMessage(prompt);
    }

    // Integration with VS Code features
    async provideCodeActions(document: vscode.TextDocument, range: vscode.Range): Promise<vscode.CodeAction[]> {
        const text = document.getText(range);
        const actions: vscode.CodeAction[] = [];

        // Review actions
        const reviewAction = new vscode.CodeAction(
            'Review with Claude AI',
            vscode.CodeActionKind.RefactorRewrite
        );
        reviewAction.command = {
            command: 'spinalsurgery.reviewWithClaude',
            title: 'Review with Claude',
            arguments: [text, document, range]
        };
        actions.push(reviewAction);

        // Generate content action
        if (text.trim().startsWith('TODO:') || text.trim().startsWith('GENERATE:')) {
            const generateAction = new vscode.CodeAction(
                'Generate content with Claude',
                vscode.CodeActionKind.RefactorRewrite
            );
            generateAction.command = {
                command: 'spinalsurgery.generateWithClaude',
                title: 'Generate with Claude',
                arguments: [text, document, range]
            };
            actions.push(generateAction);
        }

        return actions;
    }

    // Real-time collaboration features
    startCollaborativeSession(sessionId: string) {
        // Implementation for real-time collaboration with Claude
        // This could integrate with VS Code Live Share
    }

    // Export utilities
    async exportConversation(): Promise<string> {
        const { stdout } = await execAsync(`${this.claudeCodePath} export --format markdown`);
        return stdout;
    }
}