# import json
# from collections import Counter, defaultdict
# from pathlib import Path

# import pandas as pd

# # 可选：如果要做统计检验和可视化，建议安装：
# # pip install scipy seaborn matplotlib
# from scipy.stats import chi2_contingency
# import seaborn as sns
# import matplotlib.pyplot as plt


# def load_pairs_from_jsonl(path):
#     """
#     从 jsonl 文件中提取 (llm_response_type, user_feedback_category) 成对数据。

#     假设每行是一个 dict，里面有：
#         - "llm_response_type": list[str]
#         - "user_feedback_category": list[str]
#     并且它们按索引对应同一轮对话。
#     """
#     path = Path(path)
#     assert path.exists(), f"File not found: {path}"

#     pairs = []

#     with path.open("r", encoding="utf-8") as f:
#         for line_no, line in enumerate(f, start=1):
#             line = line.strip()
#             if not line:
#                 continue
#             try:
#                 obj = json.loads(line)
#             except json.JSONDecodeError:
#                 print(f"[WARN] JSON decode error at line {line_no}, skipping.")
#                 continue

#             llm_types = obj.get("llm_response_type")
#             user_cats = obj.get("user_feedback_category")

#             # 简单健壮性判断
#             if not isinstance(llm_types, list) or not isinstance(user_cats, list):
#                 print(f"[WARN] line {line_no}: missing list fields, skipping.")
#                 continue

#             if len(llm_types) != len(user_cats):
#                 print(
#                     f"[WARN] line {line_no}: length mismatch "
#                     f"(llm={len(llm_types)}, user={len(user_cats)}), "
#                     f"using min length."
#                 )

#             n = min(len(llm_types), len(user_cats))
#             for i in range(n):
#                 lt = llm_types[i]
#                 uf = user_cats[i]
#                 # 你可以在这里做过滤，比如去掉 None 或特殊标记
#                 if lt is None or uf is None:
#                     continue
#                 pairs.append((lt, uf))

#     return pairs


# def build_contingency_table(pairs):
#     """
#     从 (llm_response_type, user_feedback_category) 对构建交叉表。
#     返回：
#         - pandas.DataFrame 形式的 contingency table
#     """
#     # 统计 (llm_type, user_cat) 的频次
#     counter = Counter(pairs)

#     # 拿到所有唯一标签
#     llm_types = sorted({lt for lt, _ in counter.keys()})
#     user_cats = sorted({uf for _, uf in counter.keys()})

#     # 构建一个嵌套 dict 然后转 DataFrame
#     table_dict = defaultdict(dict)
#     for lt in llm_types:
#         for uf in user_cats:
#             table_dict[lt][uf] = counter.get((lt, uf), 0)

#     df = pd.DataFrame(table_dict).T  # 行：llm_type，列：user_cat
#     df.index.name = "llm_response_type"
#     df.columns.name = "user_feedback_category"
#     return df


# def chi_square_and_cramers_v(contingency_df):
#     """
#     对交叉表做卡方检验并计算 Cramér’s V。
#     """
#     chi2, p, dof, expected = chi2_contingency(contingency_df.values)

#     # Cramér's V = sqrt(chi2 / (n * (min(r-1, c-1))))
#     n = contingency_df.values.sum()
#     r, c = contingency_df.shape
#     denom = n * (min(r - 1, c - 1))
#     if denom == 0:
#         cramers_v = float("nan")
#     else:
#         cramers_v = (chi2 / denom) ** 0.5

#     return {
#         "chi2": chi2,
#         "p_value": p,
#         "dof": dof,
#         "cramers_v": cramers_v,
#         "n": n,
#     }


# def plot_heatmap(contingency_df, save_path=None):
#     """
#     画交叉表的热力图。
#     """
#     plt.figure(figsize=(8, 6))
#     sns.heatmap(
#         contingency_df,
#         annot=True,
#         fmt="d",
#         linewidths=0.5,
#         cbar=True,
#     )
#     plt.title("LLM Response Type vs User Feedback Category")
#     plt.tight_layout()
#     if save_path:
#         plt.savefig(save_path, dpi=300)
#         print(f"Heatmap saved to: {save_path}")
#     else:
#         plt.show()


# def main():
#     # TODO: 把这里改成你的实际路径
#     jsonl_path = "./dataset_construction/filtered/WildChat-1M-geq8_final/WildChat-1M-geq8_part_0.jsonl"

#     print("Loading pairs from jsonl...")
#     pairs = load_pairs_from_jsonl(jsonl_path)
#     print(f"Total (llm_response_type, user_feedback_category) pairs: {len(pairs)}")

#     print("\nBuilding contingency table...")
#     contingency_df = build_contingency_table(pairs)
#     print("\n=== Contingency Table ===")
#     print(contingency_df)

