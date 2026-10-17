import numpy as np
from scipy.spatial.distance import jensenshannon
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
def normalize_matrix(data_dict, llm_types, feedback_types):
    """
    将原始频数字典转换为归一化的 NumPy 矩阵 (Probabilities)
    """
    matrix = []
    for l_type in llm_types:
        row = []
        counts = data_dict.get(l_type, {})
        # 获取该行总数用于归一化
        total = sum(counts.values())
        for f_type in feedback_types:
            # 如果总数为0，设为均匀分布或全0（取决于数据情况）
            val = counts.get(f_type, 0)
            row.append(val / total if total > 0 else 0)
        matrix.append(row)
    return np.array(matrix)

def calculate_matrix_jsd(matrix_a, matrix_b):
    """
    计算两个矩阵对应行之间的平均 Jensen-Shannon Divergence
    JSD 越接近 0 表示分布越相似，越接近 1 表示差异越大
    """
    js_distances = []
    for i in range(matrix_a.shape[0]):
        p = matrix_a[i]
        q = matrix_b[i]
        
        # scipy.spatial.distance.jensenshannon 返回的是 JSD 的平方根 (JS distance)
        # 我们通常取其平方得到标准的 JS Divergence
        dist = jensenshannon(p, q)
        js_distances.append(dist**2)
    
    return np.mean(js_distances)

# --- 数据准备 ---
# 假设你有两个字典：data_lmsys 和 data_wildchat
# 这里以你提供的单份数据为例演示流程
llm_types = sorted(["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "NE"])
feedback_types = sorted(["NEG_1", "NEG_2", "NEG_3", "NEG_4", "NEG_5", "NEU", "POS", "STOP"])

# 1. 归一化矩阵
matrix_lmsys = normalize_matrix(data_lmsys, llm_types, feedback_types)
matrix_wildchat = normalize_matrix(data_wildchat, llm_types, feedback_types)

# 2. 计算相似度
avg_jsd = calculate_matrix_jsd(matrix_lmsys, matrix_wildchat)
print(f"Average Jensen-Shannon Divergence: {avg_jsd:.4f}")