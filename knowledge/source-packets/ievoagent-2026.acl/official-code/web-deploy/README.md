1️⃣ 第一步：启动 vLLM 模型服务 (显卡服务器)
这是最底层的推理引擎，负责加载模型权重。

位置：在你的显卡服务器上。

命令：

Bash
# 假设你用 Qwen-2.5-7B-Instruct 作为基础模型
# 注意：端口是 8001 (为了避开后端的 8000)
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/Qwen2.5-7B-Instruct \
    --served-model-name Qwen-2.5-Inst \
    --port 8001 \
    --trust-remote-code
(注：如果你显存不够跑多个模型，可以暂时只启动这一个，后端代码里会自动映射过去。)


2️⃣ 第二步：启动 FastAPI 后端 (中间层)
这是你的 server.py，负责处理任务逻辑、切换 Prompt 和调用 vLLM。

位置：在包含 server.py 的目录下。

**推荐：使用项目已有的 wildbench 环境**

Bash
conda activate wildbench
# 若该环境未装过 fastapi/uvicorn，执行一次: pip install fastapi uvicorn
cd web-deploy/backend
python server.py
成功标志：终端显示 Uvicorn running on http://0.0.0.0:8000。

（wildbench 里已通过 eval/WildBench/install_agent_deps.sh 装好 langchain、pandas 等；若使用 SOCKS 代理需再装 `pip install "httpx[socks]"`。）

**或使用 backend 自带 venv**

Bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python server.py

3️⃣ 第三步：启动 React 前端 (用户界面)
这是你的 App.jsx，负责给用户展示界面。

位置：在前端项目文件夹下 (cd ievo-study)。

命令：

Bash
npm run dev
成功标志：终端显示 Local: http://localhost:5173/。