#     print("\nRunning chi-square test and computing Cramér's V...")
#     stats = chi_square_and_cramers_v(contingency_df)
#     print("\n=== Statistics ===")
#     for k, v in stats.items():
#         print(f"{k}: {v}")

#     # 可选：如果你想看可视化
#     try:
#         plot_heatmap(contingency_df, save_path="llm_vs_feedback_heatmap.png")
#     except Exception as e:
#         print(f"[WARN] Failed to plot heatmap: {e}")


# if __name__ == "__main__":
#     main()


import json
from pathlib import Path
from collections import Counter, defaultdict

import pandas as pd
from scipy.stats import chi2_contingency
import seaborn as sns
import matplotlib.pyplot as plt
llm_type_list = ["NE","E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11"]
user_feedback_list = ["NEU","NEG_1","NEG_2","NEG_3","NEG_4","NEG_5","POS","STOP"]
def load_pairs_from_directory(dir_path, recursive=True):
    """
    从目录中加载所有 jsonl 文件（支持递归），提取 (llm_response_type, user_feedback_category) 对。

    会自动跳过 / 规整掉类型异常（例如 list、dict）的字段，避免 Counter 报错。
    """
    dir_path = Path(dir_path)
    assert dir_path.exists(), f"Directory not found: {dir_path}"

    print(f"Scanning directory: {dir_path}")

    if recursive:
        files = list(dir_path.rglob("*.jsonl"))
    else:
        files = list(dir_path.glob("*.jsonl"))

    print(f"Found {len(files)} jsonl files")

    pairs = []

    for file in files:
        print(f"Loading {file} ...")
        with file.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    print(f"[WARN] JSON decode error in {file}:{line_no}, skipping.")
                    continue

                llm_types = obj.get("llm_response_type")
                user_cats = obj.get("user_feedback_category")

                if not isinstance(llm_types, list) or not isinstance(user_cats, list):
                    # 不是我们预期的结构，跳过
                    continue
                n = min(len(llm_types), len(user_cats))
                for i in range(n):
                    lt = llm_types[i]
                    uf = user_cats[i]
                    if lt not in llm_type_list or uf not in user_feedback_list:
                        break
                    # lt = user_cats[i]
                    # uf = llm_types[i]
                    # if uf=="E7":
                    #     print(f"[ERROR] UF ERROR at {file}:{line_no}, skip one item.")
                    #     break
                    # 跳过 None
                    if lt is None or uf is None:
                        continue
                    # if lt != "E1" and lt != "E2" and lt != "E3" and lt != "E4":
                    #     continue
                    # 如果里面还是 list（有些数据可能是嵌套结构），做一点简单处理：
                    # 情况 1：如果是单元素 list，例如 ["NE"]，那就取第一个元素
                    if isinstance(lt, list):
                        if len(lt) == 1:
                            lt = lt[0]
                        else:
                            # 结构太复杂，直接跳过这条，避免搞脏统计
                            print(f"[WARN] lt is list with len>1 at {file}:{line_no}, skip one item.")
                            continue

                    if isinstance(uf, list):
                        if len(uf) == 1:
                            uf = uf[0]
                        else:
                            print(f"[WARN] uf is list with len>1 at {file}:{line_no}, skip one item.")
                            continue

                    # 如果此时仍然不是字符串，就直接转成字符串
                    # （比如某些场景下是数字、枚举、dict 等）
                    if not isinstance(lt, str):
                        lt = str(lt)
                    if not isinstance(uf, str):
                        uf = str(uf)

                    # 到这里 lt 和 uf 一定是可 hash 的简单类型（str）
                    pairs.append((lt, uf))

    print(f"Total extracted pairs: {len(pairs)}")
    return pairs


def build_contingency_table(pairs):
    """
    构建交叉表 DataFrame。
    """
    counter = Counter(pairs)
    llm_types = sorted({lt for lt, _ in counter.keys()})
    user_cats = sorted({uf for _, uf in counter.keys()})

    table_dict = defaultdict(dict)
    for lt in llm_types:
        for uf in user_cats:
            table_dict[lt][uf] = counter.get((lt, uf), 0)

    df = pd.DataFrame(table_dict).T
    df.index.name = "llm_response_type"
    df.columns.name = "user_feedback_category"
    return df


def chi_square_and_cramers_v(contingency_df):
    chi2, p, dof, expected = chi2_contingency(contingency_df.values)

    n = contingency_df.values.sum()
    r, c = contingency_df.shape
    denom = n * (min(r - 1, c - 1))
    cramers_v = (chi2 / denom) ** 0.5 if denom > 0 else float("nan")

    return {
        "chi2": chi2,
        "p_value": p,
        "dof": dof,
        "cramers_v": cramers_v,
        "n": n,
    }


def plot_heatmap(contingency_df, save_path=None):
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        contingency_df,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.5
    )
    plt.title("LLM Response Type vs User Feedback Category")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Heatmap saved to {save_path}")
    else:
        plt.show()
