# SuperClaude Unified API Documentation

## Overview

The SuperClaude Unified API provides a comprehensive endpoint system that integrates all SuperClaude capabilities with full MCP (Model Control Protocol) support. This unified system implements Context7 (memory persistence), Sequential (thinking orchestration), Magic (AI analysis), Memory (advanced storage), Serena (AI assistant), and Persona (intelligent role management) features.

## Base URL

```
http://localhost:8000/api/v1/superclaude-unified
```

## Authentication

All endpoints require Bearer token authentication:

```bash
Authorization: Bearer <your-access-token>
```

## Core Features

### 1. **Context7** - Memory Persistence
- Cross-session memory correlation
- Persistent context management
- Semantic memory search

### 2. **Sequential** - Thinking Orchestration
- Multi-step reasoning
- Revision tracking
- Workflow orchestration

### 3. **Magic** - Pattern Analysis
- Deep pattern recognition
- Insight generation
- Predictive modeling

### 4. **Memory** - Advanced Storage
- Semantic search capabilities
- Temporal analysis
- Memory optimization

### 5. **Serena** - AI Assistant
- Proactive assistance
- Task automation
- Learning adaptation

### 6. **Persona** - Intelligent Roles
- Auto-activation based on context
- Multi-persona blending
- Context-aware switching

## Endpoints

### 1. Unified Execute
**POST** `/execute`

Execute unified SuperClaude command with complete feature integration.

```json
{
  "query": "Analyze the effectiveness of lumbar fusion surgery",
  "mode": "intelligent",  // Options: standard, wave_based, orchestrated, intelligent
  "features": {
    "context7": true,
    "sequential": true,
    "magic": true,
    "memory": true,
    "serena": true,
    "persona": true
  },
  "session_id": "optional-session-id",
  "context": {
    "domain": "medical_research",
    "task_type": "analysis"
  },
  "metadata": {}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "completed",
  "mode_used": "intelligent",
  "features_activated": {...},
  "primary_response": "Detailed analysis...",
  "structured_data": {...},
  "thinking_process": [...],
  "memory_updates": [...],
  "persona_insights": {...},
  "serena_recommendations": [...],
  "execution_metadata": {...}
}
```

### 2. Orchestrate Complex Operations
**POST** `/orchestrate`

Orchestrate complex multi-phase operations with dependencies.

```json
{
  "objective": "Complete research workflow",
  "phases": [
    {
      "id": "phase1",
      "name": "Literature Review",
      "tasks": ["search", "filter", "summarize"]
    }
  ],
  "dependencies": {
    "phase2": ["phase1"]
  },
  "checkpoints": [...],
  "rollback_strategy": {...}
}
```

### 3. Advanced Memory Operations
**POST** `/memory/advanced`

Perform advanced memory operations with correlation analysis.

```json
{
  "query_type": "search",  // Options: search, retrieve, analyze, correlate
  "query": "lumbar fusion outcomes",
  "filters": {
    "type": "research",
    "date_range": "last_year"
  },
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2025-01-01T00:00:00Z"
  },
  "correlation_depth": 2
}
```

### 4. Configure Personas
**POST** `/persona/configure`

Configure advanced persona management with blending.

```json
{
  "primary_persona": "researcher",
  "secondary_personas": ["clinician", "analyst"],
  "auto_switch": true,
  "context_aware": true,
  "blend_mode": "weighted"  // Options: weighted, sequential, parallel
}
```

### 5. Serena AI Directive
**POST** `/serena/directive`

Execute Serena AI assistant directives.

```json
{
  "task": "Optimize research methodology",
  "guidance_level": "comprehensive",  // Options: minimal, balanced, comprehensive
  "proactive_mode": true,
  "learning_enabled": true
}
```

### 6. Deep Analysis
**POST** `/analyze/deep`

Perform deep analysis using all SuperClaude capabilities.

```json
{
  "content": "Text content to analyze",
  "analysis_types": ["semantic", "structural", "contextual", "predictive"],
  "use_all_features": true
}
```

### 7. Batch Execution
**POST** `/batch/execute`

Execute multiple unified requests in batch.

