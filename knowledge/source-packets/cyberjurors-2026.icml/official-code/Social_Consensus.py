"""
社会共识检索模块（RAG）

功能：
- 提供 `retrieve_consensus_for_case(case_data: dict, k: int = 3)`
- 首次运行时对 `Social_Consensus.json` 中的条目进行标准化并构建索引
- 如果环境中存在 scikit-learn，会使用 TF-IDF + 余弦相似度并把 vectorizer 与矩阵持久化到缓存目录
- 否则使用标准库 difflib 作为回退相似度方法

实现要求：不使用 try/except，使用 importlib.util.find_spec 检查依赖
"""

import json
import pickle
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
from difflib import SequenceMatcher

_VECTORIZER = None
_MATRIX = None
_REFLECTIONS = None
_CASE_IDS = None
_TEXTS = None

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "Social_Consensus.json"
CACHE_DIR = BASE_DIR / ".consensus_cache"
VECTORIZER_FILE = CACHE_DIR / "vectorizer.pkl"
MATRIX_SPARSE_FILE = CACHE_DIR / "matrix.npz"
MATRIX_DENSE_FILE = CACHE_DIR / "matrix.npy"
TEXTS_FILE = CACHE_DIR / "texts.json"
REFLECTIONS_FILE = CACHE_DIR / "reflections.json"
CASEIDS_FILE = CACHE_DIR / "case_ids.json"


def _ensure_cache_dir():
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_entry(entry: Dict) -> Dict:
    """把 Social_Consensus.json 中的原始 entry 转成标准化字段字典

    返回包含 keys: title, buyer_claim, seller_claim, buyer_descriptions(list), seller_descriptions(list), reflection_result, case_id
    """
    cd = entry.get('case_data', {}) if isinstance(entry, dict) else {}
    title = cd.get('title', '')
    buyer_claim = cd.get('buyer_claim', '')
    seller_claim = cd.get('seller_claim', '')

    buyer_descriptions = []
    seller_descriptions = []

    if isinstance(cd.get('case_details', {}), dict):
        evidences = cd.get('case_details', {}).get('evidences', [])
    else:
        evidences = []

    for ev in evidences or []:
        identity = ev.get('identity', '')
        content = ev.get('content', {}) or {}
        text = content.get('text', '')
        if identity == '买家' and text:
            buyer_descriptions.append(text)
        elif identity == '卖家' and text:
            seller_descriptions.append(text)

    debate = entry.get('debate_process', {}) or {}
    transcript = debate.get('transcript', []) if isinstance(debate.get('transcript', []), list) else []
    for turn in transcript or []:
        speaker = turn.get('speaker', '')
        text = turn.get('text', '') or ''
        if speaker.startswith('Buyer') and text:
            buyer_descriptions.append(text)
        elif speaker.startswith('Seller') and text:
            seller_descriptions.append(text)

    reflection_result = (entry.get('reflection', {}) or {}).get('reflection_result') or entry.get('reflection_result') or ''

    cid = cd.get('id') or cd.get('case_id') or (entry.get('metadata') or {}).get('case_id')
    cid = str(cid) if cid is not None else ''

    return {
        'title': title or '',
        'buyer_claim': buyer_claim or '',
        'seller_claim': seller_claim or '',
        'buyer_descriptions': buyer_descriptions,
        'seller_descriptions': seller_descriptions,
        'reflection_result': reflection_result,
        'case_id': cid
    }