import numpy as np
from scipy.stats import chi2_contingency
import seaborn as sns
import matplotlib.pyplot as plt


def plot_association_heatmap(contingency_df, save_path=None, use_abs=True):
    """
    用标准化残差表示“相关度”的热力图：
    - 颜色越深 → 该格子偏离“独立假设”越强 → 关联越强
    - use_abs=True：画 |残差|（只看强度，不看方向）
    - use_abs=False：画带正负的残差（正值=比预期多，负值=比预期少）
    """
    # 1. 计算期望频数
    chi2, p, dof, expected = chi2_contingency(contingency_df.values)

    expected_df = pd.DataFrame(
        expected,
        index=contingency_df.index,
        columns=contingency_df.columns
    )

    # 2. 标准化残差 (O - E) / sqrt(E)
    standardized_residuals = (contingency_df - expected_df) / np.sqrt(expected_df)

    if use_abs:
        data = standardized_residuals.abs()
        title = "Association Strength (|Standardized Residuals|)\n" \
                "LLM Response Type vs User Feedback Category"
        center = None
        fmt = ".2f"
    else:
        data = standardized_residuals
        title = "Standardized Residuals\n" \
                "(Positive: more than expected, Negative: less)"
        center = 0  # 0 居中，便于看正负
        fmt = ".2f"

    # 3. 画热力图
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        data,
        annot=True,
        fmt=fmt,
        linewidths=0.5,
        center=center,  # 只有 use_abs=False 时真正起作用
    )
    plt.title(title)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Association heatmap saved to {save_path}")
    else:
        plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm  # **关键**

def plot_count_heatmap_log(contingency_df, save_path=None):
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        contingency_df,
        annot=True,
        fmt="d",
        cmap="YlGnBu",
        linewidths=0.5,
        norm=LogNorm()  # **关键：对数刻度，解决值差距巨大的问题**
    )
    plt.title("LLM Response Type vs User Feedback Category (Log Scaled Counts)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Log-scaled heatmap saved to {save_path}")
    else:
        plt.show()

import matplotlib.pyplot as plt
import seaborn as sns

def plot_row_normalized_heatmap(contingency_df, save_path=None, show_counts=False):
    """
    每一行做归一化，颜色从白色到深蓝（Blues 色系）。
    - show_counts=True 时，格子里显示原始 count；
      否则显示比例（小数）。
    """

    # 1. 按行总和归一化
    row_sums = contingency_df.sum(axis=1)
    row_props = contingency_df.div(row_sums, axis=0)

    # 2. 注释内容
    if show_counts:
        annot_data = contingency_df.values
        fmt = "d"
    else:
        annot_data = row_props.values
        fmt = ".2f"

    # 3. 画图
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        row_props,
        annot=annot_data,
        fmt=fmt,
        cmap="Blues",      # 关键：白→蓝 渐变
        linewidths=0.5,
    )
    plt.title("Row-normalized Heatmap (White → Deep Blue)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Row-normalized heatmap saved to {save_path}")
    else:
        plt.show()

def get_cdf(input_dir):
    pairs = load_pairs_from_directory(input_dir, recursive=False)

    contingency_df = build_contingency_table(pairs)
    
    return contingency_df
def draw(contingency_df):
    print("\n=== Contingency Table ===")
    print(contingency_df)

    stats = chi_square_and_cramers_v(contingency_df)
    print("\n=== Statistical Analysis ===")
    for k, v in stats.items():
        print(f"{k}: {v}")
    # 颜色表示比例，格子里显示比例
    plot_row_normalized_heatmap(contingency_df, "./src/agent/memory/row_norm_props.png", show_counts=False)

    # 颜色表示比例，格子里显示“原始 count”
    plot_row_normalized_heatmap(contingency_df, "./src/agent/memory/row_norm_counts.png", show_counts=True)

def main():
    input_dir_wildchat = "./dataset/our_dataset/WildChat_r"
    # input_dir_lmsys = "./dataset/our_dataset/lmsys_r"

    print("Processing WildChat...")
    cdf_1 = get_cdf(input_dir_wildchat)
    
    # print("Processing LMSYS...")
    # cdf_2 = get_cdf(input_dir_lmsys)
    # draw(cdf_2)
    # 使用 add 并设置 fill_value=0，防止因某个类别在其中一个数据集缺失而导致结果为 NaN
    # 最后 astype(int) 保证是整数计数
    # cdf = cdf_1.add(cdf_2, fill_value=0).astype(int)
    
    # print("\n=== Combined Contingency Table ===")
    # print(cdf)

    # --- 保存为 JSON 的部分 ---
    output_path = "./src/agent/memory/contingency_table_result_wildchat_r.json"
    cdf_1.to_json(output_path, orient="index", indent=4, force_ascii=False)
    print(f"\nCDF saved to: {output_path}")
    


    

if __name__ == "__main__":
    main()
