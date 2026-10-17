
SWITCH = 0 # 0: gemini   1: openai   2: qwen

MathVista_PATH = "Dataset/MathVista/MathVista.parquet"
EMMA_PATH = "Dataset/EMMA/PhysicsMini.parquet"
# Dataset/EMMA/PhysicsMini.parquet
# Dataset/EMMA/ChemistryMini.parquet
# Dataset/EMMA/MathMini.parquet

MZCO = "OE_MM_maths_zh_COMP"
MZCE = "OE_MM_maths_zh_CEE"
MECO = "OE_MM_maths_en_COMP"
PECO = "OE_MM_physics_en_COMP"
PZCE = "OE_MM_physics_zh_CEE"

OLYFILEPATH = MZCO

Olympiad_PATH = f"Dataset/OlympiadBench/{OLYFILEPATH}.parquet"
olympiad_result_full = f"Output/OlympiadBench/{OLYFILEPATH}/FULL/agent_output.json"
olympiad_result_wo_aligner = f"Output/OlympiadBench/{OLYFILEPATH}/woALIGNER/agent_output.json"
olympiad_result_wo_critic = f"Output/OlympiadBench/{OLYFILEPATH}/woCRITIC/agent_output.json"
olympiad_result_wo_interpreter = f"Output/OlympiadBench/{OLYFILEPATH}/woINTERPRETER/agent_output.json"
olympiad_result_wo_scholar = f"Output/OlympiadBench/{OLYFILEPATH}/woSCHOLAR/agent_output.json"

mathvista_agent_result = "Output/MathVista/agent_output.json"
mathvista_accuracy_result = "Output/MathVista/accuracy_results.json"
mathvista_correct_ids = "Output/MathVista/correct_ids.json"

emma_agent_result = "Output/EMMA/GPT-40/MathMini/agent_output.json"



API_KEY_GOOGLE = ""
MODEL_GOOGLE = ""

API_KEY = ""
MODEL_INTERPRETER = ""
MODEL_ALIGNER = ""
MODEL_SCHOLAR = ""
MODEL_SOLVER = ""
MODEL_CRITIC = ""


API_KEY_QWEN = ""
BASE_URL_QWEN = ""
MODEL_QWEN = ""
