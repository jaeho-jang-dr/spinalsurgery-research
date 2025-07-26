import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';

export interface ResearchProject {
    id: string;
    name: string;
    type: string;
    description: string;
    created_at: string;
    updated_at: string;
    status: 'active' | 'completed' | 'archived';
    collaborators: string[];
    tags: string[];
}

export interface Paper {
    id: string;
    title: string;
    authors: string;
    journal: string;
    year: number;
    abstract: string;
    url: string;
    doi?: string;
    citations?: number;
}

export interface DataSet {
    id: string;
    name: string;
    description: string;
    type: 'csv' | 'excel' | 'json' | 'spss';
    size: number;
    created_at: string;
    project_id: string;
}

export class ResearchAPI {
    private api: AxiosInstance;
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        
        const config = vscode.workspace.getConfiguration('spinalsurgery');
        const baseURL = config.get<string>('apiEndpoint', 'http://localhost:8000');

        this.api = axios.create({
            baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add auth token if available
        this.setupAuthInterceptor();
    }

    private setupAuthInterceptor() {
        this.api.interceptors.request.use(async (config) => {
            const token = await this.context.secrets.get('spinalsurgery.authToken');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        this.api.interceptors.response.use(
            response => response,
            async error => {
                if (error.response?.status === 401) {
                    // Token expired or invalid
                    await this.context.secrets.delete('spinalsurgery.authToken');
                    vscode.window.showErrorMessage('Authentication expired. Please login again.');
                    vscode.commands.executeCommand('spinalsurgery.login');
                }
                return Promise.reject(error);
            }
        );
    }

    async login(email: string, password: string): Promise<boolean> {
        try {
            const response = await this.api.post('/auth/login', { email, password });
            const { access_token } = response.data;
            await this.context.secrets.store('spinalsurgery.authToken', access_token);
            return true;
        } catch (error) {
            console.error('Login failed:', error);
            return false;
        }
    }

    async logout() {
        await this.context.secrets.delete('spinalsurgery.authToken');
    }

    // Project management
    async getProjects(): Promise<ResearchProject[]> {
        const response = await this.api.get('/projects');
        return response.data;
    }

    async getProject(id: string): Promise<ResearchProject> {
        const response = await this.api.get(`/projects/${id}`);
        return response.data;
    }

    async createProject(project: Partial<ResearchProject>): Promise<ResearchProject> {
        const response = await this.api.post('/projects', project);
        return response.data;
    }

    async updateProject(id: string, updates: Partial<ResearchProject>): Promise<ResearchProject> {
        const response = await this.api.put(`/projects/${id}`, updates);
        return response.data;
    }

    async deleteProject(id: string): Promise<void> {
        await this.api.delete(`/projects/${id}`);
    }

    // Paper search and management
    async searchPapers(query: string, filters?: any): Promise<Paper[]> {
        const response = await this.api.get('/papers/search', {
            params: { q: query, ...filters }
        });
        return response.data;
    }

    async getPaper(id: string): Promise<Paper> {
        const response = await this.api.get(`/papers/${id}`);
        return response.data;
    }

    async savePaper(paper: Partial<Paper>, projectId: string): Promise<Paper> {
        const response = await this.api.post(`/projects/${projectId}/papers`, paper);
        return response.data;
    }

    async getProjectPapers(projectId: string): Promise<Paper[]> {
        const response = await this.api.get(`/projects/${projectId}/papers`);
        return response.data;
    }

    // Data management
    async uploadData(projectId: string, file: vscode.Uri): Promise<DataSet> {
        const fileContent = await vscode.workspace.fs.readFile(file);
        const formData = new FormData();
        formData.append('file', new Blob([fileContent]), file.fsPath.split('/').pop() || 'data.csv');
        formData.append('project_id', projectId);

        const response = await this.api.post('/data/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    }

    async getDataSets(projectId: string): Promise<DataSet[]> {
        const response = await this.api.get(`/projects/${projectId}/data`);
        return response.data;
    }

    async analyzeData(dataSetId: string, analysisType: string): Promise<any> {
        const response = await this.api.post(`/data/${dataSetId}/analyze`, {
            analysis_type: analysisType
        });
        return response.data;
    }

    // Bibliography management
    async getBibliography(projectId: string): Promise<any[]> {
        const response = await this.api.get(`/projects/${projectId}/bibliography`);
        return response.data;
    }

    async addReference(projectId: string, reference: any): Promise<any> {
        const response = await this.api.post(`/projects/${projectId}/bibliography`, reference);
        return response.data;
    }

    async formatBibliography(projectId: string, style: string): Promise<string> {
        const response = await this.api.get(`/projects/${projectId}/bibliography/format`, {
            params: { style }
        });
        return response.data;
    }

    // Export functionality
    async exportProject(projectId: string, format: 'docx' | 'pdf' | 'latex' | 'markdown'): Promise<Blob> {
        const response = await this.api.get(`/projects/${projectId}/export`, {
            params: { format },
            responseType: 'blob'
        });
        return response.data;
    }

    // Real-time sync
    connectWebSocket(projectId: string): WebSocket {
        const config = vscode.workspace.getConfiguration('spinalsurgery');
        const baseURL = config.get<string>('apiEndpoint', 'http://localhost:8000');
        const wsURL = baseURL.replace('http', 'ws');
        
        const ws = new WebSocket(`${wsURL}/ws/${projectId}`);
        
        ws.onopen = () => {
            console.log('WebSocket connected for project:', projectId);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            vscode.window.showErrorMessage('Failed to connect to research server');
        };

        return ws;
    }

    // AI Integration endpoints
    async getAISuggestions(projectId: string, context: string): Promise<any> {
        const response = await this.api.post(`/projects/${projectId}/ai/suggest`, {
            context
        });
        return response.data;
    }

    async reviewWithAI(projectId: string, text: string, reviewType: string): Promise<any> {
        const response = await this.api.post(`/projects/${projectId}/ai/review`, {
            text,
            review_type: reviewType
        });
        return response.data;
    }
}