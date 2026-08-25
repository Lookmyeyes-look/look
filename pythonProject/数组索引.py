# 很多方法需要先导入improt random
import random
a = [ 1, 342, 223, 'India', 'Fedora']
print(a[0])
# 这里：：是跳2个取值，可以利用来取奇偶值，先从第一条开始为1
print(a[1::2])
# 尝试一下数组随机取值
b = random.choice(a)
print(b)