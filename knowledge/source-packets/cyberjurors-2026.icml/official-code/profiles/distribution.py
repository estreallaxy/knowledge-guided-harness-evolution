import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm

def age_distribution(mean, sigma, lower, upper, sample_size):
    # # 定义参数
    # mu = 30  # 均值
    # sigma = 20  
    # lower, upper = 18, np.inf  # 截断范围
    # 计算截断正态分布的标准化边界
    a, b = (lower - mean) / sigma, (upper - mean) / sigma
    # 生成截断正态分布随机数
    # sample_size = 100000
    truncated_samples = truncnorm.rvs(a, b, loc=mean, scale=sigma, size=sample_size).tolist() # truncnorm.rvs返回的是数组array，要转换为列表
    truncated_samples = [round(x) for x in truncated_samples] # 把列表中的每个值四舍五入
    return truncated_samples, a, b

def init_atti_distribution(mean, sigma, lower, upper, sample_size):
    # 计算截断正态分布的标准化边界
    a, b = (lower - mean) / sigma, (upper - mean) / sigma
    # 生成截断正态分布随机数, truncnorm.rvs返回的是数组array，要转换为列表
    truncated_samples = truncnorm.rvs(a, b, loc=mean, scale=sigma, size=sample_size).tolist() 
    truncated_samples = [round(i,7) for i in truncated_samples]
    return truncated_samples, a, b

def conformity_distribution(mean, sigma, lower, upper, sample_size):
    # 计算截断正态分布的标准化边界
    a, b = (lower - mean) / sigma, (upper - mean) / sigma
    # 生成截断正态分布随机数, truncnorm.rvs返回的是数组array，要转换为列表
    truncated_samples = truncnorm.rvs(a, b, loc=mean, scale=sigma, size=sample_size).tolist() 
    truncated_samples = [round(i,2) for i in truncated_samples]
    return truncated_samples

def draw_distribution(samples1, mean1, sigma1, a1, b1, samples2, mean2, sigma2, a2, b2):
    # 绘制统计图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14,6))
    # plt.figure(figsize=(10, 6))

    ax1.hist(samples1, bins=50, density=True, alpha=0.6, color='g')
    # 添加正态分布的概率密度函数曲线
    xmin, xmax = ax1.get_xlim()
    x1 = np.linspace(xmin, xmax, 100)
    p1 = truncnorm.pdf(x1, a1, b1, loc=mean1, scale=sigma1)
    ax1.plot(x1, p1, 'k', linewidth=2)
    ax1.set_title(f'Truncated Normal Distribution (Mean = {mean1})')
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Density')
    ax1.grid()

    ax2.hist(samples2, bins=50, density=True, alpha=0.6, color='g')
    # 添加正态分布的概率密度函数曲线
    xmin, xmax = ax2.get_xlim()
    x2 = np.linspace(xmin, xmax, 100)
    p2 = truncnorm.pdf(x2, a2, b2, loc=mean2, scale=sigma2)
    ax2.plot(x2, p2, 'k', linewidth=2)
    ax2.set_title(f'Compressed Normal Distribution (Mean = {mean2})')
    ax2.set_xlabel('Value')
    ax2.set_ylabel('Density')
    ax2.grid()

    plt.show()

# age, a1, b1 = age_distribution(mean=30, sigma=20, lower=18, upper=np.inf, sample_size=50)
# init_atti, a2, b2 = init_atti_distribution(mean=0,sigma=0.3,lower=-1,upper=1,sample_size=50)
# draw_distribution(age, 30, 20, a1, b1, init_atti, 0, 0.3, a2, b2)

# print(f"年龄：{age}")
# print(f"初始态度：{init_atti}")