def _prepare_index(db_path: Optional[Path] = None):
    """准备索引：如果缓存存在则从缓存加载，否则构建索引并持久化。"""
    global _VECTORIZER, _MATRIX, _REFLECTIONS, _CASE_IDS, _TEXTS
    _ensure_cache_dir()

    sklearn_spec = importlib.util.find_spec("sklearn.feature_extraction.text")
    scipy_sparse_spec = importlib.util.find_spec("scipy.sparse")
    numpy_spec = importlib.util.find_spec("numpy")

    # 优先从缓存加载
    if VECTORIZER_FILE.exists() and (MATRIX_SPARSE_FILE.exists() or MATRIX_DENSE_FILE.exists()) and TEXTS_FILE.exists() and REFLECTIONS_FILE.exists() and CASEIDS_FILE.exists():
        try:
            _VECTORIZER = pickle.loads(VECTORIZER_FILE.read_bytes())
            
            if MATRIX_SPARSE_FILE.exists() and scipy_sparse_spec:
                scipy_sparse = importlib.import_module("scipy.sparse")
                _MATRIX = scipy_sparse.load_npz(str(MATRIX_SPARSE_FILE))
            elif MATRIX_DENSE_FILE.exists() and numpy_spec:
                numpy = importlib.import_module("numpy")
                _MATRIX = numpy.load(str(MATRIX_DENSE_FILE), allow_pickle=False)
            
            _TEXTS = json.loads(TEXTS_FILE.read_text(encoding='utf-8'))
            _REFLECTIONS = json.loads(REFLECTIONS_FILE.read_text(encoding='utf-8'))
            _CASE_IDS = json.loads(CASEIDS_FILE.read_text(encoding='utf-8'))
            
            if not sklearn_spec:
                _VECTORIZER = None
                _MATRIX = None

            return
        except (pickle.PickleError, EOFError, FileNotFoundError):
            # 缓存文件损坏或不完整，将继续执行以重建缓存
            pass

    # 如果缓存不存在或加载失败，则从原始数据构建
    db_path = db_path or DB_PATH
    if not db_path.exists():
        # 如果连原始数据文件都没有，就无法继续
        return

    data = json.loads(db_path.read_text(encoding='utf-8'))

    texts = []
    reflections = []
    case_ids = []

    for entry in data:
        norm = _normalize_entry(entry)
        parts = []
        for fld in ('title', 'buyer_claim', 'seller_claim'):
            v = norm.get(fld)
            if v:
                parts.append(str(v))
        for fld in ('buyer_descriptions', 'seller_descriptions'):
            v = norm.get(fld)
            if isinstance(v, list):
                parts.extend([str(x) for x in v if x])

        text = "\n".join(parts).strip()
        if not text:
            text = norm.get('reflection_result', '') or ''

        texts.append(text)
        reflections.append(norm.get('reflection_result', '') or '')
        case_ids.append(norm.get('case_id', '') or '')

    _TEXTS = texts
    _REFLECTIONS = reflections
    _CASE_IDS = case_ids

    TEXTS_FILE.write_text(json.dumps(_TEXTS, ensure_ascii=False, indent=2), encoding='utf-8')
    REFLECTIONS_FILE.write_text(json.dumps(_REFLECTIONS, ensure_ascii=False, indent=2), encoding='utf-8')
    CASEIDS_FILE.write_text(json.dumps(_CASE_IDS, ensure_ascii=False, indent=2), encoding='utf-8')

    if sklearn_spec:
        tf_module = importlib.import_module("sklearn.feature_extraction.text")
        TfidfVectorizer = getattr(tf_module, "TfidfVectorizer")
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        _MATRIX = vectorizer.fit_transform(texts)
        _VECTORIZER = vectorizer

        VECTORIZER_FILE.write_bytes(pickle.dumps(_VECTORIZER))

        if scipy_sparse_spec:
            scipy_sparse = importlib.import_module("scipy.sparse")
            scipy_sparse.save_npz(str(MATRIX_SPARSE_FILE), _MATRIX)
        elif numpy_spec:
            numpy = importlib.import_module("numpy")
            numpy.save(str(MATRIX_DENSE_FILE), _MATRIX.toarray())
    else:
        _VECTORIZER = None
        _MATRIX = None


def _make_query_text(case_data: Dict) -> str:
    parts = []
    if not case_data:
        return ''
    for fld in ('title', 'buyer_claim', 'seller_claim'):
        v = case_data.get(fld)
        if v:
            parts.append(str(v))
    for fld in ('buyer_descriptions', 'seller_descriptions'):
        v = case_data.get(fld)
        if isinstance(v, list):
            parts.extend([str(x) for x in v if x])
    return '\n'.join(parts)


def retrieve_consensus_for_case(case_data: Dict, k: int = 3, db_path: Optional[Path] = None) -> List[Dict]:
    """返回 top-k 社会共识条目：list[{'case_id','score','reflection_result'}]"""
    global _VECTORIZER, _MATRIX, _REFLECTIONS, _CASE_IDS, _TEXTS
    if _REFLECTIONS is None or _TEXTS is None:
        _prepare_index(db_path)

    query = _make_query_text(case_data)
    if not query:
        return []

    results: List[Dict] = []

    if _VECTORIZER is not None and _MATRIX is not None:
        pair_spec = importlib.util.find_spec("sklearn.metrics.pairwise")
        if pair_spec is not None:
            qv = _VECTORIZER.transform([query])
            pair_mod = importlib.import_module("sklearn.metrics.pairwise")
            cosine_similarity = getattr(pair_mod, "cosine_similarity")
            sims = cosine_similarity(qv, _MATRIX)[0]
            ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:k]
            for idx, score in ranked:
                results.append({
                    'case_id': _CASE_IDS[idx],
                    'score': float(score),
                    'reflection_result': _REFLECTIONS[idx]
                })
            return results

    # 回退到 difflib 的相似度计算
    scores = []
    for t in _TEXTS:
        scores.append(SequenceMatcher(None, query, t or '').ratio())
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
    for idx, score in ranked:
        results.append({
            'case_id': _CASE_IDS[idx],
            'score': float(score),
            'reflection_result': _REFLECTIONS[idx]
        })
    return results


