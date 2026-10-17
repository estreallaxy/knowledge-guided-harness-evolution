import requests
import json
from typing import Dict, Any, List
from config import config
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL.rstrip('/')
        self.model = config.OLLAMA_MODEL
        self.temperature = config.OLLAMA_TEMPERATURE
        self.max_tokens = config.OLLAMA_MAX_TOKENS
        logger.info(f"LLM service initialized with model: {self.model}")
    
    def _make_request(self, prompt: str, **kwargs) -> str:
        """Make a request to Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "I apologize, but I encountered an error while processing your request."
                
        except Exception as e:
            logger.error(f"Error making Ollama request: {e}")
            return "I apologize, but I cannot connect to the language model right now."
    
    def create_rag_chain(self):
        """Create a RAG chain for answering questions with context"""
        def rag_chain(inputs: Dict[str, str]) -> str:
            prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.
If you cannot answer the question based on the context, say so clearly.

Context:
{inputs.get('context', '')}

Question: {inputs.get('question', '')}

Answer: Let me analyze the provided context to answer your question.
"""
            return self._make_request(prompt)
        
        return type('RAGChain', (), {'invoke': rag_chain, 'ainvoke': lambda self, inputs: rag_chain(inputs)})()
    
    def create_chat_chain(self):
        """Create a conversational chain"""
        def chat_chain(inputs: Dict[str, str]) -> str:
            prompt = f"""You are a helpful AI assistant having a conversation with a user.
Use the following context from a knowledge base to inform your responses when relevant.

Previous conversation context:
{inputs.get('chat_history', '')}

Knowledge base context:
{inputs.get('context', '')}

User message: {inputs.get('message', '')}

Response:
"""
            return self._make_request(prompt)
        
        return type('ChatChain', (), {'invoke': chat_chain, 'ainvoke': lambda self, inputs: chat_chain(inputs)})()
    
    def create_query_analysis_chain(self):
        """Create a chain to analyze and potentially reformulate queries"""
        def analysis_chain(inputs: Dict[str, str]) -> str:
            prompt = f"""Analyze the following user query and determine if it needs to be reformulated for better document retrieval.

Original query: {inputs.get('query', '')}

Consider:
1. Is the query specific enough?
2. Are there important keywords missing?
3. Could it be rephrased for better semantic search?

If the query is good as-is, return it unchanged.
If it needs improvement, provide a better version.

Improved query:
"""
            return self._make_request(prompt)
        
        return type('AnalysisChain', (), {'invoke': analysis_chain, 'ainvoke': lambda self, inputs: analysis_chain(inputs)})()
    
    def create_context_synthesis_chain(self):
        """Create a chain to synthesize multiple document chunks"""
        def synthesis_chain(inputs: Dict[str, str]) -> str:
            prompt = f"""You have retrieved multiple document chunks. Synthesize them into a coherent context summary.

Document chunks:
{inputs.get('chunks', '')}

Create a coherent summary that captures the key information from all chunks:
"""
            return self._make_request(prompt)
        
        return type('SynthesisChain', (), {'invoke': synthesis_chain, 'ainvoke': lambda self, inputs: synthesis_chain(inputs)})()
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response using the LLM"""
        try:
            return self._make_request(prompt.format(**kwargs))
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "I apologize, but I encountered an error while processing your request."
    
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
