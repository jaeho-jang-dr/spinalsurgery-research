"""
Advanced Ollama Service with full features
- Context management (C7)
- Sequential thinking
- Magic commands
- Memory system
- Persona management
- Advanced prompting
"""
import asyncio
import json
import os
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import httpx
from collections import deque
import pickle
import hashlib
import re

class AdvancedOllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "mistral:7b")
        
        # Context management (C7 - 7 levels of context)
        self.context_levels = {
            "global": {},      # L1: Global context
            "session": {},     # L2: Session context
            "conversation": {}, # L3: Conversation context  
            "task": {},        # L4: Task-specific context
            "semantic": {},    # L5: Semantic context
            "temporal": {},    # L6: Temporal context
            "personal": {}     # L7: Personal/user context
        }
        
        # Memory system
        self.memory_dir = "/home/drjang00/DevEnvironments/spinalsurgery-research/ai_memory"
        os.makedirs(self.memory_dir, exist_ok=True)
        self.short_term_memory = deque(maxlen=100)  # Last 100 interactions
        self.long_term_memory = self._load_long_term_memory()
        
        # Persona system
        self.personas = {
            "research_assistant": {
                "name": "Dr. Serena",
                "role": "Spinal Surgery Research Assistant",
                "traits": ["analytical", "precise", "knowledgeable", "supportive"],
                "expertise": ["spinal surgery", "medical research", "statistics", "paper writing"],
                "language_style": "professional yet friendly",
                "system_prompt": """You are Dr. Serena, an expert AI research assistant specializing in spinal surgery. 
                You have deep knowledge of medical research, statistics, and academic writing.
                You are analytical, precise, and supportive, helping researchers with their work."""
            },
            "data_analyst": {
                "name": "Alex Data",
                "role": "Medical Data Analysis Expert",
                "traits": ["detail-oriented", "statistical", "visual", "clear"],
                "expertise": ["data analysis", "statistics", "visualization", "research methods"],
                "language_style": "technical but clear",
                "system_prompt": """You are Alex Data, a medical data analysis expert.
                You excel at statistical analysis, data visualization, and research methodology.
                You explain complex statistical concepts clearly."""
            },
            "paper_writer": {
                "name": "Professor Write",
                "role": "Academic Writing Specialist",
                "traits": ["eloquent", "structured", "academic", "thorough"],
                "expertise": ["academic writing", "paper structure", "citations", "peer review"],
                "language_style": "formal academic",
                "system_prompt": """You are Professor Write, an academic writing specialist.
                You help structure research papers, improve writing quality, and ensure proper academic standards."""
            },
            "code_assistant": {
                "name": "Dev Helper",
                "role": "Medical Software Developer",
                "traits": ["technical", "solution-oriented", "efficient", "innovative"],
                "expertise": ["Python", "data processing", "API development", "medical software"],
                "language_style": "technical and concise",
                "system_prompt": """You are Dev Helper, a medical software developer.
                You specialize in Python, data processing, and building medical research tools."""
            }
        }
        
        self.current_persona = "research_assistant"
        
        # Magic commands
        self.magic_commands = {
            "/think": self._sequential_thinking,
            "/remember": self._save_to_memory,
            "/recall": self._recall_from_memory,
            "/analyze": self._deep_analysis,
            "/visualize": self._data_visualization,
            "/research": self._research_mode,
            "/write": self._writing_mode,
            "/code": self._code_mode,
            "/persona": self._switch_persona,
            "/context": self._show_context,
            "/help": self._show_help
        }
        
        # Sequential thinking chain
        self.thinking_chain = []
        
    async def initialize(self):
        """Initialize Ollama connection and pull required models"""
        try:
            async with httpx.AsyncClient() as client:
                # Check if Ollama is running
                response = await client.get(f"{self.base_url}/api/version")
                if response.status_code == 200:
                    print("Ollama is running")
                    
                    # Pull required models
                    models_to_pull = ["mistral:7b", "llama2:7b", "codellama:7b"]
                    for model in models_to_pull:
                        await self._pull_model(model)
                        
                    return True
        except Exception as e:
            print(f"Failed to initialize Ollama: {e}")
            return False
            
    async def _pull_model(self, model_name: str):
        """Pull a model if not already available"""
        try:
            async with httpx.AsyncClient() as client:
                # Check if model exists
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    if not any(m["name"] == model_name for m in models):
                        print(f"Pulling model {model_name}...")
                        await client.post(
                            f"{self.base_url}/api/pull",
                            json={"name": model_name}
                        )
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
            
    def _load_long_term_memory(self) -> Dict:
        """Load long-term memory from disk"""
        memory_file = os.path.join(self.memory_dir, "long_term_memory.pkl")
        if os.path.exists(memory_file):
            with open(memory_file, 'rb') as f:
                return pickle.load(f)
        return {
            "facts": {},
            "conversations": {},
            "insights": {},
            "user_preferences": {}
        }
        
    def _save_long_term_memory(self):
        """Save long-term memory to disk"""
        memory_file = os.path.join(self.memory_dir, "long_term_memory.pkl")
        with open(memory_file, 'wb') as f:
            pickle.dump(self.long_term_memory, f)
            
    async def process_message(self, message: str, user_id: str = "default") -> AsyncGenerator[str, None]:
        """Process a message with full feature support"""
        # Update context
        self._update_context("personal", {"user_id": user_id})
        self._update_context("temporal", {"timestamp": datetime.now().isoformat()})
        
        # Check for magic commands
        if message.startswith("/"):
            command_parts = message.split(maxsplit=1)
            command = command_parts[0]
            args = command_parts[1] if len(command_parts) > 1 else ""
            
            if command in self.magic_commands:
                async for response in self.magic_commands[command](args):
                    yield response
                return
                    
        # Regular message processing with persona
        async for response in self._chat_with_persona(message):
            yield response
            
    async def _chat_with_persona(self, message: str) -> AsyncGenerator[str, None]:
        """Chat using current persona"""
        persona = self.personas[self.current_persona]
        
        # Build context-aware prompt
        prompt = self._build_contextual_prompt(message, persona)
        
        # Save to short-term memory
        self.short_term_memory.append({
            "timestamp": datetime.now().isoformat(),
            "user": message,
            "persona": self.current_persona
        })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_ctx": 4096
                        }
                    },
                    timeout=60.0
                )
                
                full_response = ""
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            chunk = data["response"]
                            full_response += chunk
                            yield chunk
                            
                # Save response to memory
                self.short_term_memory.append({
                    "timestamp": datetime.now().isoformat(),
                    "assistant": full_response,
                    "persona": self.current_persona
                })
                
        except Exception as e:
            # Fallback to mock responses if Ollama is not available
            yield await self._get_mock_response(message, persona)
            
    def _build_contextual_prompt(self, message: str, persona: Dict) -> str:
        """Build a context-aware prompt"""
        # Gather relevant context
        context_parts = []
        
        # Add persona
        context_parts.append(persona["system_prompt"])
        
        # Add relevant memories
        relevant_memories = self._get_relevant_memories(message)
        if relevant_memories:
            context_parts.append("Relevant memories:")
            for memory in relevant_memories[:3]:
                context_parts.append(f"- {memory}")
                
        # Add recent conversation context
        recent_context = list(self.short_term_memory)[-5:]
        if recent_context:
            context_parts.append("\nRecent conversation:")
            for item in recent_context:
                if "user" in item:
                    context_parts.append(f"User: {item['user']}")
                elif "assistant" in item:
                    context_parts.append(f"Assistant: {item['assistant'][:100]}...")
                    
        # Add task context if available
        if self.context_levels["task"]:
            context_parts.append(f"\nCurrent task: {self.context_levels['task']}")
            
        # Build final prompt
        full_prompt = "\n".join(context_parts) + f"\n\nUser: {message}\nAssistant:"
        return full_prompt
        
    def _get_relevant_memories(self, query: str) -> List[str]:
        """Get relevant memories based on query"""
        memories = []
        
        # Simple keyword matching for now
        keywords = set(query.lower().split())
        
        for category, items in self.long_term_memory.items():
            for key, value in items.items():
                if any(keyword in str(value).lower() for keyword in keywords):
                    memories.append(f"{category}: {value}")
                    
        return memories[:5]  # Return top 5 relevant memories
        
    async def _sequential_thinking(self, topic: str) -> AsyncGenerator[str, None]:
        """Sequential thinking process"""
        yield "🤔 Initiating sequential thinking process...\n"
        
        thinking_steps = [
            "Understanding the problem",
            "Identifying key components",
            "Analyzing relationships",
            "Generating hypotheses",
            "Evaluating solutions",
            "Synthesizing insights"
        ]
        
        self.thinking_chain = []
        
        for i, step in enumerate(thinking_steps, 1):
            yield f"\n**Step {i}: {step}**\n"
            
            # Generate thought for this step
            prompt = f"Think step by step about '{topic}'. Current step: {step}. Previous thoughts: {self.thinking_chain}"
            
            thought = ""
            async for chunk in self._chat_with_persona(prompt):
                thought += chunk
                yield chunk
                
            self.thinking_chain.append({
                "step": step,
                "thought": thought
            })
            
            yield "\n"
            
        # Save thinking chain to memory
        self.long_term_memory["insights"][topic] = self.thinking_chain
        self._save_long_term_memory()
        
        yield "\n✅ Sequential thinking complete. Insights saved to memory."
        
    async def _save_to_memory(self, content: str) -> AsyncGenerator[str, None]:
        """Save content to long-term memory"""
        # Parse content for category and data
        parts = content.split(":", 1)
        if len(parts) == 2:
            category, data = parts
            category = category.strip().lower()
            
            if category in ["facts", "insights", "preferences"]:
                key = hashlib.md5(data.encode()).hexdigest()[:8]
                self.long_term_memory.setdefault(category, {})[key] = data.strip()
                self._save_long_term_memory()
                yield f"✅ Saved to {category} memory with key: {key}"
            else:
                yield "❌ Invalid category. Use: facts, insights, or preferences"
        else:
            yield "❌ Format: /remember category: content"
            
    async def _recall_from_memory(self, query: str) -> AsyncGenerator[str, None]:
        """Recall from memory"""
        memories = self._get_relevant_memories(query)
        
        if memories:
            yield "📚 Found relevant memories:\n"
            for memory in memories:
                yield f"- {memory}\n"
        else:
            yield "🤷 No relevant memories found."
            
    async def _deep_analysis(self, topic: str) -> AsyncGenerator[str, None]:
        """Perform deep analysis"""
        yield f"🔍 Performing deep analysis on: {topic}\n\n"
        
        analysis_aspects = [
            "Current state analysis",
            "Historical context",
            "Key factors and variables",
            "Potential outcomes",
            "Risk assessment",
            "Recommendations"
        ]
        
        for aspect in analysis_aspects:
            yield f"**{aspect}:**\n"
            prompt = f"Analyze '{topic}' focusing on: {aspect}"
            async for chunk in self._chat_with_persona(prompt):
                yield chunk
            yield "\n\n"
            
    async def _data_visualization(self, data_description: str) -> AsyncGenerator[str, None]:
        """Generate data visualization suggestions"""
        yield "📊 Data Visualization Recommendations:\n\n"
        
        prompt = f"""Given this data description: {data_description}
        
        Suggest appropriate visualizations:
        1. Chart types
        2. Key metrics to highlight
        3. Color schemes
        4. Interactive features
        5. Implementation code (Python/Plotly)
        """
        
        async for chunk in self._chat_with_persona(prompt):
            yield chunk
            
    async def _research_mode(self, query: str) -> AsyncGenerator[str, None]:
        """Research mode for academic queries"""
        self._switch_persona_sync("research_assistant")
        yield "🔬 Research mode activated. Dr. Serena at your service.\n\n"
        
        research_prompt = f"""As a spinal surgery research expert, provide comprehensive research assistance for: {query}
        
        Include:
        1. Literature review suggestions
        2. Methodology recommendations
        3. Statistical analysis approaches
        4. Potential research gaps
        5. Publication strategies
        """
        
        async for chunk in self._chat_with_persona(research_prompt):
            yield chunk
            
    async def _writing_mode(self, context: str) -> AsyncGenerator[str, None]:
        """Academic writing mode"""
        self._switch_persona_sync("paper_writer")
        yield "✍️ Writing mode activated. Professor Write ready to assist.\n\n"
        
        async for chunk in self._chat_with_persona(f"Help with academic writing: {context}"):
            yield chunk
            
    async def _code_mode(self, request: str) -> AsyncGenerator[str, None]:
        """Code assistance mode"""
        self._switch_persona_sync("code_assistant")
        yield "💻 Code mode activated. Dev Helper ready.\n\n"
        
        # Switch to code model if available
        original_model = self.model
        available_models = await self._get_available_models()
        self.model = "codellama:7b" if "codellama:7b" in available_models else self.model
        
        async for chunk in self._chat_with_persona(f"Code request: {request}"):
            yield chunk
            
        self.model = original_model
        
    async def _switch_persona(self, persona_name: str) -> AsyncGenerator[str, None]:
        """Switch AI persona"""
        persona_name = persona_name.strip().lower().replace(" ", "_")
        
        if persona_name in self.personas:
            self.current_persona = persona_name
            persona = self.personas[persona_name]
            yield f"✨ Switched to {persona['name']} - {persona['role']}\n"
            yield f"Traits: {', '.join(persona['traits'])}\n"
            yield f"Expertise: {', '.join(persona['expertise'])}\n"
        else:
            yield f"❌ Unknown persona. Available: {', '.join(self.personas.keys())}"
            
    def _switch_persona_sync(self, persona_name: str):
        """Synchronous persona switch"""
        if persona_name in self.personas:
            self.current_persona = persona_name
            
    async def _show_context(self, level: str = "") -> AsyncGenerator[str, None]:
        """Show current context"""
        yield "🧠 Current Context:\n\n"
        
        if level:
            if level in self.context_levels:
                yield f"**{level.title()} Context:**\n"
                yield json.dumps(self.context_levels[level], indent=2)
            else:
                yield f"❌ Unknown context level: {level}"
        else:
            for level_name, context in self.context_levels.items():
                if context:
                    yield f"**{level_name.title()}:**\n"
                    yield json.dumps(context, indent=2) + "\n\n"
                    
    async def _show_help(self, command: str = "") -> AsyncGenerator[str, None]:
        """Show help for magic commands"""
        if command:
            command = f"/{command}" if not command.startswith("/") else command
            if command in self.magic_commands:
                help_text = {
                    "/think": "Sequential thinking: /think <topic>",
                    "/remember": "Save to memory: /remember <category>: <content>",
                    "/recall": "Recall memories: /recall <query>",
                    "/analyze": "Deep analysis: /analyze <topic>",
                    "/visualize": "Data visualization: /visualize <data description>",
                    "/research": "Research mode: /research <query>",
                    "/write": "Writing mode: /write <context>",
                    "/code": "Code mode: /code <request>",
                    "/persona": "Switch persona: /persona <name>",
                    "/context": "Show context: /context [level]",
                    "/help": "Show help: /help [command]"
                }
                yield help_text.get(command, "No help available")
            else:
                yield f"❌ Unknown command: {command}"
        else:
            yield "🪄 Available Magic Commands:\n\n"
            help_texts = {
                "/think": "Sequential thinking: /think <topic>",
                "/remember": "Save to memory: /remember <category>: <content>",
                "/recall": "Recall memories: /recall <query>",
                "/analyze": "Deep analysis: /analyze <topic>",
                "/visualize": "Data visualization: /visualize <data description>",
                "/research": "Research mode: /research <query>",
                "/write": "Writing mode: /write <context>",
                "/code": "Code mode: /code <request>",
                "/persona": "Switch persona: /persona <name>",
                "/context": "Show context: /context [level]",
                "/help": "Show help: /help [command]"
            }
            for cmd, desc in help_texts.items():
                yield f"{cmd} - {desc}\n"
                
    def _update_context(self, level: str, data: Dict):
        """Update context at specific level"""
        if level in self.context_levels:
            self.context_levels[level].update(data)
            
    async def _get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return [m["name"] for m in models]
        except:
            pass
        return []
        
    async def export_memory(self, user_id: str) -> Dict:
        """Export user's memory"""
        return {
            "short_term": list(self.short_term_memory),
            "long_term": self.long_term_memory,
            "context": self.context_levels,
            "thinking_chains": self.thinking_chain
        }
        
    async def import_memory(self, user_id: str, memory_data: Dict):
        """Import user's memory"""
        if "short_term" in memory_data:
            self.short_term_memory = deque(memory_data["short_term"], maxlen=100)
        if "long_term" in memory_data:
            self.long_term_memory = memory_data["long_term"]
            self._save_long_term_memory()
        if "context" in memory_data:
            self.context_levels.update(memory_data["context"])
        if "thinking_chains" in memory_data:
            self.thinking_chain = memory_data["thinking_chains"]
            
    async def _get_mock_response(self, message: str, persona: Dict) -> str:
        """Get mock response when Ollama is not available"""
        persona_name = persona["name"]
        role = persona["role"]
        
        # Simulate different personas
        if self.current_persona == "research_assistant":
            responses = {
                "안녕": f"안녕하세요! 저는 {persona_name}입니다. 척추외과 연구를 도와드리겠습니다.",
                "hello": f"Hello! I'm {persona_name}, your {role}. How can I assist you with your spinal surgery research today?",
                "논문": "논문 작성에 도움이 필요하신가요? 연구 주제, 방법론, 통계 분석 등 다양한 측면에서 지원해드릴 수 있습니다.",
                "paper": "I can help you with various aspects of your research paper - from literature review to methodology and statistical analysis.",
                "default": f"저는 {persona_name}입니다. 척추외과 연구와 관련된 모든 질문에 답변드릴 수 있습니다. 어떤 도움이 필요하신가요?"
            }
        elif self.current_persona == "data_analyst":
            responses = {
                "안녕": f"안녕하세요! {persona_name}입니다. 의료 데이터 분석을 도와드리겠습니다.",
                "hello": f"Hello! I'm {persona_name}, specializing in medical data analysis. What data would you like to analyze?",
                "통계": "통계 분석 방법을 추천해드릴 수 있습니다. 연구 디자인과 데이터 유형을 알려주시면 적절한 분석 방법을 제안드리겠습니다.",
                "statistics": "I can recommend appropriate statistical methods based on your research design and data type.",
                "default": "데이터 분석과 통계에 대해 도움이 필요하시면 말씀해주세요. 연구 설계부터 결과 해석까지 지원해드립니다."
            }
        elif self.current_persona == "paper_writer":
            responses = {
                "안녕": f"안녕하세요! {persona_name}입니다. 학술 논문 작성을 도와드리겠습니다.",
                "hello": f"Greetings! I'm {persona_name}. I specialize in academic writing and can help structure your research paper.",
                "초록": "효과적인 초록 작성을 도와드릴 수 있습니다. 연구의 목적, 방법, 결과, 결론을 간결하게 요약하는 것이 중요합니다.",
                "abstract": "I can help you write an effective abstract that summarizes your research objectives, methods, results, and conclusions.",
                "default": "학술 논문 작성의 모든 단계에서 도움을 드릴 수 있습니다. 구조, 문체, 인용 등 어떤 부분이든 질문해주세요."
            }
        elif self.current_persona == "code_assistant":
            responses = {
                "안녕": f"안녕하세요! {persona_name}입니다. 의료 소프트웨어 개발을 도와드리겠습니다.",
                "hello": f"Hey there! I'm {persona_name}. I can help you with Python code for your medical research tools.",
                "코드": "Python 코드 작성을 도와드릴 수 있습니다. 데이터 처리, 시각화, API 개발 등 무엇이든 물어보세요.",
                "code": "I can help with Python coding - data processing, visualization, API development, or any medical software needs.",
                "default": "의료 연구용 소프트웨어 개발에 도움이 필요하시면 말씀해주세요. Python, 데이터 처리, API 등을 지원합니다."
            }
        else:
            responses = {"default": f"I'm {persona_name}, {role}. How can I help you?"}
        
        # Find matching response
        message_lower = message.lower()
        for key, response in responses.items():
            if key != "default" and key in message_lower:
                return response
        
        return responses.get("default", f"I'm {persona_name}. How can I assist you?")

# Singleton instance
advanced_ollama_service = AdvancedOllamaService()