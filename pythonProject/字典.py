data = {'kushal':'Fedora', 'kart_':'Debian', 'Jace':'Mac'}
# 新增一个键值对
data['test'] = 'test'
print(data)
# 删除del
del data['test']
print(data)
if 'test' not    in data:
    data['test'] = 'test'
    print(data)
# 遍历一个字典使用item()方法
for key,value in data.items():
    print(f"{key} in {value}")
# 新增时判断是否存在dict.setdefault(key, default)
data.setdefault('test1','test1')
print(data)
# 枚举索引和值enumerate
for key,value in enumerate(data):
    print(f"{key} in {value}")


# 学生成绩判断
n = int(input("Enter the number of students: "))
data = {} # 用来存储数据的字典变量
Subjects = ('Physics', 'Maths', 'History') # 所有科目
for i in range(0, n):
    name = input('Enter the name of the student {}: '.format(i + 1)) # 获得学生名称
    marks = [] # 成绩变量循环
    for x in Subjects:
        marks.append(int(input('Enter marks of {}: '.format(x)))) # 获得每一科的分数
    data[name] = marks
    print(data)
for x, y in data.items():
    total =  sum(y)
    print("{}'s total marks {}".format(x, total))
    if total < 120:
        print(x, "failed :(")
    else:
        print(x, "passed :)")
