import random

data= [['s+', 90002], ['s+', 90001], ['b', 101058], ['null', 99082], ['s', 90003], ['s', 90004], ['a', 90005]]

# 1. 定义等级权重的映射字典
rank_weights = {'s+': 5, 's': 4, 'a': 3, 'b':2, 'c':1, 'null': 0}

# 2. 使用 sorted() 函数进行多级排序
# key 参数是一个 lambda 函数，它为每个元素生成一个用于排序的元组
sorted_data = sorted(data, key=lambda x: (-rank_weights[x[0]],random.random()))

# 打印结果
print("排序后的列表:")
for item in sorted_data:
    print(item)