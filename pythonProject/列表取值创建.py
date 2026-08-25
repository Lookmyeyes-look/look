#
# squares=[]
# for x in range(1,11):
#     squares = x ** 2
#     if x % 2 == 0:
#         squares += x
#     print("squares: ", squares)
squares = [x ** 2 for x in range(10)]
print(squares)
# 长度
print(len(squares))
# 类型
print(type(squares))
# 为了取带有1的值，先创建一个空数组，然后走转str判断
result = []
for x in squares:
      if '1' in str(x):
          result.append(x)
print(result)
# startsitch先转str然后排序首位为1的值
resultant = [s for s in result if str(s).startswith('1')]
print(resultant)

