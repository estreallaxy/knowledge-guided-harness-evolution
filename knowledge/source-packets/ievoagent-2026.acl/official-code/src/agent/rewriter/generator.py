from configs import agent_config as agentcfg
from openai import OpenAI

# Configure client (using REWRITER_LLM configuration)
# client = OpenAI(
#     base_url=agentcfg.REWRITER_LLM_URL,
#     api_key=agentcfg.REWRITER_LLM_API_KEY,
# )
# MODEL_NAME = agentcfg.REWRITER_LLM_MODEL_NAME

client = OpenAI(
    base_url=agentcfg.REWRITER_LLM_URL,
    api_key="",
)

MODEL_NAME = agentcfg.REWRITER_LLM_MODEL_NAME

class Generator:
    """Generator - Generates responses using customizable prompts"""

    def __init__(self, model_name=None, temperature=None, max_tokens=None):
        self.model_name = model_name or MODEL_NAME
        self.temperature = temperature or agentcfg.REWRITER_TEMPERATURE
        self.max_tokens = max_tokens or agentcfg.REWRITER_MAX_TOKENS
        self.default_system_prompt = "You are a helpful assistant. Please provide accurate, relevant, and helpful responses to user queries."
        
    def generate(self, user_input: str, history: list = None, system_prompt: str = None) -> str:
        """
        Generate response
        
        Args:
            user_input: User input
            history: Conversation history [{"role": "user/assistant", "content": "..."}]
            system_prompt: Custom system prompt (uses default if None)
            
        Returns:
            str: Generated response
        """
        messages = []
        
        # Add system prompt (supports customization)
        messages.append({
            "role": "system",
            "content": system_prompt or self.default_system_prompt
        })
        
        # Add conversation history
        if history:
            messages.extend(history)
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            if response.choices[0].message.content is None:
                print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Generator returned None content")
                return ""
                
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Generator error: {e}")
            return ""
    
    def generate_with_context(self, user_input: str, history: list = None, 
                             additional_context: str = None) -> str:
        messages = []
        
        # Build system prompt (include additional context)
        system_prompt = "You are a helpful assistant. Please provide accurate, relevant, and helpful responses to user queries."
        if additional_context:
            system_prompt += f"\n\nAdditional Context:\n{additional_context}"
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history
        if history:
            messages.extend(history)
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            if response.choices[0].message.content is None:
                print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Generator returned None content")
                return ""
                
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Generator error: {e}")
            return ""


if __name__ == "__main__":
    # Test code
    generator = Generator()
    
    # Test simple generation
    response = generator.generate("What is the capital of France?")
    print(f"Response: {response}")
    
    # Test generation with history
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]
    response = generator.generate("Tell me about Paris", history=history)
    print(f"Response with history: {response}")
