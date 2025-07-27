# SpinalSurgery Research - Advanced AI System Guide

## Overview

The SpinalSurgery Research platform now includes a state-of-the-art AI assistant with advanced features including:
- 🧠 **7-Level Context Management (C7)**
- 🤔 **Sequential Thinking**
- 🪄 **Magic Commands**
- 💾 **Memory System** (Short-term & Long-term)
- 🎭 **Multiple AI Personas**
- 🔌 **Advanced Endpoint Integration**

## Quick Start

1. **Access the AI**: Navigate to the AI Assistant tab in the application
2. **Default Persona**: Dr. Serena (Spinal Surgery Research Assistant) is active by default
3. **Type naturally**: The AI understands both English and Korean
4. **Use Magic Commands**: Start messages with `/` for special features

## AI Personas

### 1. Dr. Serena (Research Assistant)
- **Role**: Spinal Surgery Research Assistant
- **Specialties**: Medical research, statistics, paper writing
- **Best for**: Research design, literature review, methodology

### 2. Alex Data (Data Analyst)
- **Role**: Medical Data Analysis Expert
- **Specialties**: Statistical analysis, data visualization
- **Best for**: Data analysis, statistical methods, result interpretation

### 3. Professor Write (Paper Writer)
- **Role**: Academic Writing Specialist
- **Specialties**: Academic writing, paper structure, citations
- **Best for**: Manuscript preparation, abstract writing, formatting

### 4. Dev Helper (Code Assistant)
- **Role**: Medical Software Developer
- **Specialties**: Python, data processing, API development
- **Best for**: Research software, data scripts, automation

## Magic Commands

### Basic Commands
- `/help` - Show all available commands
- `/help [command]` - Get help for specific command
- `/persona [name]` - Switch to different AI persona
- `/context` - Show current context levels
- `/context [level]` - Show specific context level

### Advanced Features
- `/think [topic]` - Sequential thinking process for complex problems
- `/analyze [topic]` - Deep analysis with multiple perspectives
- `/research [query]` - Activate research mode
- `/write [context]` - Academic writing assistance
- `/code [request]` - Programming help

### Memory Management
- `/remember [category]: [content]` - Save to long-term memory
  - Categories: `facts`, `insights`, `preferences`
- `/recall [query]` - Search and retrieve memories
- Memory persists across sessions

### Data & Visualization
- `/visualize [data description]` - Get visualization recommendations

## Context Management System (C7)

The AI maintains 7 hierarchical context levels:

1. **Global Context** - System-wide settings
2. **Session Context** - Current session information
3. **Conversation Context** - Ongoing conversation flow
4. **Task Context** - Specific task details
5. **Semantic Context** - Meaning and relationships
6. **Temporal Context** - Time-based information
7. **Personal Context** - User preferences and history

## Memory System

### Short-term Memory
- Stores last 100 interactions
- Quick access to recent context
- Automatically managed

### Long-term Memory
- Persistent storage across sessions
- Categorized: facts, conversations, insights, preferences
- Exportable/Importable in JSON format

### Memory Operations
- **Export**: Settings → Memory Management → Export Memory
- **Import**: Settings → Memory Management → Import Memory
- **Clear**: Option to clear short-term or long-term memory

## Example Usage

### Research Query
```
/research lumbar fusion 2-year outcomes with different surgical approaches
```

### Sequential Thinking
```
/think optimal statistical approach for comparing PLIF vs TLIF outcomes
```

### Save Important Information
```
/remember facts: PLIF shows 92% fusion rate at 2 years in recent meta-analysis
```

### Switch Persona for Data Analysis
```
/persona data_analyst
Can you help me design a statistical analysis plan for my cohort study?
```

### Academic Writing Help
```
/write abstract for lumbar fusion outcomes study
```

## API Endpoints

The advanced AI system exposes several endpoints:

- `POST /api/v1/ai-advanced/chat` - Send messages
- `WS /api/v1/ai-advanced/ws` - WebSocket for streaming
- `GET /api/v1/ai-advanced/personas` - List personas
- `PUT /api/v1/ai-advanced/personas/{id}` - Switch persona
- `GET /api/v1/ai-advanced/memory/export` - Export memory
- `POST /api/v1/ai-advanced/memory/import` - Import memory
- `GET /api/v1/ai-advanced/context` - Get context
- `PUT /api/v1/ai-advanced/context/{level}` - Update context

## Ollama Integration

The system is designed to work with Ollama for local LLM support:

1. **Models Used**:
   - `mistral:7b` - General purpose
   - `llama2:7b` - Alternative model
   - `codellama:7b` - Code-specific tasks

2. **Fallback**: If Ollama is not available, the system uses intelligent mock responses

3. **Start Ollama**: Run `/home/drjang00/DevEnvironments/spinalsurgery-research/backend/start_ollama.sh`

## Tips for Best Results

1. **Be Specific**: Provide clear context for better responses
2. **Use Personas**: Switch to the most appropriate persona for your task
3. **Save Important Info**: Use `/remember` for key findings
4. **Sequential Thinking**: Use `/think` for complex problems
5. **Export Your Work**: Regularly export memory for backup

## Troubleshooting

- **AI Not Responding**: Check if backend is running on port 8000
- **Persona Not Switching**: Ensure valid persona ID is used
- **Memory Not Saving**: Check disk space and permissions
- **Ollama Issues**: Check logs at `/home/drjang00/DevEnvironments/spinalsurgery-research/logs/ollama.log`

## Future Enhancements

- PDF integration for paper analysis
- Direct PubMed search integration
- Multi-modal support (images, charts)
- Collaborative research features
- Custom persona creation

---

For technical support or feature requests, please contact the development team.