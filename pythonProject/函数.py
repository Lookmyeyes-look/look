# 我们使用关键字 def 来定义一个函数，语法描述如下所示：
def testsum(a, b):
    return a+b
res = testsum(1234,5678)
print(res)
# 局域变量
print('局域变量' + '-' * 15)
def change():
    a = 90
    print(a)
a = 9
print("Before the function call ", a)
print("inside change function", end=' ')
change()
print("After the function call ", a)
# 全局变量
print('全局变量' + '-' * 15 )
a = 9
def change():
    global a
    print(a)
    a = 100
print("Before the function call ", a)
print("inside change function", end=' ')
change()
print("After the function call ", a)

# 可以预置默认参数，只要第一个带默认参数后其他的参数也只能为带默认参数
print('默认参数' + '-' * 15 )
def func(a,c,b=3):
    c += 1
    print("a =", a)
    print("c =", c)
    print("b =", b)
    print("---")
# 关键字前后调用keyword = value，先按照顺序赋值，如果有关键字出现，就顺推
func(1,2)
print("---")
func(12,c=1)

#  内置高阶函数举例
# mac()将函数应用于可迭代对象的每个元素  map(lambda x: x*2, [1,2,3])得到 [2,4,6]
# filter()过滤掉不符合条件的元素   filter(lambda x: x>0, [-1,0,1])得到 [1]
# reduce()用某种规则将序列元素依次累积计算为一个值   reduce(lambda x,y: x+y, [1,2,3])得到 6
# sorted()根据 key参数指定的函数进行排序   sorted(['cat','a'], key=len)得到 ['a','cat']
# (Lambda x:x*2,1)这里的lambda为一个匿名函数经常和其他高阶函数一起使用，为简单表达式，这里输入x为1，x=x*2即输出x为1*2=2
# 自定义高阶函数--函数作为返回值（闭包）
def make_multiplier(factor):
    """生成一个乘以特定因子的函数"""
    def multiplier(x):
        return x * factor
    return multiplier

double = make_multiplier(2)  # 创建一个乘以2的函数
triple = make_multiplier(3)  # 创建一个乘以3的函数

print(double(5))   # 输出 10
print(triple(5))
# 自定义高阶函数--实际应用：装饰器
print("装饰器"+"-" * 10)
def simple_decorator(func):           # 1. 装饰器函数
    def wrapper():                   # 2. 内部包装函数
        print("函数执行前做一些事")
        func()                       # 3. 执行原始函数
        print("函数执行后做一些事")
    return wrapper                   # 4. 返回包装函数

@simple_decorator                     # 5. 应用装饰器
def say_hello():                     # 6. 原始函数
    print("Hello!")

say_hello()                          # 7. 调用装饰后的函数
# 手动应用装饰器
# decorated_say_hello = simple_decorator(say_hello)
# 调用装饰后的函数
# decorated_say_hello()
print("装饰器带参"+"-" * 10)
def repeat(n):
    """重复执行n次的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):  #*args(可变位置参数)元组  **kwargs(可变关键字参数)字典
            for i in range(n):
                print(f"第{i+1}次执行：")
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"你好，{name}!")
    return f"已问候{name}"

greet("张三")