if __name__ == '__main__':
    print("Running self-test for Social_Consensus.py...")

    # 确保缓存目录是干净的，以测试缓存创建
    if CACHE_DIR.exists():
        import shutil
        print(f"Removing existing cache directory: {CACHE_DIR}")
        shutil.rmtree(CACHE_DIR)

    sample_case = {
        'title': '商品与描述不符',
        'buyer_claim': '收到的商品与描述严重不符，申请退货退款。',
        'seller_claim': '商品为正品，轻微差异不影响使用，不同意退款。',
        'buyer_descriptions': ['图片上是蓝色的，发过来是黑色的。', '尺寸也小了一号。'],
        'seller_descriptions': ['仓库发货批次不同，颜色有轻微差异属于正常现象。']
    }

    print("\n--- First run (should build and save cache) ---")
    results1 = retrieve_consensus_for_case(sample_case, k=3)
    print("Top 3 retrieved consensus:")
    for res in results1:
        print(f"  - Case ID: {res.get('case_id')}, Score: {res.get('score'):.4f}, Reflection: {res.get('reflection_result', 'N/A')[:80]}...")
    
    if CACHE_DIR.exists() and any(CACHE_DIR.iterdir()):
        print("\n✅ Cache directory and files created successfully.")
    else:
        print("\n❌ Error: Cache was not created on the first run.")

    print("\n--- Second run (should load from cache) ---")
    # 在第二次运行时，不清除缓存，以测试加载逻辑
    results2 = retrieve_consensus_for_case(sample_case, k=3)
    print("Top 3 retrieved consensus (from cache):")
    for res in results2:
        print(f"  - Case ID: {res.get('case_id')}, Score: {res.get('score'):.4f}, Reflection: {res.get('reflection_result', 'N/A')[:80]}...")

    # 简单验证两次结果是否一致
    if len(results1) == len(results2) and all(r1['case_id'] == r2['case_id'] for r1, r2 in zip(results1, results2)):
        print("\n✅ Verification successful: Results from both runs are consistent.")
    else:
        print("\n❌ Verification failed: Results from the two runs are different.")
        print("Results 1:", [r['case_id'] for r in results1])
        print("Results 2:", [r['case_id'] for r in results2])

    print("\nSelf-test finished.")
"""
社会共识检索模块（RAG）

提供接口：`retrieve_consensus_for_case(case_data: dict, k: int = 3)`
返回与输入 case_data 相似度最高的 k 条社会共识（包含 case_id、score、reflection_result）

实现细节：优先使用 sklearn 的 TF-IDF + 余弦相似度；若不可用则回退到 difflib 相似度。
该模块会在首次调用时为整个 Social_Consensus.json 建立索引并缓存以便复用。
"""

import json
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional
from difflib import SequenceMatcher

_VECTORIZER = None
_MATRIX = None
_REFLECTIONS = None
_CASE_IDS = None
_TEXTS = None

DB_PATH = Path(__file__).parent / "Social_Consensus.json"


