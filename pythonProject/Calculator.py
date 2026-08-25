# 模块文档字符串
"""这是一个简单的计算器模块"""

# 模块级变量
PI = 3.14159 #大写命名表示常量，在整个模块中可用，提供配置信息和共享数据
VERSION = "1.0.0"


# 函数定义，随意定义加减乘除
def add(x, y):
    """返回两个数的和"""
    return x + y


def subtract(x, y):
    """返回两个数的差"""
    return x - y


def multiply(x, y):
    """返回两个数的积"""
    return x * y


def divide(x, y):
    """返回两个数的商"""
    if y == 0:
        return "错误：除数不能为0"
    return x / y


# 类定义
class Calculator:
    """计算器类"""

    def __init__(self, name="默认计算器"):  #初始化两个值
        self.name = name    #设置为属性
        self.history = []   #初始化一个空列表

    def power(self, x, n):  #这里是幂函数
        """计算x的n次方"""
        result = x ** n
        self.history.append(f"{x}^{n} = {result}") #将计算的结果放在self.history后面
        return result

    def show_history(self):
        """显示计算历史"""
        if not self.history:
            print("暂无计算记录")
        else:
            for i, record in enumerate(self.history, 1): #从第一个开始遍历列表
                print(f"{i}. {record}")


# 模块测试代码
if __name__ == "__main__":
    # 当直接运行此文件时执行
    print("测试计算器模块:")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"PI = {PI}")

    calc = Calculator("我的计算器")
    calc.power(5, 3)
    calc.show_history()