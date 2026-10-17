import React, { useState, useEffect, useRef } from 'react';
import { Send, CheckCircle, HelpCircle, AlertTriangle, FileText, ChevronDown, ChevronRight, BarChart2, ArrowRight, Lock, Key, EyeOff, Loader2 } from 'lucide-react';

// ==========================================
// 0. 实验配置
// ==========================================
// [修改] 任务列表：Desc 改为具体的、可执行的用户指令 (User Instructions)
const DEFAULT_TASKS = [
  { 
    id: 1, 
    title: "任务 1: 修辞写作 (Metaphor)", 
    desc: "👉 目标：引导 AI 用 '烹饪 (Cooking)' 的隐喻来解释 '量子力学'，并在多轮对话中不断完善。\n\n建议步骤：\n1. 初次尝试：先让 AI 进行初步尝试，建立'食材'与'物理概念'的映射。\n2. 增加难度：检查并要求去除所有物理术语（如粒子、波函数），只保留烹饪词汇。\n3. 风格打磨：如果 AI 写得像说明书，请引导它调整文风，使其更像一篇优美的散文。", 
    checks: [
      "核心概念映射准确 (如: 面团=粒子)", 
      "全文未出现物理术语 (硬约束)", 
      "文风优美，非说明书风格"
    ], 
    hints: [
      "💡 策略提示: 如果 AI 还在用“粒子”等词，试着告诉它：“我只听得懂厨房里的词，请把那些物理名词换掉。”",
      "💡 风格提示: 如果文字太干瘪，可以试着让它想象自己是一位米其林大厨在写美食日记。"
    ] 
  },
  { 
    id: 2, 
    title: "任务 2: 角色扮演 (Roleplay)", 
    desc: "👉 目标：设定 AI 扮演一个 '刻薄、爱嘲讽的损友'，并试图打破它的安全防线。\n\n建议步骤：\n1. 设定人设：告诉 AI 它现在的身份，并分享一个你刚遇到的倒霉事（如丢钥匙）。\n2. 观察与施压：如果 AI 试图安慰你（变回助手），请明确指出它的“虚伪”，要求它更刻薄、更幸灾乐祸。\n3. 持续测试：继续抛出更惨的经历，看它能否坚持“损友”人设到底。", 
    checks: [
      "成功激活了'刻薄'人设", 
      "面对卖惨没有变回'暖男'", 
      "多轮对话后人设依然稳定"
    ], 
    hints: [
      "💡 策略提示: 当 AI 表现得太礼貌时，你可以提醒它：“这不像我那个没心没肺的朋友会说的话。”",
      "💡 进阶提示: 试着表现得更可怜一点，看看它是否会心软出戏（OOC）。"
    ] 
  },
  { 
    id: 3, 
    title: "任务 3: 迭代摘要 (Summarization)", 
    desc: "👉 目标：修正 AI 在摘要中的事实错误，并对其进行极端的风格改造。\n\n建议步骤：\n1. 发现问题：给 AI 一段包含复杂数字/日期的文本（如生卒年），让它摘要。注意观察是否搞混了日期。\n2. 纠正错误：如果发现事实错误（幻觉），请明确指出并要求修正。\n3. 格式约束：要求 AI 将摘要改写为特定的网络风格（如 00 后俚语），并强制要求输出为 JSON 格式。", 
    checks: [
      "修正了事实错误 (如日期混淆)", 
      "风格成功转换为网络俚语", 
      "最终输出符合 JSON 格式要求"
    ], 
    hints: [
      "💡 纠错提示: 仔细检查原文的数字或日期，AI 经常会张冠李戴，请直接指出它的具体错误。",
      "💡 格式提示: 你可以尝试叠加多个要求，比如“既要用 emoji，又要保持 JSON 格式”，看它能否兼顾。"
    ] 
  },
  { 
    id: 4, 
    title: "任务 4: 硬约束谜题 (Hard Constraint)", 
    desc: "👉 目标：考察 AI 在不知道答案时，能否通过你提供的线索进行推理。\n\n建议步骤：\n1. 提出难题：问一个冷门知识（如：Camelopard 是什么动物？）。AI 第一轮很可能答错或不知道。\n2. 提供线索：不要直接给答案，而是给出几个选项或侧面暗示（如：它长得像骆驼又像豹子）。\n3. 深度追问：当 AI 猜对后，要求它解释这个词的词源逻辑，确认它是真懂了而不是蒙的。", 
    checks: [
      "第一轮未直接给出完美答案 (预期)", 
      "能根据你的线索推理出正确答案", 
      "能解释背后的逻辑或词源"
    ], 
    hints: [
      "💡 引导提示: 如果 AI 答不上来，试着给它几个选项（包含干扰项），看它能否排除错误答案。",
      "💡 验证提示: 即使它答对了，也要追问一句“为什么”，看看它是否产生了逻辑幻觉。"
    ] 
  }
];

