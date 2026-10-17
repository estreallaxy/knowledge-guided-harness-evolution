from typing import Dict, List, Any, Optional
import logging
from vector_store import VectorStore
from llm_service import LLMService

logger = logging.getLogger(__name__)

class RAGWorkflow:
    """Simplified RAG workflow without LangGraph dependencies"""
    
    def __init__(self, vector_store: VectorStore, llm_service: LLMService):
        self.vector_store = vector_store
        self.llm_service = llm_service
        logger.info("RAG workflow initialized")
    
    async def _analyze_query(self, question: str) -> tuple[str, List[str]]:
        """Analyze and potentially improve the user query"""
        try:
            reasoning_steps = ["Analyzing user query for optimization"]
            
            # For now, we'll keep the query as-is
            # In a more advanced implementation, we could use the LLM to reformulate
            analyzed_query = question
            
            logger.info(f"Query analysis complete: {analyzed_query}")
            return analyzed_query, reasoning_steps
            
        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            return question, [f"Query analysis failed: {str(e)}"]
    
    async def _retrieve_documents(self, question: str, collection_name: str, top_k: int) -> tuple[List[Dict[str, Any]], List[str]]:
        """Retrieve relevant documents from the vector store"""
        try:
            reasoning_steps = [f"Retrieving top {top_k} documents from collection '{collection_name}'"]
            
            results = self.vector_store.query_documents(
                collection_name=collection_name,
                query_text=question,
                n_results=top_k
            )
            
            # Format retrieved documents
            retrieved_docs = []
            for i, (doc, metadata, distance, doc_id) in enumerate(zip(
                results["documents"],
                results["metadatas"],
                results["distances"],
                results["ids"]
            )):
                retrieved_docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "distance": distance,
                    "id": doc_id,
                    "rank": i + 1
                })
            
            reasoning_steps.append(f"Retrieved {len(retrieved_docs)} relevant documents")
            logger.info(f"Document retrieval complete: {len(retrieved_docs)} documents")
            return retrieved_docs, reasoning_steps
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            return [], [f"Document retrieval failed: {str(e)}"]
    
    async def _synthesize_context(self, retrieved_docs: List[Dict[str, Any]]) -> tuple[str, List[str]]:
        """Synthesize retrieved documents into coherent context"""
        try:
            reasoning_steps = ["Synthesizing retrieved documents into context"]
            
            if not retrieved_docs:
                return "No relevant documents found.", reasoning_steps
            
            # Combine document contents
            context_parts = []
            for doc in retrieved_docs:
                source_info = f"Source: {doc['metadata'].get('source', 'Unknown')}"
                context_parts.append(f"{source_info}\n{doc['content']}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            reasoning_steps.append(f"Context synthesized from {len(retrieved_docs)} documents")
            logger.info("Context synthesis complete")
            return context, reasoning_steps
            
        except Exception as e:
            logger.error(f"Error in context synthesis: {e}")
            return "Error occurred while processing retrieved documents.", [f"Context synthesis failed: {str(e)}"]
    
    async def _generate_answer(self, question: str, context: str) -> tuple[str, List[str]]:
        """Generate answer using LLM with retrieved context"""
        try:
            reasoning_steps = ["Generating answer using LLM with retrieved context"]
            
            rag_chain = self.llm_service.create_rag_chain()
            
            answer = await rag_chain.ainvoke({
                "context": context,
                "question": question
            })
            
            reasoning_steps.append("Answer generated successfully")
            logger.info("Answer generation complete")
            return answer, reasoning_steps
            
        except Exception as e:
            logger.error(f"Error in answer generation: {e}")
            return "I apologize, but I encountered an error while generating the answer.", [f"Answer generation failed: {str(e)}"]
    
    async def process_query(
        self,
        question: str,
        collection_name: str = "rag_collection",
        top_k: int = 3,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a RAG query through the workflow"""
        
        all_reasoning_steps = []
        
        try:
            # Step 1: Analyze query
            analyzed_query, steps = await self._analyze_query(question)
            all_reasoning_steps.extend(steps)
            
            # Step 2: Retrieve documents
            retrieved_docs, steps = await self._retrieve_documents(analyzed_query, collection_name, top_k)
            all_reasoning_steps.extend(steps)
            
            # Step 3: Synthesize context
            context, steps = await self._synthesize_context(retrieved_docs)
            all_reasoning_steps.extend(steps)
            
            # Step 4: Generate answer
            answer, steps = await self._generate_answer(question, context)
            all_reasoning_steps.extend(steps)
            
            return {
                "answer": answer,
                "context": context,
                "retrieved_docs": retrieved_docs,
                "reasoning_steps": all_reasoning_steps,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in RAG workflow: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question.",
                "context": "",
                "retrieved_docs": [],
                "reasoning_steps": all_reasoning_steps + [f"Workflow error: {str(e)}"],
                "success": False
            }
    
    async def process_chat(
        self,
        message: str,
        session_id: str,
        collection_name: str = "rag_collection",
        top_k: int = 3,
        chat_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a chat message through the RAG workflow"""
        
        # For chat, we use the same workflow but with conversation context
        result = await self.process_query(
            question=message,
            collection_name=collection_name,
            top_k=top_k,
            session_id=session_id
        )
        
        return {
            "response": result["answer"],
            "session_id": session_id,
            "retrieved_docs": result["retrieved_docs"],
            "reasoning_steps": result["reasoning_steps"],
            "success": result["success"]
        }
