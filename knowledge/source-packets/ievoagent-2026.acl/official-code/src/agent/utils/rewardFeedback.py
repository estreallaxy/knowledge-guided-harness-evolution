def feedback_reward(feedback_type: str, error_code: str) -> float:
    """
    根据用户反馈类型和错误代码查表计算 Reward。
    
    Args:
        text (str): 用户反馈的文本内容 (本函数仅作记录或预处理，不参与直接查表)。
        feedback_type (str): 用户反馈标签 (a), 例如 "POS", "NEG_1", "NEU"。
        error_code (str): 错误具体代码 (b), 例如 "E1", "E8", "NE"。
        
    Returns:
        float: 对应的 Reward 分值。
    """
    
    # 1. 定义错误代码到表格列的映射关系
    error_category_map = {
        "NE": "NO_ERROR",

        # 轻微错误 (E8, E7, E6)
        "E8": "MINOR", "E7": "MINOR", "E6": "MINOR",

        # 中度错误 (E4, E3, E1, E2)
        "E4": "MODERATE", "E3": "MODERATE", "E1": "MODERATE","E2": "MODERATE","E11": "MODERATE",

        # 严重错误 (E5, E9, E10)
        "E5": "SEVERE", "E9": "SEVERE", "E10": "SEVERE"
    }

    # 2. 定义 Reward 表格数据 (行: Feedback, 列: Error Category)
    reward_matrix = {
        "POS":   {"NO_ERROR": 1.0, "MINOR": 0.5, "MODERATE": 0.2, "SEVERE": -0.2},
        "NEU":   {"NO_ERROR": 0.5, "MINOR": 0.2, "MODERATE": -0.1, "SEVERE": -0.3},
        "STOP":   {"NO_ERROR": 0.2, "MINOR": 0.1, "MODERATE": -0.2, "SEVERE": -0.4},
        "NEG_5": {"NO_ERROR": 0.0, "MINOR": -0.1, "MODERATE": -0.3, "SEVERE": -0.4},
        "NEG_1": {"NO_ERROR": -0.1, "MINOR": -0.3, "MODERATE": -0.5, "SEVERE": -0.6},
        "NEG_4": {"NO_ERROR": -0.1, "MINOR": -0.4, "MODERATE": -0.6, "SEVERE": -0.7},
        "NEG_3": {"NO_ERROR": -0.1, "MINOR": -0.6, "MODERATE": -0.8, "SEVERE": -0.8},
        "NEG_2": {"NO_ERROR": -0.2, "MINOR": -0.7, "MODERATE": -0.9, "SEVERE": -0.9},
    }

    f_key = str(feedback_type).upper().strip()
    e_key = str(error_code).upper().strip()
    category = error_category_map.get(e_key)
    
    if category is None:
        if e_key in ["MINOR", "MODERATE", "SEVERE", "NO_ERROR"]:
            category = e_key
        else:
            print(f"警告: 未知的错误代码 '{error_code}'")
            return 0.0 # 或者根据需求抛出异常

    # B. 查表获取分数 (Lookup)
    if f_key in reward_matrix:
        score = reward_matrix[f_key].get(category, 0.0)
        return score
    else:
        print(f"警告: 未知的反馈类型 '{feedback_type}'")
        return 0.0