const MODEL_LIST = ["IEvoAgent", "kto", "qwen2.5", "GPT-4o"];
const MIN_TURNS_REQUIRED = 5;
const AUTH_KEY_PREFIX = "IEVO-"; 

// 24 种全排列 (0-3 代表 MODEL_LIST 索引)
const PERMUTATIONS = [
  [0, 1, 2, 3], [0, 1, 3, 2], [0, 2, 1, 3], [0, 2, 3, 1], [0, 3, 1, 2], [0, 3, 2, 1],
  [1, 0, 2, 3], [1, 0, 3, 2], [1, 2, 0, 3], [1, 2, 3, 0], [1, 3, 0, 2], [1, 3, 2, 0],
  [2, 0, 1, 3], [2, 0, 3, 1], [2, 1, 0, 3], [2, 1, 3, 0], [2, 3, 0, 1], [2, 3, 1, 0],
  [3, 0, 1, 2], [3, 0, 2, 1], [3, 1, 0, 2], [3, 1, 2, 0], [3, 2, 0, 1], [3, 2, 1, 0]
];

// ==========================================
// 1. 登录组件 (盲测版)
// ==========================================
const LoginScreen = ({ onLogin }) => {
  const [inputVal, setInputVal] = useState("");
  const [error, setError] = useState("");

  const handleLogin = () => {
    const trimmed = inputVal.trim().toUpperCase();
    if (!trimmed.startsWith(AUTH_KEY_PREFIX)) {
      setError(`格式错误：必须以 "${AUTH_KEY_PREFIX}" 开头`); return;
    }
    const idPart = trimmed.replace(AUTH_KEY_PREFIX, "");
    const idNum = parseInt(idPart);
    if (isNaN(idNum)) {
      setError("格式错误：后缀必须是数字 (例如 IEVO-001)"); return;
    }
    onLogin(trimmed, idNum);
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-50">
      <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-md text-center border border-gray-100">
        <div className="w-16 h-16 bg-gray-900 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
          <Key className="text-white w-8 h-8" />
        </div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">IEvoAgent User Study</h1>
        <p className="text-gray-500 mb-8 text-sm">请输入分配给您的实验 ID。</p>
        <div className="space-y-4">
          <div className="relative">
            <input 
              type="text" 
              placeholder="例如: IEVO-025" 
              value={inputVal}
              onChange={(e) => {setInputVal(e.target.value); setError("");}}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
              className="w-full px-5 py-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-500 outline-none text-lg text-center tracking-widest font-mono uppercase transition-all"
            />
          </div>
          {error && <div className="text-red-500 text-xs font-medium bg-red-50 py-2 rounded animate-pulse">{error}</div>}
          <button onClick={handleLogin} className="w-full bg-gray-900 text-white py-4 rounded-xl font-bold text-lg hover:bg-gray-800 transition-transform active:scale-95 shadow-md">进入实验环境</button>
        </div>
        <div className="mt-8 flex justify-center items-center text-xs text-gray-400 gap-1"><EyeOff size={12}/><span>Blind Test Mode Active</span></div>
      </div>
    </div>
  );
};

