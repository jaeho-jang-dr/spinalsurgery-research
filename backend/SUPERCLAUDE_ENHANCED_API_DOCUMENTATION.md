# SuperClaude Enhanced API Documentation

## Overview

The SuperClaude Enhanced endpoint is a comprehensive AI-powered system that integrates multiple MCP (Model Context Protocol) servers to provide advanced capabilities for research, development, and analysis tasks. It features wave-based execution, auto-persona activation, and full integration with Context7, Sequential thinking, Magic analysis, Memory persistence, Serena assistant, and dynamic Persona capabilities.

## Base URL
```
http://localhost:8000/api/v1/superclaude-enhanced
```

## Authentication
All endpoints require Bearer token authentication:
```
Authorization: Bearer <access_token>
```

## Core Features

### 1. Context7 (--c7)
- Persistent context management across sessions
- Memory storage and retrieval
- Session state preservation

### 2. Sequential Thinking (--seq)
- Step-by-step problem solving
- Thought revision capabilities
- Multi-step orchestration

### 3. Magic Analysis (--magic)
- Pattern recognition
- Intelligent insights generation
- Comprehensive analysis modes

### 4. Memory Persistence (--memory)
- Session-based memory storage
- Key-value pair management
- Context retrieval and updates

### 5. Serena Integration (--serena)
- AI assistant enhancements
- Context-aware suggestions
- Learning resources recommendations
- Action item extraction

### 6. Persona System (--persona)
- Auto-activation based on task context
- Multiple specialized personas:
  - Research: Statistician, Clinician, Methodologist, Writer, Ethicist
  - Development: Frontend, Backend, Architect, Security, DevOps, FullStack

## Main Endpoints

### 1. Execute SuperClaude Command
**POST** `/execute`

Execute commands with wave-based processing and full MCP integration.

**Request Body:**
```json
{
  "command": "analyze|implement|build|improve|troubleshoot|design|test",
  "target": "string - target for the command",
  "flags": ["--c7", "--seq", "--magic", "--memory", "--serena", "--persona"],
  "context": {
    "key": "value"
  },
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "command": "analyze",
  "target": "lumbar fusion research protocol",
  "session_id": "uuid",
  "waves_executed": ["analysis", "validation"],
  "results": {
    "analysis": { ... },
    "validation": { ... }
  },
  "features_enabled": {
    "context7": true,
    "sequential": true,
    "magic": true,
    "memory": true,
    "serena": true,
    "persona": true
  },
  "total_thinking_steps": 15,
  "timestamp": "2025-07-27T12:00:00Z"
}
```

### 2. Execute Wave
**POST** `/wave/execute`

Execute a specific wave in the SuperClaude system.

**Request Body:**
```json
{
  "wave_type": "analysis|implementation|validation|finalization",
  "task": "string - task description",
  "context": {},
  "session_id": "optional-session-id",
  "auto_persona": true,
  "use_mcp": ["context7", "sequential", "magic", "memory", "playwright"]
}
```

### 3. Enhanced Chat
**POST** `/chat/enhanced`

Chat with full SuperClaude capabilities.

**Request Body:**
```json
{
  "message": "string",
  "session_id": "optional-session-id",
  "context": "optional-context-string",
  "enable_c7": true,
  "enable_seq": true,
  "enable_magic": true,
  "enable_memory": true,
  "enable_serena": true,
  "enable_persona": true
}
```

### 4. Memory Operations
**POST** `/memory/operation`

Perform memory operations with Context7 integration.

**Request Body:**
```json
{
  "operation": "save|retrieve|update|delete",
  "session_id": "string",
  "key": "string",
  "value": "any (optional for retrieve/delete)"
}
```

### 5. Persona Management
**POST** `/persona/activate`

Manually activate a specific persona.

**Request Body:**
```json
{
  "persona_type": "statistician|clinician|methodologist|writer|ethicist|frontend|backend|architect|security|devops|fullstack",
  "task_context": "string",
  "session_id": "optional-session-id"
}
```

**GET** `/persona/list`

List all available personas with their capabilities.

### 6. Sequential Thinking
**POST** `/thinking/sequential`

Execute sequential thinking process.

