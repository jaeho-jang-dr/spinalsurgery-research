# SuperClaude Enhanced API Documentation

## Overview

The SuperClaude Enhanced API provides a comprehensive endpoint system with full MCP (Model Context Protocol) integration, wave-based execution, and advanced AI capabilities for the SpinalSurgery Research Platform.

## Base URL

```
/api/v1/superclaude-enhanced
```

## Features

- **Wave-Based Execution**: Multi-phase processing (Analysis → Implementation → Validation → Finalization)
- **MCP Integration**: Context7, Sequential, Magic, Memory, and Playwright servers
- **Auto-Persona System**: Automatic activation of specialized research personas
- **Memory Persistence**: Context-aware session management
- **Serena Capabilities**: Enhanced AI assistant features
- **WebSocket Support**: Real-time interactive sessions

## Endpoints

### 1. Execute SuperClaude Command

Execute commands with full MCP integration and wave-based processing.

**POST** `/execute`

```json
{
  "command": "implement",
  "target": "user authentication system",
  "flags": ["--c7", "--seq", "--magic", "--memory", "--serena", "--persona"],
  "context": {
    "requirements": ["OAuth2", "JWT tokens", "Role-based access"]
  },
  "session_id": "optional-session-id"
}
```

**Commands:**
- `analyze`: Comprehensive analysis with multi-persona approach
- `implement`: Feature implementation with full lifecycle
- `build`: Intelligent build system with optimization
- `improve`: Code optimization and enhancement
- `troubleshoot`: Advanced debugging and problem resolution
- `design`: Architecture and system design
- `test`: Comprehensive testing approach

**Flags:**
- `--c7`: Enable Context7 memory persistence
- `--seq`: Enable sequential thinking orchestration
- `--magic`: Enable Magic server analysis
- `--memory`: Enable memory operations
- `--serena`: Enable Serena assistant capabilities
- `--persona`: Enable auto-persona activation

### 2. Wave Execution

Execute specific waves in the SuperClaude system.

**POST** `/wave/execute`

```json
{
  "wave_type": "analysis",
  "task": "Design a clinical trial protocol",
  "context": {
    "study_type": "RCT",
    "population": "lumbar fusion patients"
  },
  "session_id": "optional-session-id",
  "auto_persona": true,
  "use_mcp": ["context7", "sequential", "magic"]
}
```

**Wave Types:**
- `analysis`: Requirements gathering and analysis
- `implementation`: Core implementation and development
- `validation`: Testing and quality assurance
- `finalization`: Documentation and deployment preparation

### 3. Enhanced Chat

Interactive chat with full SuperClaude capabilities.

**POST** `/chat/enhanced`

```json
{
  "message": "Help me design a statistical analysis plan for my study",
  "session_id": "optional-session-id",
  "context": "RCT with 200 patients",
  "enable_c7": true,
  "enable_seq": true,
  "enable_magic": true,
  "enable_memory": true,
  "enable_serena": true,
  "enable_persona": true
}
```

### 4. Memory Operations

Perform memory operations with Context7 integration.

**POST** `/memory/operation`

```json
{
  "operation": "save",
  "session_id": "session-123",
  "key": "study_protocol",
  "value": {
    "title": "Lumbar Fusion Outcomes Study",
    "design": "Prospective cohort"
  }
}
```

**Operations:**
- `save`: Store data in memory
- `retrieve`: Get data from memory
- `update`: Update existing data
- `delete`: Remove data from memory

### 5. Persona Management

#### Activate Persona

**POST** `/persona/activate`

```json
{
  "persona_type": "statistician",
  "task_context": "Sample size calculation for RCT",
  "session_id": "optional-session-id"
}
```

**Persona Types:**
- Research: `statistician`, `clinician`, `methodologist`, `writer`, `ethicist`
- Development: `frontend`, `backend`, `architect`, `security`, `devops`, `fullstack`

#### List Personas

**GET** `/persona/list`

Returns all available personas with their capabilities.

### 6. Sequential Thinking

Execute sequential thinking process for complex problems.

**POST** `/thinking/sequential`

```json
{
  "problem": "Design a multi-center clinical trial with adaptive design",
  "max_steps": 15,
  "allow_revision": true,
  "session_id": "optional-session-id"
}
```

### 7. Magic Analysis

Perform advanced AI-powered analysis.

**POST** `/magic/analyze`

```json
{
  "content": "Randomized controlled trial comparing surgical techniques",
  "analysis_type": "methodology",
  "depth": "comprehensive",
  "session_id": "optional-session-id"
}
```

**Analysis Types:**
- `methodology`: Research methodology analysis
- `statistics`: Statistical approach analysis
- `code`: Code quality and architecture analysis
- `architecture`: System design analysis

**Depth Levels:**
- `quick`: Brief summary
- `standard`: Normal analysis
- `comprehensive`: Detailed analysis with SWOT

### 8. Research Task Execution

Execute comprehensive research tasks.

**POST** `/research/task`

