
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" 
OPENAI_API_KEY = [
    "YOUR_API_KEY",
    "YOUR_API_KEY",
    "YOUR_API_KEY"
]
# LLM Configuration
# LLM_LOCAL_URL = "http://localhost:8001/v1"
# LLM_MODEL_NAME = "qwen2.5-7b"
LLM_LOCAL_URL = "http://localhost:8010/v1"
LLM_MODEL_NAME = "qwen-kto"
temperature = 0
# temperature = 0
max_tokens = 4096

# Matrix Configuration
MatrixBasePath = "./src/agent/memory/contingency_table_result.json"
MatrixUserPath = "./src/agent/memory/user_feedback_matrix_interp.json"

UTILS_LLM_URL = "http://localhost:8010/v1"
UTILS_LLM_MODEL_NAME = "qwen-kto"
UTILS_LLM_APIKEY = "EMPTY"

u_temperature = 0
# u_temperature = 0
u_max_tokens = 2048

# ==================== Rewriter LLM Configuration ====================
# Custom API for Rewriter/Generator (separate from utils LLM)
# REWRITER_LLM_URL = "http://localhost:8001/v1"
# REWRITER_LLM_MODEL_NAME = "qwen2.5-7b"
REWRITER_LLM_URL = "http://localhost:8010/v1"
REWRITER_LLM_MODEL_NAME = "qwen-kto"
REWRITER_LLM_API_KEY = "EMPTY"

REWRITER_TEMPERATURE = 0
# REWRITER_TEMPERATURE = 0
REWRITER_MAX_TOKENS = 4096

# ==================== Rewriter / Refinement Agent Configuration ====================
# Aggressive Mode: High quality standards with more iterations
REFINEMENT_MAX_ITERATIONS = 5
# REFINEMENT_MAX_ITERATIONS = 3 # User Chat Lower Iterations
REFINEMENT_CONVERGENCE_THRESHOLD = 0.7
REFINEMENT_MIN_SCORE_THRESHOLD = 0.55

REFINEMENT_WEIGHT_FEEDBACK = 0.5  # Feedback reward weight
REFINEMENT_WEIGHT_INFO = 0.5      # Mutual information reward weight
REFINEMENT_LAMBDA = 0.4           # Information gain weight λ

REFINEMENT_MAX_HISTORY_TURNS = 6    # Max conversation history turns to keep
REFINEMENT_MAX_PROMPT_HISTORY = 3     # Max prompt history versions to keep

REFINEMENT_SCORE_DROP_TOLERANCE = 0.1  # Score drop tolerance
REFINEMENT_ENABLE_EARLY_STOPPING = True  # Enable early stopping

# Log Configuration
class Colors:
    GREEN = "\033[32m"  # 绿色 (用于 Info / Success)
    YELLOW = "\033[33m" # 黄色 (用于 Warn)
    RED = "\033[31m"    # 红色 (用于 Error)
    RESET = "\033[0m"   # 重置颜色