# ============================================================
# ANCHOR 配置文件 — 使用前请根据实际环境修改以下参数
# ============================================================

# ---------- Sentence-Transformers 嵌入模型路径 ----------
# 用于 Stage 1 (因子聚类) 和 Stage 2 (KNN 检索)
# 需要下载 all-MiniLM-L6-v2 模型到本地路径，参见 README.md
MiniLM_L6_PATH = '/mnt/models/LLMs/all-MiniLM-L6-v2'

# ---------- 数据集选择 ----------
# 可选: common2sense, plasma, today, cnn, xsum, covid, expertqa
dataset_name = "common2sense"

# ---------- 数据与输出目录 ----------
# 相对路径，基于 code/run/ 目录
dataset_file_dic = "../../data/"
save_file_dic = "./results/"

# ---------- LLM API 配置 ----------
# 使用 OpenAI 兼容接口 (如 gpt-4o-mini / 本地 vLLM 服务 等)
model_name = 'gpt-4o-mini'
base_url = 'https://models-proxy.stepfun-inc.com/v1'   # 替换为你的 API 地址
api_key = 'your-api-key-here'                           # 替换为你的 API Key