**Request Body:**
```json
{
  "problem": "string",
  "max_steps": 10,
  "allow_revision": true,
  "session_id": "optional-session-id"
}
```

### 7. Magic Analysis
**POST** `/magic/analyze`

Perform Magic server analysis.

**Request Body:**
```json
{
  "content": "string",
  "analysis_type": "methodology|statistics|code|architecture",
  "depth": "quick|standard|comprehensive",
  "session_id": "optional-session-id"
}
```

### 8. Research Task Execution
**POST** `/research/task`

Execute comprehensive research task with full SuperClaude capabilities.

**Request Body:**
```json
{
  "task_type": "protocol|analysis|manuscript|review|statistics|ethics",
  "description": "string",
  "requirements": {},
  "use_waves": true,
  "auto_persona": true,
  "mcp_integration": true,
  "session_id": "optional-session-id"
}
```

### 9. Session Context
**GET** `/session/{session_id}/context`

Get complete session context from memory.

### 10. MCP Status
**GET** `/mcp/status`

Get status of all MCP servers.

### 11. WebSocket Interactive Session
**WebSocket** `/ws/interactive`

Real-time interactive SuperClaude sessions.

**Message Format:**
```json
{
  "type": "chat|command",
  "message": "string",
  "context": {}
}
```

### 12. Workflow Management
**POST** `/workflow/create`

Create a multi-step workflow.

**Request Body:**
```json
{
  "workflow_name": "string",
  "steps": [
    {
      "name": "step1",
      "action": "analyze",
      "params": {}
    }
  ]
}
```

**POST** `/workflow/{workflow_id}/execute`

Execute a predefined workflow.

## Wave System

The SuperClaude system uses a wave-based execution model:

1. **Analysis Wave**: Understanding and planning
   - Requirements gathering
   - Constraint analysis
   - Insights generation

2. **Implementation Wave**: Core execution
   - Action implementation
   - Code generation
   - Configuration setup

3. **Validation Wave**: Quality assurance
   - Testing and verification
   - Quality metrics
   - Issue identification

4. **Finalization Wave**: Completion and documentation
   - Documentation generation
   - Cleanup tasks
   - Deployment preparation

## Usage Examples

### Example 1: Analyze Research Protocol
```bash
curl -X POST http://localhost:8000/api/v1/superclaude-enhanced/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "analyze",
    "target": "lumbar fusion clinical trial protocol",
    "flags": ["--c7", "--seq", "--magic", "--memory", "--serena", "--persona"],
    "context": {
      "study_type": "RCT",
      "population": "Adults with degenerative disc disease"
    }
  }'
```

### Example 2: Enhanced Chat with All Features
```bash
curl -X POST http://localhost:8000/api/v1/superclaude-enhanced/chat/enhanced \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me design a statistical analysis plan for my study",
    "enable_c7": true,
    "enable_seq": true,
    "enable_magic": true,
    "enable_memory": true,
    "enable_serena": true,
    "enable_persona": true
  }'
```

### Example 3: Sequential Thinking Process
```bash
curl -X POST http://localhost:8000/api/v1/superclaude-enhanced/thinking/sequential \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "How to handle missing data in longitudinal studies?",
    "max_steps": 15,
    "allow_revision": true
  }'
```

## Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

Error responses include detailed messages:
```json
{
  "detail": "Error description"
}
```

## Best Practices

1. **Session Management**: Always use session IDs for context persistence
2. **Feature Selection**: Enable only the features you need for better performance
3. **Wave Selection**: Choose appropriate waves based on your task complexity
4. **Persona Usage**: Let auto-persona select the expert or manually choose for specific needs
5. **Memory Management**: Clean up sessions when done to free resources

## MCP Server Endpoints

The system integrates with these MCP servers:
- **Context7**: http://localhost:8001
- **Sequential**: http://localhost:8002
- **Magic**: http://localhost:8003
- **Memory**: http://localhost:8004
- **Playwright**: http://localhost:8005

## Performance Considerations

- Wave execution can take 10-60 seconds depending on complexity
- Sequential thinking steps are limited to 50 per request
- Memory operations are session-scoped
- WebSocket connections have a 10-minute idle timeout

## Version
Current Version: 1.0.0
Last Updated: 2025-07-27