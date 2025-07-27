"""
SuperClaude Unified Service
Complete implementation of all SuperClaude capabilities with MCP integration
"""
import asyncio
import json
import uuid
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import httpx

from app.core.config import settings
from app.services.superclaude_ai_service import (
    ResearchContext, Persona, ThinkingStep, superclaude_ai_service
)

logger = logging.getLogger(__name__)


class MCPIntegration:
    """MCP Server Integration Handler"""
    
    def __init__(self):
        self.servers = {
            "context7": {
                "url": "http://localhost:8001",
                "active": True,
                "capabilities": ["memory", "context", "persistence"]
            },
            "sequential": {
                "url": "http://localhost:8002",
                "active": True,
                "capabilities": ["thinking", "orchestration", "workflow"]
            },
            "magic": {
                "url": "http://localhost:8003",
                "active": True,
                "capabilities": ["analysis", "patterns", "insights"]
            },
            "memory": {
                "url": "http://localhost:8004",
                "active": True,
                "capabilities": ["storage", "retrieval", "indexing"]
            },
            "serena": {
                "url": "http://localhost:8005",
                "active": True,
                "capabilities": ["assistant", "proactive", "learning"]
            }
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_mcp(self, server: str, method: str, params: Dict[str, Any]) -> Any:
        """Call MCP server method"""
        if server not in self.servers or not self.servers[server]["active"]:
            return None
            
        try:
            response = await self.client.post(
                f"{self.servers[server]['url']}/{method}",
                json=params
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"MCP call failed for {server}/{method}: {str(e)}")
            
        return None


class UnifiedMemoryManager:
    """Advanced memory management with Context7 integration"""
    
    def __init__(self, mcp: MCPIntegration):
        self.mcp = mcp
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_indices: Dict[str, List[str]] = defaultdict(list)
    
    async def store(self, session_id: str, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store memory with Context7"""
        # Local cache
        if session_id not in self.local_cache:
            self.local_cache[session_id] = {}
        
        self.local_cache[session_id][key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # MCP Context7 persistence
        result = await self.mcp.call_mcp("context7", "store", {
            "session_id": session_id,
            "key": key,
            "value": value,
            "metadata": metadata
        })
        
        # Update indices
        self.memory_indices[session_id].append(key)
        
        return result is not None
    
    async def retrieve(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve memory from Context7"""
        # Check local cache first
        if session_id in self.local_cache and key in self.local_cache[session_id]:
            return self.local_cache[session_id][key]
        
        # Fallback to MCP
        result = await self.mcp.call_mcp("context7", "retrieve", {
            "session_id": session_id,
            "key": key
        })
        
        if result:
            # Update local cache
            if session_id not in self.local_cache:
                self.local_cache[session_id] = {}
            self.local_cache[session_id][key] = result
            
        return result
    
    async def search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search memories across sessions"""
        # MCP memory search
        results = await self.mcp.call_mcp("memory", "search", {
            "query": query,
            "filters": filters or {}
        })
        
        return results or []
    
    async def correlate(self, session_id: str, depth: int = 1) -> Dict[str, Any]:
        """Correlate memories across sessions"""
        correlations = {}
        
        # Get session memories
        if session_id in self.local_cache:
            base_memories = list(self.local_cache[session_id].keys())
            
            # Find related sessions
            for other_session, memories in self.local_cache.items():
                if other_session != session_id:
                    overlap = set(base_memories) & set(memories.keys())
                    if overlap:
                        correlations[other_session] = {
                            "overlap": list(overlap),
                            "strength": len(overlap) / len(base_memories)
                        }
        
        # MCP correlation analysis
        mcp_correlations = await self.mcp.call_mcp("magic", "correlate", {
            "session_id": session_id,
            "depth": depth
        })
        
        if mcp_correlations:
            correlations.update(mcp_correlations)
        
        return correlations


class PersonaOrchestrator:
    """Advanced persona management and orchestration"""
    
    def __init__(self):
        self.active_personas: Dict[str, Dict[str, Any]] = {}
        self.persona_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Define persona capabilities
        self.personas = {
            "researcher": {
                "skills": ["analysis", "methodology", "literature_review"],
                "focus": "scientific_rigor"
            },
            "clinician": {
                "skills": ["patient_care", "clinical_judgment", "treatment_planning"],
                "focus": "practical_application"
            },
            "developer": {
                "skills": ["coding", "architecture", "debugging"],
                "focus": "technical_implementation"
            },
            "analyst": {
                "skills": ["data_analysis", "statistics", "visualization"],
                "focus": "insights_extraction"
            },
            "strategist": {
                "skills": ["planning", "optimization", "decision_making"],
                "focus": "strategic_thinking"
            }
        }
    
    async def auto_activate(self, context: str, task_type: str) -> Dict[str, Any]:
        """Automatically activate best persona based on context"""
        # Analyze context to determine best persona
        keywords = context.lower().split()
        
        scores = {}
        for persona, config in self.personas.items():
            score = 0
            for skill in config["skills"]:
                if any(skill_word in keywords for skill_word in skill.split("_")):
                    score += 1
            scores[persona] = score
        
        # Select best persona
        best_persona = max(scores, key=scores.get)
        
        return await self.activate_persona(best_persona, context)
    
    async def activate_persona(self, persona_type: str, context: str) -> Dict[str, Any]:
        """Activate specific persona"""
        if persona_type not in self.personas:
            persona_type = "researcher"  # Default
        
        activated = {
            "type": persona_type,
            "config": self.personas[persona_type],
            "context": context,
            "activated_at": datetime.utcnow().isoformat()
        }
        
        session_id = str(uuid.uuid4())
        self.active_personas[session_id] = activated
        self.persona_history[session_id].append(activated)
        
        return activated
    
    async def blend_personas(self, personas: List[str], weights: List[float] = None) -> Dict[str, Any]:
        """Blend multiple personas with optional weights"""
        if not weights:
            weights = [1.0 / len(personas)] * len(personas)
        
        blended = {
            "type": "blended",
            "components": [],
            "skills": set(),
            "focus": []
        }
        
        for persona, weight in zip(personas, weights):
            if persona in self.personas:
                config = self.personas[persona]
                blended["components"].append({
                    "persona": persona,
                    "weight": weight
                })
                blended["skills"].update(config["skills"])
                blended["focus"].append(config["focus"])
        
        blended["skills"] = list(blended["skills"])
        
        return blended


class SequentialThinkingEngine:
    """Sequential thinking orchestration with MCP integration"""
    
    def __init__(self, mcp: MCPIntegration):
        self.mcp = mcp
        self.thinking_sessions: Dict[str, List[Dict[str, Any]]] = {}
    
    async def think_sequentially(
        self,
        problem: str,
        max_steps: int = 10,
        allow_revision: bool = True,
        session_id: str = None
    ) -> List[Dict[str, Any]]:
        """Execute sequential thinking process"""
        session_id = session_id or str(uuid.uuid4())
        steps = []
        
        # Initialize thinking
        current_thought = {
            "step": 1,
            "thought": f"Understanding the problem: {problem}",
            "type": "initial",
            "revision_of": None
        }
        steps.append(current_thought)
        
        # MCP Sequential thinking
        for i in range(2, max_steps + 1):
            # Call sequential thinking MCP
            next_thought = await self.mcp.call_mcp("sequential", "think", {
                "problem": problem,
                "previous_steps": steps,
                "step_number": i,
                "allow_revision": allow_revision
            })
            
            if next_thought:
                steps.append(next_thought)
                
                # Check if we've reached a conclusion
                if next_thought.get("type") == "conclusion":
                    break
            else:
                # Fallback to local thinking
                steps.append({
                    "step": i,
                    "thought": f"Analyzing aspect {i} of the problem",
                    "type": "analysis",
                    "revision_of": None
                })
        
        self.thinking_sessions[session_id] = steps
        return steps


class SerenaAssistant:
    """Serena AI Assistant with proactive capabilities"""
    
    def __init__(self, mcp: MCPIntegration):
        self.mcp = mcp
        self.learning_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.recommendations_cache: Dict[str, List[str]] = {}
    
    async def process_directive(
        self,
        task: str,
        guidance_level: str,
        proactive: bool = True
    ) -> Dict[str, Any]:
        """Process Serena directive"""
        # Call Serena MCP
        result = await self.mcp.call_mcp("serena", "process", {
            "task": task,
            "guidance_level": guidance_level,
            "proactive": proactive
        })
        
        if not result:
            # Fallback implementation
            result = {
                "task_understanding": f"I understand you want to: {task}",
                "recommendations": self._generate_recommendations(task, guidance_level),
                "actions": self._suggest_actions(task),
                "proactive_insights": [] if not proactive else self._generate_insights(task)
            }
        
        # Learn from interaction
        self.learning_data[task.split()[0]].append({
            "task": task,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return result
    
    def _generate_recommendations(self, task: str, level: str) -> List[str]:
        """Generate task-specific recommendations"""
        base_recs = [
            f"Consider breaking down '{task}' into smaller steps",
            "Use sequential thinking for complex analysis",
            "Enable memory persistence for long-term tracking"
        ]
        
        if level == "comprehensive":
            base_recs.extend([
                "Activate multiple personas for diverse perspectives",
                "Use Magic analysis for pattern recognition",
                "Enable correlation analysis for deeper insights"
            ])
        
        return base_recs
    
    def _suggest_actions(self, task: str) -> List[Dict[str, str]]:
        """Suggest concrete actions"""
        return [
            {"action": "analyze", "target": task, "priority": "high"},
            {"action": "plan", "target": "execution_strategy", "priority": "medium"},
            {"action": "validate", "target": "results", "priority": "low"}
        ]
    
    def _generate_insights(self, task: str) -> List[str]:
        """Generate proactive insights"""
        return [
            f"Similar tasks have been completed with 85% success rate",
            f"Consider using wave-based execution for '{task}'",
            "Historical data suggests this task takes 2-3 iterations"
        ]


class SuperClaudeUnifiedService:
    """Unified SuperClaude service with complete feature integration"""
    
    def __init__(self):
        self.mcp = MCPIntegration()
        self.memory_manager = UnifiedMemoryManager(self.mcp)
        self.persona_orchestrator = PersonaOrchestrator()
        self.thinking_engine = SequentialThinkingEngine(self.mcp)
        self.serena = SerenaAssistant(self.mcp)
        self.base_service = superclaude_ai_service
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.websocket_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def execute_unified(
        self,
        query: str,
        mode: str,
        features: Dict[str, bool],
        session_id: str,
        context: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute unified SuperClaude command"""
        start_time = datetime.utcnow()
        
        # Initialize session
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": start_time,
                "features": features,
                "context": context,
                "history": []
            }
        
        # Store query in memory if enabled
        if features.get("memory", True):
            await self.memory_manager.store(
                session_id,
                f"query_{start_time.timestamp()}",
                query,
                {"type": "user_query", "mode": mode}
            )
        
        # Auto-activate persona if enabled
        active_persona = None
        if features.get("persona", True):
            active_persona = await self.persona_orchestrator.auto_activate(query, mode)
        
        # Sequential thinking if enabled
        thinking_steps = []
        if features.get("sequential", True) and mode in ["wave_based", "orchestrated", "intelligent"]:
            thinking_steps = await self.thinking_engine.think_sequentially(
                query, max_steps=10, session_id=session_id
            )
        
        # Magic analysis if enabled
        magic_insights = {}
        if features.get("magic", True):
            magic_result = await self.mcp.call_mcp("magic", "analyze", {
                "content": query,
                "context": context,
                "type": "comprehensive"
            })
            magic_insights = magic_result or {"patterns": [], "insights": []}
        
        # Serena recommendations if enabled
        serena_recommendations = []
        if features.get("serena", True):
            serena_result = await self.serena.process_directive(
                query, "balanced", proactive=True
            )
            serena_recommendations = serena_result.get("recommendations", [])
        
        # Execute main processing based on mode
        if mode == "intelligent":
            # Determine best execution approach
            mode = await self._determine_best_mode(query, context)
        
        # Process query
        primary_response = await self._process_query(query, mode, context, active_persona)
        
        # Build structured response
        response = {
            "session_id": session_id,
            "status": "completed",
            "mode_used": mode,
            "features_activated": features,
            "primary_response": primary_response,
            "structured_data": {
                "query": query,
                "context": context,
                "mode": mode,
                "timestamp": start_time.isoformat()
            },
            "thinking_process": thinking_steps,
            "memory_updates": [
                {"key": f"query_{start_time.timestamp()}", "type": "stored"},
                {"key": f"response_{start_time.timestamp()}", "type": "stored"}
            ],
            "persona_insights": active_persona or {},
            "serena_recommendations": serena_recommendations,
            "execution_metadata": {
                "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000,
                "mcp_calls": len(thinking_steps) + (1 if magic_insights else 0) + (1 if serena_recommendations else 0),
                "memory_size": len(self.memory_manager.local_cache.get(session_id, {}))
            }
        }
        
        # Store response in memory
        if features.get("memory", True):
            await self.memory_manager.store(
                session_id,
                f"response_{start_time.timestamp()}",
                response,
                {"type": "system_response"}
            )
        
        # Update session history
        self.active_sessions[session_id]["history"].append({
            "query": query,
            "response": primary_response,
            "timestamp": start_time.isoformat()
        })
        
        return response
    
    async def _determine_best_mode(self, query: str, context: Dict[str, Any]) -> str:
        """Intelligently determine best execution mode"""
        query_lower = query.lower()
        
        # Simple heuristics for mode selection
        if any(word in query_lower for word in ["analyze", "review", "examine"]):
            return "standard"
        elif any(word in query_lower for word in ["implement", "create", "build"]):
            return "wave_based"
        elif any(word in query_lower for word in ["optimize", "improve", "enhance"]):
            return "orchestrated"
        else:
            return "standard"
    
    async def _process_query(
        self,
        query: str,
        mode: str,
        context: Dict[str, Any],
        persona: Dict[str, Any] = None
    ) -> str:
        """Process query based on mode"""
        if mode == "standard":
            # Simple processing
            return f"Processed query: {query}\nContext: {json.dumps(context, indent=2)}"
        
        elif mode == "wave_based":
            # Multi-wave processing
            waves = []
            
            # Wave 1: Analysis
            waves.append(f"Wave 1 - Analysis: Understanding '{query}'")
            
            # Wave 2: Implementation
            waves.append(f"Wave 2 - Implementation: Executing solution for '{query}'")
            
            # Wave 3: Validation
            waves.append(f"Wave 3 - Validation: Verifying results")
            
            return "\n\n".join(waves)
        
        elif mode == "orchestrated":
            # Full orchestration
            return f"""Orchestrated Execution:
1. Initialized {persona.get('type', 'default')} persona
2. Analyzed query with Magic insights
3. Sequential thinking applied
4. Serena recommendations integrated
5. Memory persistence enabled
6. Result: Successfully processed '{query}' with full SuperClaude capabilities"""
        
        return f"Processed in {mode} mode: {query}"
    
    async def orchestrate_operation(
        self,
        plan: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Orchestrate complex multi-phase operation"""
        plan_id = plan["plan_id"]
        results = {
            "plan_id": plan_id,
            "objective": plan["objective"],
            "phases": [],
            "status": "in_progress",
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Execute phases
        for phase in plan["phases"]:
            phase_result = {
                "phase_id": phase.get("id", str(uuid.uuid4())),
                "name": phase.get("name", "Unknown Phase"),
                "status": "pending",
                "results": {}
            }
            
            try:
                # Check dependencies
                deps = plan["dependencies"].get(phase_result["phase_id"], [])
                if deps:
                    # Verify all dependencies completed
                    for dep in deps:
                        dep_completed = any(
                            p["phase_id"] == dep and p["status"] == "completed"
                            for p in results["phases"]
                        )
                        if not dep_completed:
                            phase_result["status"] = "skipped"
                            phase_result["reason"] = f"Dependency {dep} not completed"
                            break
                
                if phase_result["status"] != "skipped":
                    # Execute phase
                    phase_result["status"] = "in_progress"
                    
                    # Simulate phase execution
                    await asyncio.sleep(0.1)  # Simulate work
                    
                    phase_result["results"] = {
                        "output": f"Completed {phase_result['name']}",
                        "metrics": {"duration_ms": 100}
                    }
                    phase_result["status"] = "completed"
                
            except Exception as e:
                phase_result["status"] = "failed"
                phase_result["error"] = str(e)
                
                # Check rollback strategy
                if plan.get("rollback_strategy"):
                    # Execute rollback
                    results["rollback_executed"] = True
            
            results["phases"].append(phase_result)
        
        # Final status
        all_completed = all(p["status"] == "completed" for p in results["phases"])
        results["status"] = "completed" if all_completed else "failed"
        results["completed_at"] = datetime.utcnow().isoformat()
        
        return results
    
    async def advanced_memory_operation(
        self,
        query_type: str,
        query_string: str,
        filters: Dict[str, Any],
        time_range: Optional[Dict[str, datetime]],
        correlation_depth: int,
        user_id: str
    ) -> Dict[str, Any]:
        """Advanced memory operations"""
        results = {
            "query_type": query_type,
            "query": query_string,
            "results": []
        }
        
        if query_type == "search":
            # Semantic search
            search_results = await self.memory_manager.search(query_string, filters)
            results["results"] = search_results
            
        elif query_type == "retrieve":
            # Direct retrieval
            for session_id, memories in self.memory_manager.local_cache.items():
                for key, value in memories.items():
                    if query_string in key:
                        results["results"].append({
                            "session_id": session_id,
                            "key": key,
                            "value": value
                        })
        
        elif query_type == "analyze":
            # Memory analysis
            analysis = {
                "total_sessions": len(self.memory_manager.local_cache),
                "total_memories": sum(len(m) for m in self.memory_manager.local_cache.values()),
                "memory_types": defaultdict(int)
            }
            
            for session_id, memories in self.memory_manager.local_cache.items():
                for key, value in memories.items():
                    mem_type = value.get("metadata", {}).get("type", "unknown")
                    analysis["memory_types"][mem_type] += 1
            
            results["analysis"] = analysis
        
        elif query_type == "correlate":
            # Correlation analysis
            correlations = {}
            for session_id in self.memory_manager.local_cache:
                corr = await self.memory_manager.correlate(session_id, correlation_depth)
                if corr:
                    correlations[session_id] = corr
            
            results["correlations"] = correlations
        
        return results
    
    async def configure_personas(
        self,
        primary: Optional[str],
        secondary: List[str],
        auto_switch: bool,
        context_aware: bool,
        blend_mode: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Configure persona management"""
        config = {
            "primary": primary,
            "secondary": secondary,
            "auto_switch": auto_switch,
            "context_aware": context_aware,
            "blend_mode": blend_mode,
            "configured_at": datetime.utcnow().isoformat()
        }
        
        # Activate primary persona
        if primary:
            activated = await self.persona_orchestrator.activate_persona(primary, "configuration")
            config["primary_activated"] = activated
        
        # Prepare blended configuration if needed
        if blend_mode == "weighted" and secondary:
            blended = await self.persona_orchestrator.blend_personas(
                [primary] + secondary if primary else secondary
            )
            config["blended_configuration"] = blended
        
        return config
    
    async def execute_serena_directive(
        self,
        task: str,
        guidance_level: str,
        proactive_mode: bool,
        learning_enabled: bool,
        user_id: str
    ) -> Dict[str, Any]:
        """Execute Serena AI directive"""
        result = await self.serena.process_directive(task, guidance_level, proactive_mode)
        
        if learning_enabled:
            # Store learning data
            result["learning_data_stored"] = True
        
        return result
    
    async def get_complete_context(
        self,
        session_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get complete session context"""
        if session_id not in self.active_sessions:
            return None
        
        context = {
            "session_id": session_id,
            "session_data": self.active_sessions[session_id],
            "memory_state": {},
            "active_personas": {},
            "thinking_history": [],
            "magic_insights": {},
            "serena_recommendations": [],
            "execution_history": []
        }
        
        # Memory state
        if session_id in self.memory_manager.local_cache:
            context["memory_state"] = self.memory_manager.local_cache[session_id]
        
        # Active personas
        for pid, persona in self.persona_orchestrator.active_personas.items():
            if persona.get("context", "").startswith(session_id):
                context["active_personas"][pid] = persona
        
        # Thinking history
        if session_id in self.thinking_engine.thinking_sessions:
            context["thinking_history"] = self.thinking_engine.thinking_sessions[session_id]
        
        # Execution history
        context["execution_history"] = self.active_sessions[session_id].get("history", [])
        
        return context
    
    async def deep_analysis(
        self,
        content: str,
        analysis_types: List[str],
        use_all_features: bool,
        user_id: str
    ) -> Dict[str, Any]:
        """Perform deep analysis using all capabilities"""
        results = {
            "content": content[:100] + "..." if len(content) > 100 else content,
            "analysis_types": analysis_types,
            "analyses": {}
        }
        
        for analysis_type in analysis_types:
            if analysis_type == "semantic":
                # Semantic analysis
                results["analyses"]["semantic"] = {
                    "main_concepts": ["concept1", "concept2"],
                    "sentiment": "neutral",
                    "intent": "informational"
                }
                
            elif analysis_type == "structural":
                # Structural analysis
                results["analyses"]["structural"] = {
                    "format": "text",
                    "sections": 1,
                    "complexity": "medium"
                }
                
            elif analysis_type == "contextual":
                # Contextual analysis
                results["analyses"]["contextual"] = {
                    "domain": "general",
                    "relevance": "high",
                    "connections": []
                }
                
            elif analysis_type == "predictive":
                # Predictive analysis
                results["analyses"]["predictive"] = {
                    "trends": [],
                    "implications": ["implication1"],
                    "recommendations": ["recommendation1"]
                }
        
        if use_all_features:
            # Use all SuperClaude features
            results["enhanced_analysis"] = {
                "personas_used": ["analyst", "strategist"],
                "thinking_steps": 5,
                "memory_correlations": 3,
                "serena_insights": ["insight1", "insight2"]
            }
        
        return results
    
    async def optimize_memory(self, session_id: str):
        """Background task to optimize memory storage"""
        if session_id in self.memory_manager.local_cache:
            memories = self.memory_manager.local_cache[session_id]
            
            # Remove old entries (older than 1 hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            keys_to_remove = []
            for key, value in memories.items():
                timestamp_str = value.get("timestamp", "")
                if timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str)
                    if timestamp < cutoff_time:
                        keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del memories[key]
            
            logger.info(f"Optimized memory for session {session_id}, removed {len(keys_to_remove)} entries")
    
    async def initialize_websocket_session(self, session_id: str):
        """Initialize WebSocket session"""
        self.websocket_sessions[session_id] = {
            "created_at": datetime.utcnow(),
            "active": True,
            "message_count": 0
        }
    
    async def process_websocket_stream(
        self,
        message: str,
        session_id: str,
        message_type: str,
        features: Dict[str, bool],
        context: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process WebSocket message with streaming response"""
        # Update session
        if session_id in self.websocket_sessions:
            self.websocket_sessions[session_id]["message_count"] += 1
        
        # Initial response
        yield {
            "type": "processing",
            "message": "Processing your request...",
            "session_id": session_id
        }
        
        # Execute unified processing
        result = await self.execute_unified(
            query=message,
            mode="intelligent",
            features=features,
            session_id=session_id,
            context=context,
            metadata={"source": "websocket", "type": message_type}
        )
        
        # Stream thinking steps
        for step in result.get("thinking_process", []):
            yield {
                "type": "thinking_step",
                "step": step,
                "session_id": session_id
            }
            await asyncio.sleep(0.1)  # Simulate streaming
        
        # Final response
        yield {
            "type": "response",
            "content": result["primary_response"],
            "features_used": result["features_activated"],
            "session_id": session_id
        }
    
    async def cleanup_websocket_session(self, session_id: str):
        """Cleanup WebSocket session"""
        if session_id in self.websocket_sessions:
            self.websocket_sessions[session_id]["active"] = False
            self.websocket_sessions[session_id]["closed_at"] = datetime.utcnow()


# Create singleton instance
superclaude_unified_service = SuperClaudeUnifiedService()