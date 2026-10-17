

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# --- 数据定义 ---
data_wildchat = {
    "E1":{
        "NEG_1":613,
        "NEG_2":175,
        "NEG_3":24,
        "NEG_4":68,
        "NEG_5":432,
        "NEU":39,
        "POS":2,
        "STOP":254
    },
    "E10":{
        "NEG_1":18,
        "NEG_2":44,
        "NEG_3":14,
        "NEG_4":8,
        "NEG_5":46,
        "NEU":20,
        "POS":1,
        "STOP":10
    },
    "E11":{
        "NEG_1":14,
        "NEG_2":35,
        "NEG_3":8,
        "NEG_4":2,
        "NEG_5":26,
        "NEU":9,
        "POS":0,
        "STOP":545
    },
    "E2":{
        "NEG_1":867,
        "NEG_2":432,
        "NEG_3":70,
        "NEG_4":114,
        "NEG_5":817,
        "NEU":235,
        "POS":16,
        "STOP":337
    },
    "E3":{
        "NEG_1":2136,
        "NEG_2":1270,
        "NEG_3":237,
        "NEG_4":316,
        "NEG_5":742,
        "NEU":150,
        "POS":19,
        "STOP":314
    },
    "E4":{
        "NEG_1":59,
        "NEG_2":148,
        "NEG_3":3,
        "NEG_4":7,
        "NEG_5":258,
        "NEU":170,
        "POS":0,
        "STOP":46
    },
    "E5":{
        "NEG_1":718,
        "NEG_2":1675,
        "NEG_3":476,
        "NEG_4":416,
        "NEG_5":2690,
        "NEU":1547,
        "POS":42,
        "STOP":614
    },
    "E6":{
        "NEG_1":11,
        "NEG_2":10,
        "NEG_3":3,
        "NEG_4":2,
        "NEG_5":56,
        "NEU":8,
        "POS":0,
        "STOP":7
    },
    "E7":{
        "NEG_1":647,
        "NEG_2":612,
        "NEG_3":155,
        "NEG_4":131,
        "NEG_5":952,
        "NEU":374,
        "POS":21,
        "STOP":373
    },
    "E8":{
        "NEG_1":224,
        "NEG_2":80,
        "NEG_3":28,
        "NEG_4":483,
        "NEG_5":101,
        "NEU":40,
        "POS":2,
        "STOP":92
    },
    "E9":{
        "NEG_1":1,
        "NEG_2":4,
        "NEG_3":4,
        "NEG_4":0,
        "NEG_5":1,
        "NEU":0,
        "POS":0,
        "STOP":1
    },
    "NE":{
        "NEG_1":3520,
        "NEG_2":672,
        "NEG_3":412,
        "NEG_4":2241,
        "NEG_5":4441,
        "NEU":53452,
        "POS":1507,
        "STOP":5362
    }
}

data_lmsys = {
    "E1":{
        "NEG_1":2531,
        "NEG_2":444,
        "NEG_3":371,
        "NEG_4":314,
        "NEG_5":2359,
        "NEU":221,
        "POS":25,
        "STOP":1457
    },
    "E10":{
        "NEG_1":88,
        "NEG_2":132,
        "NEG_3":59,
        "NEG_4":67,
        "NEG_5":195,
        "NEU":167,
        "POS":16,
        "STOP":58
    },
    "E11":{
        "NEG_1":811,
        "NEG_2":207,
        "NEG_3":253,
        "NEG_4":360,
        "NEG_5":1815,
        "NEU":443,
        "POS":45,
        "STOP":828
    },
    "E2":{
        "NEG_1":2332,
        "NEG_2":998,
        "NEG_3":411,
        "NEG_4":313,
        "NEG_5":2644,
        "NEU":693,
        "POS":79,
        "STOP":931
    },
    "E3":{
        "NEG_1":1565,
        "NEG_2":1141,
        "NEG_3":271,
        "NEG_4":343,
        "NEG_5":1304,
        "NEU":512,
        "POS":48,
        "STOP":249
    },
    "E4":{
        "NEG_1":154,
        "NEG_2":325,
        "NEG_3":22,
        "NEG_4":22,
        "NEG_5":292,
        "NEU":199,
        "POS":21,
        "STOP":67
    },
    "E5":{
        "NEG_1":1442,
        "NEG_2":2304,
        "NEG_3":725,
        "NEG_4":1000,
        "NEG_5":5462,
        "NEU":3595,
        "POS":233,
        "STOP":1139
    },
    "E6":{
        "NEG_1":67,
        "NEG_2":67,
        "NEG_3":39,
        "NEG_4":44,
        "NEG_5":242,
        "NEU":91,
        "POS":14,
        "STOP":67
    },
    "E7":{
        "NEG_1":2500,
        "NEG_2":2227,
        "NEG_3":1038,
        "NEG_4":771,
        "NEG_5":4803,
        "NEU":1936,
        "POS":233,
        "STOP":1605
    },
    "E8":{
        "NEG_1":217,
        "NEG_2":81,
        "NEG_3":32,
        "NEG_4":665,
        "NEG_5":222,
        "NEU":161,
        "POS":5,
        "STOP":36
    },
    "E9":{
        "NEG_1":7,
        "NEG_2":26,
        "NEG_3":28,
        "NEG_4":17,
        "NEG_5":68,
        "NEU":177,
        "POS":32,
        "STOP":36
    },
    "NE":{
        "NEG_1":2615,
        "NEG_2":529,
        "NEG_3":483,
        "NEG_4":1239,
        "NEG_5":4367,
        "NEU":41757,
        "POS":3027,
        "STOP":3060
    }
}

def get_merged_df(data_d1, data_d2):
    # 定义行列顺序
    all_types = ["NE", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11"]
    feedback_types = ["NEG_1", "NEG_2", "NEG_3", "NEG_4", "NEG_5", "NEU", "POS", "STOP"]

    # 转为 DataFrame
    df1 = pd.DataFrame.from_dict(data_d1, orient='index')
    df2 = pd.DataFrame.from_dict(data_d2, orient='index')

    # 对齐数据（确保行列一致，缺的补0）
    df1 = df1.reindex(index=all_types, columns=feedback_types).fillna(0)
    df2 = df2.reindex(index=all_types, columns=feedback_types).fillna(0)

    # 【关键步骤】相加原始数值
    df_total = df1.add(df2)

    # 【关键步骤】行归一化（计算概率）
    df_norm = df_total.div(df_total.sum(axis=1), axis=0)
    
    return df_norm

df_merged = get_merged_df(data_lmsys, data_wildchat)

# --- 3. 绘图 ---
def plot_single_heatmap(df, save_path="merged_single_heatmap.pdf"):
    plt.rcParams["font.family"] = "serif"
    
    # 设置画布大小 (因为只有一张图，不需要那么宽了)
    fig, ax = plt.subplots(figsize=(8, 7))

    # 绘图
    sns.heatmap(df, 
                annot=True, 
                fmt=".2f", 
                vmin=0, vmax=1, 
                cmap="GnBu", 
                cbar_kws={'label': 'Probability'},
                annot_kws={"size": 9}, # 字号可以稍微大一点
                ax=ax)

    # 标题
    ax.set_title("Merged Dataset Distribution (LMSYS + WildChat)", fontsize=12, pad=15)

    # 轴标签优化
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(axis='both', which='both', length=0) # 去掉刻度线
    
    # 调整标签字体和旋转
    ax.set_xticklabels(df.columns, rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(df.index, rotation=0, fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()

plot_single_heatmap(df_merged)