def _prepare_index(db_path: Optional[Path] = None):
    global _VECTORIZER, _MATRIX, _REFLECTIONS, _CASE_IDS, _TEXTS
    db_path = db_path or DB_PATH
    data = json.loads(db_path.read_text(encoding='utf-8'))

    texts = []
    reflections = []
    case_ids = []

    def _normalize_entry(entry: Dict) -> Dict:
        """把 Social_Consensus.json 中的原始 entry 转成标准化字段字典

        返回包含 keys: title, buyer_claim, seller_claim, buyer_descriptions(list), seller_descriptions(list), reflection_result, case_id
        """
        cd = entry.get('case_data', {}) if isinstance(entry, dict) else {}
        title = cd.get('title', '')
        buyer_claim = cd.get('buyer_claim', '')
        seller_claim = cd.get('seller_claim', '')

        # 收集描述文本：有时存放在 case_details -> evidences[*].content.text 或 transcript
        buyer_descriptions = []
        seller_descriptions = []

        evidences = cd.get('case_details', {}).get('evidences', []) if isinstance(cd.get('case_details', {}), dict) else []
        for ev in evidences:
            identity = ev.get('identity', '')
            content = ev.get('content', {}) or {}
            text = content.get('text', '')
            if identity == '买家' and text:
                buyer_descriptions.append(text)
            elif identity == '卖家' and text:
                seller_descriptions.append(text)

        # reflection_result 可能在 entry['reflection']['reflection_result'] 或 entry['reflection_result']
        reflection_result = (entry.get('reflection', {}) or {}).get('reflection_result') or entry.get('reflection_result') or ''

        cid = cd.get('id') or cd.get('case_id') or (entry.get('metadata') or {}).get('case_id')
        cid = str(cid) if cid is not None else ''

        return {
            'title': title or '',
            'buyer_claim': buyer_claim or '',
            'seller_claim': seller_claim or '',
            'buyer_descriptions': buyer_descriptions,
            'seller_descriptions': seller_descriptions,
            'reflection_result': reflection_result,
            'case_id': cid
        }

    for entry in data:
        norm = _normalize_entry(entry)
        parts = []
        for fld in ('title', 'buyer_claim', 'seller_claim'):
            v = norm.get(fld)
            if v:
                parts.append(str(v))
        for fld in ('buyer_descriptions', 'seller_descriptions'):
            v = norm.get(fld)
            if isinstance(v, list):
                parts.extend([str(x) for x in v if x])

        text = "\n".join(parts).strip()
        if not text:
            text = norm.get('reflection_result', '') or ''

        texts.append(text)
        reflections.append(norm.get('reflection_result', '') or '')
        case_ids.append(norm.get('case_id', '') or '')

    _TEXTS = texts
    _REFLECTIONS = reflections
    _CASE_IDS = case_ids

    # 使用 importlib 检查 sklearn 可用性，避免 try/except
    spec = importlib.util.find_spec("sklearn.feature_extraction.text")
    if spec is not None:
        tf_module = importlib.import_module("sklearn.feature_extraction.text")
        TfidfVectorizer = getattr(tf_module, "TfidfVectorizer")
        vectorizer = TfidfVectorizer(max_features=5000)
        X = vectorizer.fit_transform(texts)
        _VECTORIZER = vectorizer
        _MATRIX = X
    else:
        _VECTORIZER = None
        _MATRIX = None


def _make_query_text(case_data: Dict) -> str:
    parts = []
    if not case_data:
        return ''
    for fld in ('title', 'buyer_claim', 'seller_claim'):
        v = case_data.get(fld)
        if v:
            parts.append(str(v))
    for fld in ('buyer_descriptions', 'seller_descriptions'):
        v = case_data.get(fld)
        if isinstance(v, list):
            parts.extend([str(x) for x in v if x])
    return '\n'.join(parts)


def preload_consensus_index(db_path: Optional[Path] = None):
    """预加载社会共识索引（在主进程中调用，避免多线程竞争）
    
    使用场景：在启动多线程任务前调用此函数，确保索引已经加载完毕
    """
    global _REFLECTIONS, _TEXTS
    if _REFLECTIONS is None or _TEXTS is None:
        print("🔨 预加载社会共识索引...")
        _prepare_index(db_path)
        print(f"✅ 社会共识索引加载完成（{len(_TEXTS) if _TEXTS else 0} 个案例）")


def retrieve_consensus_for_case(case_data: Dict, k: int = 3, db_path: Optional[Path] = None) -> List[Dict]:
    """返回 top-k 社会共识条目：list[{'case_id','score','reflection_result'}]
    
    注意：建议在多线程环境下先调用 preload_consensus_index() 预加载索引
    """
    global _VECTORIZER, _MATRIX, _REFLECTIONS, _CASE_IDS, _TEXTS
    _ensure_cache_dir()
    if _REFLECTIONS is None or _TEXTS is None:
        _prepare_index(db_path)

    query = _make_query_text(case_data)
    if not query:
        return []

    results: List[Dict] = []

    if _VECTORIZER is not None and _MATRIX is not None:
        # 使用 sklearn 的余弦相似度计算
        pair_spec = importlib.util.find_spec("sklearn.metrics.pairwise")
        if pair_spec is not None:
            qv = _VECTORIZER.transform([query])
            pair_mod = importlib.import_module("sklearn.metrics.pairwise")
            cosine_similarity = getattr(pair_mod, "cosine_similarity")
            sims = cosine_similarity(qv, _MATRIX)[0]
            ranked = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:k]
            for idx, score in ranked:
                results.append({
                    'case_id': _CASE_IDS[idx],
                    'score': float(score),
                    'reflection_result': _REFLECTIONS[idx]
                })
            return results

    # 回退到 difflib 的相似度计算（SequenceMatcher），该模块为标准库，直接使用
    scores = []
    for t in _TEXTS:
        scores.append(SequenceMatcher(None, query, t or '').ratio())
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:k]
    for idx, score in ranked:
        results.append({
            'case_id': _CASE_IDS[idx],
            'score': float(score),
            'reflection_result': _REFLECTIONS[idx]
        })
    return results


if __name__ == '__main__':
    # quick self-test (requires Social_Consensus.json next to this file)
    sample = {'title': '商品与描述不符', 'buyer_claim': '收到商品与描述不符', 'seller_claim': ''}
    print(retrieve_consensus_for_case(sample, k=3))