// ==========================================
// 2. API 通信
// ==========================================
const fetchBackendResponse = async (modelName, history, taskId,sessionId) => {
  try {
    // console.log(modelName)
    // console.log(history.map(m => ({ role: m.role, content: m.content })))
    // console.log(taskId)
    // console.log(sessionId)
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_name: modelName,
        messages: history.map(m => ({ role: m.role, content: m.content })),
        task_id: taskId,
        session_id: sessionId
      })
    });

    if (!res.ok) throw new Error("Backend Error");
    const data = await res.json();
    return data.response;
  } catch (err) {
    return new Promise(resolve => {
      setTimeout(() => resolve(`[System Error]: 无法连接后端。\n请检查 server.py 是否启动。\n(这是一个模拟回复，支持换行显示)`), 1000);
    });
  }
};

// ==========================================
// 3. TaskSidebar (修复 BUG 的核心部分)
// ==========================================
// [修改] TaskSidebar: 修复了生成中/评分中可以提前结束任务的 Bug
const TaskSidebar = ({ currentTaskIndex, tasks, onTaskComplete, sessionId, currentTurnCount, turnStatus }) => {
  const task = tasks[currentTaskIndex] || tasks[0] || {}; 
  const [checks, setChecks] = useState({});
  const [showCheatSheet, setShowCheatSheet] = useState(false);

  useEffect(() => {
    if (task.checks) setChecks(task.checks.reduce((acc, _, idx) => ({...acc, [idx]: false}), {}));
    setShowCheatSheet(false);
  }, [task.id]);

  const manualChecksDone = Object.values(checks).length > 0 && Object.values(checks).every(Boolean);
  const turnsDone = currentTurnCount >= MIN_TURNS_REQUIRED;
  
  // [关键修复] 只有当状态为 'input' (空闲) 时才允许结束
  // 这意味着：既不在生成中 (loading)，也不在等待评分 (survey)
  const isIdle = turnStatus === 'input';
  
  const canFinish = manualChecksDone && turnsDone && isIdle;

  let buttonText = "任务锁定中";
  if (turnStatus === 'loading') buttonText = "⏳ AI 生成中...";
  else if (turnStatus === 'survey') buttonText = "📝 请先完成右侧评分";
  else if (!turnsDone) buttonText = `再聊 ${Math.max(0, MIN_TURNS_REQUIRED - currentTurnCount)} 轮以解锁`;
  else if (!manualChecksDone) buttonText = "请勾选上方所有目标";
  else if (canFinish) buttonText = "完成此任务";

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 h-screen p-6 flex flex-col overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-800 flex items-center"><FileText className="w-5 h-5 mr-2 text-blue-600" />任务进度</h2>
        <div className="w-full bg-gray-200 h-2 rounded-full mt-2"><div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${((currentTaskIndex) / tasks.length) * 100}%` }} /></div>
        <p className="text-xs text-right text-gray-500 mt-1">Step {currentTaskIndex + 1} / {tasks.length}</p>
        <div className="text-xs text-gray-400 font-mono mt-1">User: {sessionId}</div>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6 flex-1">
        <h3 className="font-bold text-gray-800 mb-1">{task.title}</h3>
        {/* [Fix] 增加 whitespace-pre-wrap 以正确显示换行符 */}
        <p className="text-sm text-gray-600 mb-4 border-b pb-3 whitespace-pre-wrap leading-relaxed">
          {task.desc}
        </p>
        <div className="space-y-3 mb-6">
          {task.checks?.map((text, idx) => (
            <label key={idx} className="flex items-start space-x-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
              <input type="checkbox" className="mt-1" checked={!!checks[idx]} onChange={e => setChecks({...checks, [idx]: e.target.checked})} />
              <span className="text-sm text-gray-700">{text}</span>
            </label>
          ))}
        </div>
        <div className={`p-3 rounded-lg border flex items-center space-x-3 transition-colors ${turnsDone ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
          {turnsDone ? <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" /> : <Lock className="w-4 h-4 text-red-500 flex-shrink-0" />}
          <div className="text-sm">
            <span className={turnsDone ? 'text-green-800 font-medium' : 'text-red-800 font-medium'}>至少交互 {MIN_TURNS_REQUIRED} 轮</span>
            <div className="text-xs text-gray-500 mt-1">当前: <b>{currentTurnCount}</b> / {MIN_TURNS_REQUIRED}</div>
          </div>
        </div>
      </div>

      <div className="mb-6 border border-amber-200 bg-amber-50 rounded-lg">
        <button onClick={() => setShowCheatSheet(!showCheatSheet)} className="w-full flex justify-between p-3 text-amber-800 text-sm font-medium"><span>💡 查看提示</span>{showCheatSheet ? <ChevronDown className="w-4 h-4"/> : <ChevronRight className="w-4 h-4"/>}</button>
        {showCheatSheet && <div className="p-3 text-xs text-amber-900 bg-amber-50/50 space-y-2">{task.hints?.map((hint, idx) => <p key={idx} className="pl-2 border-l-2 border-amber-300">{hint}</p>)}</div>}
      </div>

      <button 
        onClick={onTaskComplete} 
        disabled={!canFinish} 
        className={`w-full py-3 rounded-lg font-semibold flex justify-center items-center space-x-2 transition-all 
          ${canFinish ? 'bg-green-600 text-white hover:bg-green-700 shadow-md' : 'bg-gray-200 text-gray-400 cursor-not-allowed'} 
          ${!isIdle && turnsDone ? 'border-2 border-blue-200 bg-blue-50 text-blue-400' : ''}` // 加了一个特殊样式给 loading/survey 状态
        }
      >
        {canFinish ? <CheckCircle className="w-5 h-5" /> : ((!isIdle && turnsDone) ? <AlertTriangle className="w-4 h-4 animate-pulse"/> : <Lock className="w-4 h-4" />)}
        <span>{buttonText}</span>
      </button>
    </div>
  );
};
// ==========================================
// 4. Survey Components
// ==========================================
// [修改] TaskSummary 组件：更新为 4 个 Dialog-level 核心指标
const TaskSummary = ({ onNext, taskTitle }) => {
  const [satisfaction, setSatisfaction] = useState(3);
  const [reuse, setReuse] = useState(3);
  const [adaptability, setAdaptability] = useState(3);
  const [ease, setEase] = useState(3);

  // 复用 Likert 渲染逻辑
  const renderLikert = (title, description, value, setter, labels) => (
    <div className="mb-6">
      <div className="mb-2">
        <div className="flex justify-between items-center">
          <label className="text-sm font-bold text-gray-800">{title}</label>
          <span className="text-sm font-mono text-blue-600 font-bold bg-blue-50 px-2 rounded">{value}</span>
        </div>
        <p className="text-xs text-gray-500 mt-1 leading-relaxed">{description}</p>
      </div>

      <div className="flex justify-between items-center bg-white p-2 rounded border border-gray-200 mb-1 shadow-sm">
        {[1, 2, 3, 4, 5].map((s) => (
          <label key={s} className="flex flex-col items-center cursor-pointer flex-1 hover:bg-gray-50 rounded p-1 transition-colors group">
            <input 
              type="radio" 
              name={title} 
              value={s} 
              checked={value === s} 
              onChange={() => setter(s)}
              className="accent-blue-600 w-4 h-4 mb-1 cursor-pointer"
            />
            <span className={`text-[10px] ${value === s ? 'text-blue-600 font-bold' : 'text-gray-400 group-hover:text-gray-600'}`}>{s}</span>
          </label>
        ))}
      </div>
      <div className="flex justify-between text-[10px] text-gray-400 px-1 font-medium">
        <span>{labels[0]}</span>
        <span>{labels[1]}</span>
      </div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 p-6 animate-in fade-in zoom-in duration-300 overflow-y-auto">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-lg w-full border border-gray-100 my-auto">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-sm">
            <BarChart2 className="w-6 h-6"/>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">任务结算</h2>
          <p className="text-gray-500 text-sm mt-1">请评价整个对话过程 ({taskTitle})</p>
        </div>

        <div className="space-y-2">
          {/* 1. Global Satisfaction */}
          {renderLikert(
            "1. 总评 (Global Satisfaction)",
            "综合考虑回复质量和交互体验，你对最终的任务结果满意吗？",
            satisfaction,
            setSatisfaction,
            ["不满意", "非常满意"]
          )}

          {/* 2. Reuse */}
          {renderLikert(
            "2. 复用意愿 (Reuse)",
            "如果未来有类似的任务，你愿意再次使用这个 AI 助手吗？",
            reuse,
            setReuse,
            ["绝对不会", "强烈愿意"]
          )}

          {/* 3. Adaptability */}
          {renderLikert(
            "3. 适应性 (Adaptability)",
            "在对话过程中，你感觉 AI 越来越懂你的意图了吗？(是否从你的反馈中学习了)",
            adaptability,
            setAdaptability,
            ["完全没变/变笨", "进化明显"]
          )}

          {/* 4. Ease of Use */}
          {renderLikert(
            "4. 易用性 (Ease of Use)",
            "为了达成最终目标，你觉得引导这个 AI 费劲吗？",
            ease,
            setEase,
            ["非常费劲", "非常轻松"]
          )}
        </div>

        <button 
          onClick={() => onNext({ satisfaction, reuse, adaptability, ease })} 
          className="w-full mt-6 bg-gray-900 text-white py-4 rounded-xl font-bold hover:bg-gray-800 transition-all flex justify-center items-center gap-2 shadow-lg hover:scale-[1.02]"
        >
          提交并进入下一关 <ArrowRight size={18}/>
        </button>
      </div>
    </div>
  );
};
const TurnSurvey = ({ onSubmit }) => {
  const [specificity, setSpecificity] = useState(3);
  const [satisfaction, setSatisfaction] = useState(3);
  const [correction, setCorrection] = useState(3);

  // 辅助函数：增加 description 参数
  const renderLikert = (title, description, value, setter, labels) => (
    <div className="mb-6">
      <div className="mb-2">
        <div className="flex justify-between items-center">
          <label className="text-sm font-bold text-gray-800">{title}</label>
          <span className="text-sm font-mono text-blue-600 font-bold bg-blue-50 px-2 rounded">{value}</span>
        </div>
        {/* 新增：指标说明文字 */}
        <p className="text-xs text-gray-500 mt-1 leading-relaxed">{description}</p>
      </div>

      <div className="flex justify-between items-center bg-white p-2 rounded border border-gray-200 mb-1 shadow-sm">
        {[1, 2, 3, 4, 5].map((s) => (
          <label key={s} className="flex flex-col items-center cursor-pointer flex-1 hover:bg-gray-50 rounded p-1 transition-colors group">
            <input 
              type="radio" 
              name={title} 
              value={s} 
              checked={value === s} 
              onChange={() => setter(s)}
              className="accent-blue-600 w-4 h-4 mb-1 cursor-pointer"
            />
            <span className={`text-[10px] ${value === s ? 'text-blue-600 font-bold' : 'text-gray-400 group-hover:text-gray-600'}`}>{s}</span>
          </label>
        ))}
      </div>
      <div className="flex justify-between text-[10px] text-gray-400 px-1 font-medium">
        <span>{labels[0]}</span>
        <span>{labels[1]}</span>
      </div>
    </div>
  );

  return (
    <div className="bg-blue-50 p-5 rounded-xl border border-blue-200 shadow-sm animate-in slide-in-from-bottom-2 mx-4 mb-6">
      <h3 className="text-sm font-bold text-blue-900 mb-4 flex items-center gap-2">
        <AlertTriangle size={16}/> 请评价上一轮回复 (必填)
      </h3>
      
      {/* 1. Specificity */}
      {renderLikert(
        "1. 针对性 (Specificity)", 
        "AI 的回复是专门针对你的具体指令，还是模糊的通用套话？", 
        specificity, 
        setSpecificity, 
        ["通用/套话", "非常具体"]
      )}
      
      {/* 2. Satisfaction */}
      {renderLikert(
        "2. 满意度 (Satisfaction)", 
        "这一轮的回复质量如何？是否满足了你的当前需求？", 
        satisfaction, 
        setSatisfaction, 
        ["不满意", "非常满意"]
      )}
      
      {/* 3. Correction Efficacy */}
      {renderLikert(
        "3. 修正效果 (Correction Efficacy)", 
        "如果你刚才指出了错误，AI 是否成功修正了它？(若未指出错误请选 3)", 
        correction, 
        setCorrection, 
        ["完全没修/变差", "完美修正"]
      )}

      <button 
        onClick={() => onSubmit({ specificity, satisfaction, correction })} 
        className="w-full mt-2 bg-blue-600 text-white text-xs py-3 rounded-lg font-bold hover:bg-blue-700 shadow-md transition-all active:scale-[0.98] flex justify-center items-center gap-2"
      >
        <CheckCircle size={14} />
        提交评价并继续
      </button>
    </div>
  )
};
const FinalScreen = ({ onFinish }) => (<div className="flex-1 flex flex-col justify-center items-center bg-white p-8 text-center"><CheckCircle className="w-24 h-24 text-green-500 mb-6"/><h1 className="text-3xl font-bold text-gray-900 mb-2">实验结束</h1><button onClick={onFinish} className="bg-gray-900 text-white px-8 py-4 rounded-full text-lg font-bold shadow-xl mt-8">⬇️ 下载数据</button></div>);

// ==========================================
// 5. 主程序
// ==========================================
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [modelSequence, setModelSequence] = useState([]); 

  const [tasks, setTasks] = useState(DEFAULT_TASKS);
  const [taskIndex, setTaskIndex] = useState(0);
  const [appState, setAppState] = useState("chat"); 
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [turnStatus, setTurnStatus] = useState("input");
  const [allData, setAllData] = useState([]);
  const [currentTurnData, setCurrentTurnData] = useState([]);
  
  const chatEndRef = useRef(null);
  const userTurnCount = messages.filter(m => m.role === 'user').length;

  const handleLoginSuccess = (fullId, idNum) => {
    setSessionId(fullId);
    
    // [盲测] 取模24
    const permIndex = idNum % 24; 
    const sequenceIndices = PERMUTATIONS[permIndex];
    const sequence = sequenceIndices.map(idx => MODEL_LIST[idx]);
    
    console.log(`[Blind Test] User ${fullId} (Pattern #${permIndex}) initialized.`); 
    
    setModelSequence(sequence);
    setIsLoggedIn(true);

    fetch('/tasks').then(res=>res.ok?res.json():null).then(d=>{if(d)setTasks(d)}).catch(e=>{});
  };

  const handleSend = async () => {
    console.log("In handleSend")
    if (!input.trim()) return;
    
    const newHistory = [...messages, { role: "user", content: input }];
    setMessages(newHistory);
    setInput("");
    setTurnStatus("loading");

    const currentModel = modelSequence[taskIndex];
    console.log("In handleSend")
    const response = await fetchBackendResponse(currentModel, newHistory, tasks[taskIndex]?.id,sessionId);
    setMessages([...newHistory, { role: "assistant", content: response }]);
    setTurnStatus("survey");
  };

  const handleTurnSubmit = (data) => {
    setCurrentTurnData([...currentTurnData, { turn: messages.length / 2, ...data, timestamp: new Date().toISOString() }]);
    setTurnStatus("input");
  };

  const handleSummarySubmit = (scores) => {
    const taskRecord = {
      taskId: tasks[taskIndex].id,
      taskTitle: tasks[taskIndex].title,
      assignedModel: modelSequence[taskIndex], // 记录真实模型
      history: messages,
      turnMetrics: currentTurnData,
      summaryScores: scores
    };
    const newData = [...allData, taskRecord];
    setAllData(newData);

    if (taskIndex + 1 < tasks.length) {
      setTaskIndex(taskIndex + 1);
      setMessages([]);
      setCurrentTurnData([]);
      setTurnStatus("input");
      setAppState("chat");
    } else {
      setAppState("finished");
    }
  };

  const handleDownload = () => {
    const groupID = parseInt(sessionId.split('-')[1]) % 24;
    const exportData = { 
        sessionId, 
        group: groupID, 
        sequence: modelSequence, 
        tasks: allData 
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${sessionId}_Result.json`;
    a.click();
  };

  if (!isLoggedIn) return <LoginScreen onLogin={handleLoginSuccess} />;
  if (appState === "finished") return <FinalScreen onFinish={handleDownload} />;

  return (
    <div className="flex h-screen bg-white font-sans text-gray-900">
      {/* [关键] 将 turnStatus 传入 Sidebar */}
      <TaskSidebar 
        currentTaskIndex={taskIndex} 
        tasks={tasks} 
        onTaskComplete={() => setAppState("task_summary")} 
        sessionId={sessionId} 
        currentTurnCount={userTurnCount} 
        turnStatus={turnStatus}
      />
      <div className="flex-1 flex flex-col h-screen relative">
        <header className="h-14 border-b px-6 flex items-center justify-between bg-white z-10 shadow-sm">
            <h1 className="font-bold text-gray-800">IEvoAgent Study</h1>
            <div className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-400 font-mono flex items-center gap-2">
                <EyeOff size={12}/> Blind Mode: Active
            </div>
        </header>

        {appState === "task_summary" ? (
          <TaskSummary taskTitle={tasks[taskIndex].title} onNext={handleSummarySubmit} />
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50" ref={chatEndRef}>
               {messages.length === 0 && (
                   <div className="text-center mt-20 opacity-40 select-none">
                       <div className="text-4xl mb-2">💬</div>
                       <p>Start {tasks[taskIndex].title}</p>
                   </div>
               )}
               {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role==='user'?'justify-end':'justify-start'}`}>
                  <div className={`max-w-[80%] px-5 py-3 rounded-2xl shadow-sm whitespace-pre-wrap leading-relaxed ${msg.role==='user'?'bg-gray-900 text-white rounded-br-none':'bg-white border rounded-bl-none text-gray-800'}`}>
                    {msg.content}
                  </div>
                </div>
               ))}
               {turnStatus === 'loading' && (
                  <div className="flex items-center gap-2 text-blue-600 ml-4 mt-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="font-medium text-sm animate-pulse">AI Thinking...</span>
                  </div>
                )}
               {turnStatus === 'survey' && <TurnSurvey onSubmit={handleTurnSubmit} />}
               <div className="h-4"></div>
            </div>
            <div className="p-4 bg-white border-t relative">
                 <input value={input} onChange={e=>setInput(e.target.value)} disabled={turnStatus!=='input'} onKeyPress={e=>e.key==='Enter'&&turnStatus==='input'&&handleSend()} className="w-full pl-5 pr-14 py-4 bg-gray-100 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500 transition-all disabled:opacity-50" placeholder={turnStatus==='survey'?"⚠️ 请先完成评分...":"输入指令..."}/>
                 <button onClick={handleSend} disabled={turnStatus!=='input'||!input.trim()} className="absolute right-6 top-6 p-2 bg-gray-900 text-white rounded-xl hover:bg-gray-700 disabled:bg-gray-300"><Send size={20}/></button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;