```json
[
  {
    "query": "First query",
    "mode": "standard",
    "features": {...}
  },
  {
    "query": "Second query",
    "mode": "wave_based",
    "features": {...}
  }
]
```

Query Parameters:
- `parallel`: boolean (default: false) - Execute requests in parallel

### 8. Get Session Context
**GET** `/session/{session_id}/complete-context`

Retrieve complete session context including all features.

**Response:**
```json
{
  "session_id": "uuid",
  "session_data": {...},
  "memory_state": {...},
  "active_personas": {...},
  "thinking_history": [...],
  "magic_insights": {...},
  "serena_recommendations": [...],
  "execution_history": [...]
}
```

### 9. Get Capabilities
**GET** `/capabilities`

Get complete list of unified SuperClaude capabilities.

**Response:**
```json
{
  "features": {
    "context7": {
      "enabled": true,
      "capabilities": ["memory_persistence", "context_management", "cross_session_correlation"]
    },
    ...
  },
  "execution_modes": ["standard", "wave_based", "orchestrated", "intelligent"],
  "version": "1.0.0",
  "status": "active"
}
```

### 10. WebSocket Interactive Session
**WebSocket** `/ws/unified`

Real-time unified SuperClaude interaction with streaming responses.

**Connection:** `ws://localhost:8000/api/v1/superclaude-unified/ws/unified`

**Message Format:**
```json
{
  "message": "Your query here",
  "type": "chat",  // Options: chat, command, query
  "features": {
    "context7": true,
    "sequential": true,
    "magic": true,
    "memory": true,
    "serena": true,
    "persona": true
  },
  "context": {}
}
```

## Execution Modes

### 1. **Standard Mode**
- Single-pass execution
- Quick responses
- Suitable for simple queries

### 2. **Wave-Based Mode**
- Multi-wave execution
- Analysis → Implementation → Validation
- Suitable for complex tasks

### 3. **Orchestrated Mode**
- Full orchestration with all features
- Complete lifecycle management
- Maximum capability utilization

### 4. **Intelligent Mode**
- AI-driven mode selection
- Automatic optimization
- Context-aware processing

## Best Practices

1. **Session Management**
   - Use consistent session IDs for related queries
   - Session context persists across requests
   - Clean up sessions when done

2. **Feature Selection**
   - Enable only needed features for performance
   - Use intelligent mode for automatic optimization
   - Consider batch execution for multiple queries

3. **Memory Management**
   - Regular memory optimization occurs automatically
   - Use correlation analysis for insights
   - Implement time-based filtering for large datasets

4. **Persona Usage**
   - Let auto-activation handle most cases
   - Configure blending for complex scenarios
   - Use context-aware switching for dynamic needs

## Error Handling

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

Error Response Format:
```json
{
  "detail": "Error description"
}
```

## Rate Limiting

- Default: 100 requests per minute per user
- WebSocket: 10 concurrent connections per user
- Batch: Maximum 10 requests per batch

## Examples

### Example 1: Medical Research Analysis
```bash
curl -X POST http://localhost:8000/api/v1/superclaude-unified/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze recent advances in minimally invasive spine surgery",
    "mode": "intelligent",
    "features": {
      "context7": true,
      "sequential": true,
      "magic": true,
      "memory": true,
      "serena": true,
      "persona": true
    },
    "context": {
      "research_focus": "clinical_outcomes",
      "time_period": "2020-2025"
    }
  }'
```

### Example 2: Complex Workflow Orchestration
```bash
curl -X POST http://localhost:8000/api/v1/superclaude-unified/orchestrate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Complete systematic literature review",
    "phases": [
      {
        "id": "search",
        "name": "Literature Search",
        "tasks": ["pubmed_search", "filter_criteria", "deduplication"]
      },
      {
        "id": "analysis",
        "name": "Data Analysis",
        "tasks": ["quality_assessment", "data_extraction", "synthesis"]
      },
      {
        "id": "report",
        "name": "Report Generation",
        "tasks": ["draft_writing", "visualization", "peer_review"]
      }
    ],
    "dependencies": {
      "analysis": ["search"],
      "report": ["analysis"]
    }
  }'
```

## Support

For issues or questions, please contact the development team or refer to the internal documentation.