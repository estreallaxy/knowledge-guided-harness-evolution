import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd
import json
random.seed(42)

def create_graph(num_nodes=1000, num_edges=6, min_follow_num=0.1, max_follow_num=0.25):
    if(min_follow_num<1):
        min_follow_num = min_follow_num * num_nodes
    if(max_follow_num<1):
        max_follow_num = max_follow_num * num_nodes

    # 生成无标度网络 
    
    G = nx.barabasi_albert_graph(num_nodes, num_edges)

    # 计算所有节点的平均距离（需要图是连通的）
    if nx.is_connected(G):
        avg_distance = nx.average_shortest_path_length(G)
    else:
        avg_distance = float('inf')  # 如果图不连通，则设为无穷大

    # 计算所有节点的平均邻居数量
    avg_neighbors = sum(dict(G.degree()).values()) / G.number_of_nodes()

    # print("平均距离:", avg_distance)
    # print("平均邻居数量:", avg_neighbors)

    # 获取所有节点的度
    degrees = [degree for _, degree in G.degree()]

    # 计算度分布
    degree_counts = np.bincount(degrees)
    degree_values = np.arange(len(degree_counts))

    # 过滤掉频率为0的度值
    nonzero_degrees = degree_values[degree_counts > 0]
    nonzero_counts = degree_counts[degree_counts > 0]

    # 绘制度分布曲线图（非对数坐标）
    plt.figure(figsize=(10, 6))
    plt.plot(nonzero_degrees, nonzero_counts, linestyle="-", color="tab:blue")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    plt.title("Degree Distribution Curve of Barabási-Albert Scale-Free Network")
    plt.grid(True, linestyle="--", lw=0.5)
    # plt.savefig(f"{FILE_PREFIX}degree_distribution_{num_nodes}.png", dpi=500)  # 可以调整 dpi 来控制图像分辨率

    G_directed = G.to_directed() # 将无向图转换为有向图
    follow = {node: [] for node in G_directed.nodes()}  
    following = {node: [] for node in G_directed.nodes()}
    
    for node in G_directed.nodes(): # 意见领袖和普通用户的粉丝关系、关注关系
        follow[node] = [n for n in G_directed.predecessors(node)]  # 每个节点的前驱节点，就是它的粉丝
        following[node] = [n for n in G_directed.successors(node)]  # 每个节点的后继节点，就是它关注的人

    weights = [len(follow[node]) for node in follow]

    for key in following:
        sample_num = random.choice(range(min_follow_num, max_follow_num + 1))
        
        if(sample_num >= len(following[key])):
            continue
        else:
            index_ls = range(len(following[key]))
            p = [weights[i] for i in following[key]]
            sample_index = np.random.choice(index_ls, p = np.array(p) / sum(p), size = sample_num, replace = False)
            following[key] = [following[key][i] for i in sample_index]

    network = nx.DiGraph()
    network.add_nodes_from([a for a in following])
    network.add_edges_from([(a, b) for a in following for b in following[a]])

    return network

# def save_json(network, scale):

#     follower = {node: list(network.predecessors(node)) for node in network.nodes()}

#     following = {node: list(network.successors(node)) for node in network.nodes()}

#     # 
#     with open(f"{FILE_PREFIX}agents_{scale}/follower_{scale}.json", "w") as file:
#         json.dump(follower, file, indent=4)  # indent 参数可以使输出更具可读性
#     # 
#     with open(f"{FILE_PREFIX}agents_{scale}/following_{scale}.json", "w") as file:
#         json.dump(following, file, indent=4)  # indent 参数可以使输出更具可读性

def save_following_network(save_path):
    network = create_graph(num_nodes=17, num_edges=3, min_follow_num=1, max_follow_num=3)
    following = {node: list(network.successors(node)) for node in network.nodes()}
    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(following, file, indent=4)

if __name__ == "__main__":
    save_path = 'result/17_test_12_20/following.json'
    save_following_network(save_path)
