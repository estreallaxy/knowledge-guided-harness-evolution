from typing import List, Dict, Optional, Literal, Any, Union
from pydantic import BaseModel, Field
import json_repair
import uuid
from datetime import datetime

from llm_controller import LLMController
from embedding_retriever import FlexibleEmbeddingRetriever


class MemoryNoteResponse(BaseModel):
    keywords: List[str] = Field(..., description="List of salient keywords")
    context: str = Field(..., description="Summarized context of the memory")
    tags: List[str] = Field(..., description="List of categorical tags")


class AMSResponse(BaseModel):
    should_evolve: bool = Field(..., description="Indicates if the memory should evolve")
    actions: List[str] = Field(..., description="List of actions to take, choose from ['strengthen', 'update_neighbor']")
    suggested_connections: List[int] = Field(..., description="List of neighbour memory ids to connect to")
    new_context_neighborhood: List[str] = Field(..., description="List of new context for the neighborhood memories")
    tags_to_update: List[str] = Field(..., description="Tags to update for the new memory")
    new_tags_neighborhood: List[List[str]] = Field(..., description="List of new tags for the neighborhood memories")


class MemoryNote:
    def __init__(self, 
                 content: str,
                 id: Optional[str] = None,
                 keywords: Optional[List[str]] = None,
                 links: Optional[Dict] = None,
                 importance_score: Optional[float] = None,
                 retrieval_count: Optional[int] = None,
                 timestamp: Optional[str] = None,
                 last_accessed: Optional[str] = None,
                 context: Optional[str] = None, 
                 evolution_history: Optional[List] = None,
                 category: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 llm_controller: Optional[LLMController] = None):
        
        self.content = content
        
        # Generate metadata using LLM if not provided and controller is available
        if llm_controller and any(param is None for param in [keywords, context, category, tags]):
            analysis = self.analyze_content(content, llm_controller)
            # print("analysis", analysis)
            keywords = keywords or analysis["keywords"]
            context = context or analysis["context"]
            tags = tags or analysis["tags"]
        
        # Set default values for optional parameters
        self.id = id or str(uuid.uuid4())
        self.keywords = keywords or []
        self.links = links or []
        self.importance_score = importance_score or 1.0
        self.retrieval_count = retrieval_count or 0
        current_time = datetime.now().strftime("%Y%m%d%H%M")
        self.timestamp = timestamp or current_time
        self.last_accessed = last_accessed or current_time
        
        # Handle context that can be either string or list
        self.context = context or "General"
        if isinstance(self.context, list):
            self.context = " ".join(self.context)  # Convert list to string by joining
            
        self.evolution_history = evolution_history or []
        self.category = category or "Uncategorized"
        self.tags = tags or []

    @staticmethod
    def analyze_content(content: str, llm_controller, max_retries=3) -> Dict:            
        """Analyze content to extract keywords, context, and other metadata"""
        prompt = """Generate a structured analysis of the following content by:
            1. Identifying the most salient keywords (focus on nouns, verbs, and key concepts)
            2. Extracting core themes and contextual elements
            3. Creating relevant categorical tags

            Format the response as a JSON object:
            {
                "keywords": [
                    // several specific, distinct keywords that capture key concepts and terminology
                    // Order from most to least important
                    // Don't include keywords that are the name of the speaker or time
                    // At least three keywords, but don't be too redundant.
                ],
                "context": 
                    // one sentence summarizing:
                    // - Main topic/domain
                    // - Key arguments/points
                    // - Intended audience/purpose
                ,
                "tags": [
                    // several broad categories/themes for classification
                    // Include domain, format, and type tags
                    // At least three tags, but don't be too redundant.
                ]
            }

            Content for analysis:
            """ + content
        
        response = None
        for attempt in range(max_retries):
            try:
                response = llm_controller.llm.get_completion(prompt,response_format={"type": "json_schema", "json_schema": {
                        "name": "response",
                        "schema": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                            },
                            "context": {
                            "type": "string",
                            },
                            "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                            },
                        },
                        "required": ["keywords", "context", "tags"],
                        "additionalProperties": False
                        },
                        "strict": True
                    }
                }, extra_body=MemoryNoteResponse)
                
                try:
                    analysis = json_repair.loads(response)
                except:
                    print(f"JSON repair failed on response: {response} (attempt {attempt + 1}/{max_retries})")
                    continue

                # check keywords, context, tags
                if (not isinstance(analysis.get("keywords"), list) or
                    not isinstance(analysis.get("context"), str) or len(analysis.get("context").strip()) == 0 or
                    not isinstance(analysis.get("tags"), list)):
                    print(f"Invalid analysis format (attempt {attempt + 1}/{max_retries}): {analysis}")
                    continue
                
                return analysis
        
            except Exception as e:
                print(f"Error analyzing content (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if response is not None:
                    print(f"Raw response: {response}")
                if attempt == max_retries - 1:  # Last attempt
                    print("All retry attempts failed")
        
        return {
            "keywords": [],
            "context": "General",
            "tags": []
        }
            

class FlexibleAgenticMemorySystem:
    """
    Extended AgenticMemorySystem with flexible retriever support.
    
    This class provides a flexible memory system supporting multiple
    embedding models and retrieval strategies.
    """
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 model_type: Literal['sentence-transformer', 'contriever', 'stella', 'gte', 'openai', 'bm25'] = 'sentence-transformer',
                 llm_backend: str = "openai",
                 llm_model: str = "gpt-4o-mini",
                 evo_threshold: int = 100,
                 api_key: Optional[str] = None,
                 device: str = None,
                 cache_dir: str = None,
                 base_url: Optional[str] = None,
                 embedding_api_key: Optional[str] = None,
                 embedding_base_url: Optional[str] = None):
        """
        Initialize the flexible agentic memory system.
        
        Args:
            model_name: Name of the embedding model
            model_type: Type of embedding model
            llm_backend: LLM backend (openai/ollama)
            llm_model: LLM model name
            evo_threshold: Evolution threshold
            api_key: API key for LLM
            device: Device to run embedding model on
            cache_dir: Cache directory for models
            base_url: Base URL for LLM API
            embedding_api_key: API key for embedding model (if different from api_key)
            embedding_base_url: Base URL for embedding API (if different from base_url)
        """
        # Initialize memory storage
        self.memories = {}  # id -> MemoryNote
        
        # Initialize LLM controller with enhanced features
        self.llm_controller = LLMController(llm_backend, llm_model, api_key, base_url=base_url, use_json_schema=True if 'gpt' in llm_model else False)
        
        # Use separate API key for embeddings if provided, otherwise use the same as LLM
        emb_api_key = embedding_api_key if embedding_api_key else api_key
        emb_base_url = embedding_base_url if embedding_base_url else base_url
        
        # Initialize flexible retriever
        self.retriever = FlexibleEmbeddingRetriever(
            model_name=model_name, 
            model_type=model_type,
            device=device,
            cache_dir=cache_dir,
            api_key=emb_api_key,
            base_url=emb_base_url
        )
        
        # Evolution system configuration
        self.evo_cnt = 0
        self.evo_threshold = evo_threshold
        
        # Evolution system prompt
        self.evolution_system_prompt = '''
                                You are an AI memory evolution agent responsible for managing and evolving a knowledge base.
                                Analyze the the new memory note according to keywords and context, also with their several nearest neighbors memory.
                                Make decisions about its evolution.  

                                The new memory context:
                                {context}
                                content: {content}
                                keywords: {keywords}

                                The nearest neighbors memories:
                                {nearest_neighbors_memories}

                                Based on this information, determine:
                                1. Should this memory be evolved? Consider its relationships with other memories.
                                2. What specific actions should be taken (strengthen, update_neighbor)?
                                   2.1 If choose to strengthen the connection, which memory should it be connected to? Can you give the updated tags of this memory?
                                   2.2 If choose to update_neighbor, you can update the context and tags of these memories based on the understanding of these memories. If the context and the tags are not updated, the new context and tags should be the same as the original ones. Generate the new context and tags in the sequential order of the input neighbors.
                                Tags should be determined by the content of these characteristic of these memories, which can be used to retrieve them later and categorize them.
                                Note that the length of new_tags_neighborhood must equal the number of input neighbors, and the length of new_context_neighborhood must equal the number of input neighbors.
                                The number of neighbors is {neighbor_number}.
                                Return your decision in JSON format with the following structure:
                                {{
                                    "should_evolve": True or False,
                                    "actions": ["strengthen", "update_neighbor"],
                                    "suggested_connections": ["neighbor_memory_ids"],
                                    "tags_to_update": ["tag_1",..."tag_n"], 
                                    "new_context_neighborhood": ["new context",...,"new context"],
                                    "new_tags_neighborhood": [["tag_1",...,"tag_n"],...["tag_1",...,"tag_n"]],
                                }}
                                '''
        
        # Store model config
        self.model_name = model_name
        self.model_type = model_type
        self.device = device
        self.cache_dir = cache_dir
        self.embedding_api_key = emb_api_key
        self.embedding_base_url = emb_base_url
    
    def consolidate_memories(self):
        """Consolidate memories: update retriever with new documents"""
        # Reset the retriever with same configuration
        self.retriever = FlexibleEmbeddingRetriever(
            model_name=self.model_name,
            model_type=self.model_type,
            device=self.device,
            cache_dir=self.cache_dir,
            api_key=self.embedding_api_key,
            base_url=self.embedding_base_url
        )
        
        # Re-add all memory documents with their metadata
        for memory in self.memories.values():
            metadata_text = f"{memory.context} {' '.join(memory.keywords)} {' '.join(memory.tags)}"
            self.retriever.add_documents([memory.content + " , " + metadata_text])

    def add_note(self, content: str, time: str = None, raw_sess_id=None, **kwargs) -> str:
        """Add a new memory note"""
        note = MemoryNote(content=content, llm_controller=self.llm_controller, timestamp=time, **kwargs)
        note.raw_content = content  # NOTE: manually store original context
        note.raw_sess_id = raw_sess_id  # manually add id
        # TODO not sure why it generate duplicated contents
        note.keywords = list(set(note.keywords))
        note.tags = list(set(note.tags))
        
        # Update retriever with all documents
        # all_docs = [m.content for m in self.memories.values()]
        evo_label, note = self.process_memory(note)
        self.memories[note.id] = note
        self.retriever.add_documents(["content:" + note.content + " context:" + note.context + " keywords: " + ", ".join(note.keywords) + " tags: " + ", ".join(note.tags)])
        if evo_label == True:
            self.evo_cnt += 1
            if self.evo_cnt % self.evo_threshold == 0:
                self.consolidate_memories()
        return note.id, note
  
    def process_memory(self, note: MemoryNote, max_retries: int = 3) -> bool:
        """Process a memory note and return an evolution label"""
        neighbor_memory, indices = self.find_related_memories(note.content, k=5)
        prompt_memory = self.evolution_system_prompt.format(context=note.context, content=note.content, keywords=note.keywords, nearest_neighbors_memories=neighbor_memory,neighbor_number=len(indices))
        # print("prompt_memory", prompt_memory)
        
        response = None
        response_json = None
        
        for attempt in range(max_retries):
            try:
                response = self.llm_controller.llm.get_completion(
                    prompt_memory,response_format={"type": "json_schema", "json_schema": {
                                "name": "response",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "should_evolve": {
                                            "type": "boolean",
                                        },
                                        "actions": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "suggested_connections": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer"
                                            }
                                        },
                                        "new_context_neighborhood": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "tags_to_update": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        },
                                        "new_tags_neighborhood": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                }
                                            }
                                        }
                                    },
                                    "required": ["should_evolve","actions","suggested_connections","tags_to_update","new_context_neighborhood","new_tags_neighborhood"],
                                    "additionalProperties": False
                                },
                                "strict": True
                            }},
                    extra_body=AMSResponse
                )
                
                try:
                    response_json = json_repair.loads(response)
                except Exception as json_error:
                    print(f"JSON parsing failed on response (attempt {attempt + 1}/{max_retries}): {json_error}")
                    if response is not None:
                        print(f"Raw response: {response}")
                    continue
                
                # Validate required fields are present
                required_fields = ["should_evolve", "actions", "suggested_connections", 
                                 "tags_to_update", "new_context_neighborhood", "new_tags_neighborhood"]
                missing_fields = [field for field in required_fields if field not in response_json]
                
                if missing_fields:
                    print(f"Missing required fields (attempt {attempt + 1}/{max_retries}): {missing_fields}")
                    print(f"Response JSON: {response_json}")
                    continue
                
                # Validate field types
                if not isinstance(response_json.get("should_evolve"), bool):
                    print(f"Invalid 'should_evolve' type (attempt {attempt + 1}/{max_retries}): expected bool, got {type(response_json.get('should_evolve'))}")
                    continue
                
                if not isinstance(response_json.get("actions"), list):
                    print(f"Invalid 'actions' type (attempt {attempt + 1}/{max_retries}): expected list, got {type(response_json.get('actions'))}")
                    continue
                
                # If we get here, the response is valid
                break
                
            except Exception as e:
                print(f"Error processing memory (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if response is not None:
                    print(f"Raw response: {response}")
                if attempt == max_retries - 1:  # Last attempt
                    print("All retry attempts failed, returning default values")
                    return False, note
        
        # If all retries failed
        if response_json is None:
            print("Failed to get valid response after all retries, returning default values")
            return False, note
        
        should_evolve = response_json["should_evolve"]
        if should_evolve:
            actions = response_json["actions"]
            for action in actions:
                if action == "strengthen":
                    suggest_connections = response_json.get("suggested_connections", [])
                    new_tags = response_json.get("tags_to_update", [])
                    note.links.extend(suggest_connections)
                    note.tags = new_tags
                elif action == "update_neighbor":
                    new_context_neighborhood = response_json.get("new_context_neighborhood", [])
                    new_tags_neighborhood = response_json.get("new_tags_neighborhood", [])
                    noteslist = list(self.memories.values())
                    notes_id = list(self.memories.keys())
                    # print("indices", indices)
                    # if slms output less than the number of neighbors, use the sequential order of new tags and context.
                    for i in range(min(len(indices), len(new_tags_neighborhood))):
                        # find some memory
                        tag = new_tags_neighborhood[i]
                        if i < len(new_context_neighborhood):
                            context = new_context_neighborhood[i]
                        else:
                            context = noteslist[indices[i]].context
                        memorytmp_idx = indices[i]
                        notetmp = noteslist[memorytmp_idx]
                        # add tag to memory
                        notetmp.tags = tag
                        notetmp.context = context
                        self.memories[notes_id[memorytmp_idx]] = notetmp
        return should_evolve,note

    def find_related_memories(self, query: str, k: int = 5) -> tuple[str, List[int]]:
        """Find related memories using retrieval
        
        Args:
            query: Query text to search for related memories
            k: Number of related memories to retrieve
            
        Returns:
            tuple: (formatted memory string, list of memory indices)
        """
        if not self.memories:
            return "", []
            
        # Get indices of related memories
        indices = self.retriever.search(query, k)
        
        # Convert to list of memories
        all_memories = list(self.memories.values())
        memory_str = ""
        for i in indices:
            memory_str += "memory index:" + str(i) + "\t talk start time:" + all_memories[i].timestamp + "\t memory content: " + all_memories[i].content + "\t memory context: " + all_memories[i].context + "\t memory keywords: " + str(all_memories[i].keywords) + "\t memory tags: " + str(all_memories[i].tags) + "\n"
        return memory_str, indices

    def find_related_memories_raw(self, query: str, k: int = 5) -> str:
        """Find related memories using retrieval and include their linked neighbors
        
        Args:
            query: Query text to search for related memories
            k: Number of related memories to retrieve
            
        Returns:
            str: Formatted string containing memories and their linked neighbors
        """
        if not self.memories:
            return ""
            
        # Get indices of related memories
        indices = self.retriever.search(query, k)
        
        # Convert to list of memories
        all_memories = list(self.memories.values())
        memory_str = ""
        j = 0
        for i in indices:
            memory_str += "talk start time:" + all_memories[i].timestamp + "memory content: " + all_memories[i].content + "memory context: " + all_memories[i].context + "memory keywords: " + str(all_memories[i].keywords) + "memory tags: " + str(all_memories[i].tags) + "\n"
            neighborhood = all_memories[i].links
            for neighbor in neighborhood:
                memory_str += "talk start time:" + all_memories[neighbor].timestamp + "memory content: " + all_memories[neighbor].content + "memory context: " + all_memories[neighbor].context + "memory keywords: " + str(all_memories[neighbor].keywords) + "memory tags: " + str(all_memories[neighbor].tags) + "\n"
                if j >= k:
                    break
                j += 1
        return memory_str