```json
{
  "task_type": "protocol",
  "description": "Develop IRB protocol for spine surgery outcomes study",
  "requirements": {
    "population": "Adults with lumbar stenosis",
    "intervention": "Minimally invasive decompression",
    "outcomes": ["pain scores", "functional status", "quality of life"]
  },
  "use_waves": true,
  "auto_persona": true,
  "mcp_integration": true,
  "session_id": "optional-session-id"
}
```

**Task Types:**
- `protocol`: Study protocol development
- `analysis`: Data analysis planning
- `manuscript`: Paper writing
- `review`: Literature review
- `statistics`: Statistical analysis
- `ethics`: Ethics documentation

### 9. Session Context

Get complete session context from memory.

**GET** `/session/{session_id}/context`

Returns comprehensive session information including:
- Research context
- Wave execution history
- Active persona
- Session metadata

### 10. MCP Status

Get status of all MCP servers.

**GET** `/mcp/status`

Returns health and capability information for each MCP server.

### 11. WebSocket Interactive Session

Real-time interactive SuperClaude sessions.

**WebSocket** `/ws/interactive`

Message format:
```json
{
  "type": "chat",
  "message": "Your question or command",
  "context": {}
}
```

Response format:
```json
{
  "type": "chat_response",
  "content": "SuperClaude response",
  "session_id": "session-id",
  "enhancements": {
    "suggestions": [],
    "related_topics": [],
    "learning_resources": [],
    "action_items": []
  }
}
```

### 12. Workflow Management

#### Create Workflow

**POST** `/workflow/create`

```json
{
  "workflow_name": "Complete Research Study",
  "steps": [
    {
      "name": "Protocol Development",
      "command": "design",
      "target": "study protocol",
      "context": {"phase": "planning"}
    },
    {
      "name": "Statistical Plan",
      "command": "analyze",
      "target": "statistical approach",
      "context": {"phase": "analysis"}
    }
  ]
}
```

#### Execute Workflow

**POST** `/workflow/{workflow_id}/execute`

```json
{
  "context": {
    "study_name": "LUMBAR-2025",
    "principal_investigator": "Dr. Smith"
  }
}
```

## Response Formats

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "metadata": {
    "session_id": "session-123",
    "timestamp": "2025-01-27T12:00:00Z",
    "thinking_steps": 10,
    "waves_executed": ["analysis", "implementation"],
    "active_persona": "methodologist"
  }
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_COMMAND",
    "message": "Unknown command: invalid_command",
    "details": {}
  }
}
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Rate Limiting

- Standard endpoints: 100 requests per minute
- WebSocket connections: 10 concurrent connections per user
- Workflow execution: 10 workflows per hour

## Best Practices

1. **Session Management**: Always use session IDs for context persistence across requests
2. **Wave Selection**: Let the system auto-select waves based on command type
3. **Persona Usage**: Enable auto-persona for optimal expertise matching
4. **MCP Integration**: Enable all MCP servers for comprehensive capabilities
5. **Error Handling**: Implement proper error handling for all API calls

## Examples

### Example 1: Complete Research Protocol Development

```python
import requests

# Step 1: Create session and analyze requirements
response = requests.post(
    "/api/v1/superclaude-enhanced/execute",
    json={
        "command": "analyze",
        "target": "lumbar fusion clinical trial requirements",
        "flags": ["--c7", "--seq", "--magic", "--memory", "--persona"],
        "context": {
            "study_type": "RCT",
            "population_size": 200
        }
    },
    headers={"Authorization": "Bearer <token>"}
)
session_id = response.json()["session_id"]

# Step 2: Design protocol based on analysis
response = requests.post(
    "/api/v1/superclaude-enhanced/execute",
    json={
        "command": "design",
        "target": "clinical trial protocol",
        "flags": ["--c7", "--seq", "--magic", "--memory", "--persona"],
        "session_id": session_id
    },
    headers={"Authorization": "Bearer <token>"}
)

# Step 3: Retrieve complete context
context = requests.get(
    f"/api/v1/superclaude-enhanced/session/{session_id}/context",
    headers={"Authorization": "Bearer <token>"}
)
```

### Example 2: Interactive Research Assistant

```javascript
// WebSocket connection for interactive session
const ws = new WebSocket('ws://localhost:8000/api/v1/superclaude-enhanced/ws/interactive');

ws.onopen = () => {
    console.log('Connected to SuperClaude');
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log('SuperClaude:', response.content);
    
    // Display suggestions
    if (response.enhancements) {
        console.log('Suggestions:', response.enhancements.suggestions);
        console.log('Action Items:', response.enhancements.action_items);
    }
};

// Send message
ws.send(JSON.stringify({
    type: 'chat',
    message: 'Help me calculate sample size for my study',
    context: {
        effect_size: 0.5,
        power: 0.8,
        alpha: 0.05
    }
}));
```

## Version History

- **v1.0.0** (2025-01-27): Initial release with full MCP integration
  - Wave-based execution system
  - Enhanced chat capabilities
  - Persona management
  - Memory operations
  - WebSocket support
  - Workflow orchestration