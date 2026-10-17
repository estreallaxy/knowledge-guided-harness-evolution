import pandas as pd
from set import First_Name, Last_Name, Status, Trait, Interest
from distribution import age_distribution, init_atti_distribution, draw_distribution, conformity_distribution
import random
import numpy as np
from tqdm import tqdm
import json
import openai
import time


data = []               # 待存储信息
agent_number = 17

# age是截断正态分布的年龄值，a1、b1是截断正态分布的标准化边界
age, a1, b1 = age_distribution(mean=30, sigma=20, lower=18, upper=np.inf, sample_size= agent_number)


same_name_id = 0

name_set = set()

for id in tqdm(range(agent_number),desc='processing agents'):
    

    first_name = random.choice(First_Name) 
    last_name = random.choice(Last_Name)
    new_name = f"{first_name} {last_name}"
    
    if new_name in name_set:
        new_name = new_name + str(same_name_id)
        same_name_id += 1
    
    name_set.add(new_name)

    new_gender = random.choice(["male","female"])
    
    s_type = random.choice( list(Status.keys()) ) # Status's随机抽取3个键
    if age[id] > 30 and s_type == "Education" :
        new_status = random.choice( [status for status in Status[s_type] if status != "Student"] )
    else:
        new_status = random.choice( Status[s_type] )


    t_class = random.sample([i for i in range(5)], 3) # Trait随机抽取3个类别的下标（共5种类别，对应5个字典）
    t_type = [random.choice(list(Trait[i].keys())) for i in t_class]# 每个类别中随机抽取正面或负面名词
    new_traits = [random.choice(Trait[value][t_type[index]]) for index, value in enumerate(t_class)] # 每个名词选取1个形容词
    new_interest = [random.choice(Interest[value][t_type[index]]) for index, value in enumerate(t_class)] # 注意，interest得和trait_type对齐
    new_traits_string = ';'.join(new_traits)
    new_interest_string = ';'.join(new_interest)

    new_role_description = f"{new_name} is a {age[id]}-year-old {new_gender} {new_status} who is {new_traits[0]}, {new_traits[1]} and {new_traits[2]}, and has interests of {new_interest[0]}, {new_interest[1]} and {new_interest[2]}."



    new_agent = {
        # 'id':id,
        'name': new_name,
        'role_description': new_role_description,
        'gender': new_gender,
        'age': age[id],
        'status': new_status,
        'traits': new_traits_string,
        'interest': new_interest_string,
    }

    data.append(new_agent)

# 将数据转换为pandas DataFrame
df = pd.DataFrame(data)
# 指定CSV文件名
filename = f'./profiles/profiles_{agent_number}.csv'
# 写入CSV文件
df.to_csv(filename, index=False)

print(f'Data has been written to {filename}')