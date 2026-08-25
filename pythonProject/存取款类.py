class Account(object):
    """账号类，amount 是美元金额."""

    def __init__(self, rate):  #__init__初始化self，rate值
        self.__amt = 0    # 私有属性，前面加下划线表示"内部使用"
        self.rate = rate  # # 使用属性设置器进行初始化，后续可以调用并修改，属性主要是作用于该实例生命周期内

    @property    #Getter方法（@property装饰器）将下面方法属性化，实际是方法计算
    def amount(self):
        """账号余额（美元）- 只读"""
        return self.__amt

    @property    #Getter方法（@property装饰器）
    def rate(self):
        """汇率"""
        return self.__rate

    @rate.setter  #Setter方法（@属性名.setter装饰器）setter方法主要是用作于数据验证/转换/保护只读等
    def rate(self, value):
        if value <= 0:
            raise ValueError("汇率必须为正数")
        self.__rate = value

    @property
    def cny(self):
        """账号余额（人民币）- 只读"""
        return self.__amt * self.__rate

    def deposit(self, value):
        """存款"""
        if value <= 0:
            raise ValueError("存款金额必须为正数")
        self.__amt += value  #余额=余额+新的存款
        return self.__amt

    def withdraw(self, value):
        """取款"""
        if value <= 0:
            raise ValueError("取款金额必须为正数")
        if value > self.__amt:
            raise ValueError("余额不足")
        self.__amt -= value  #余额=余额-提现金额
        return self.__amt


if __name__ == '__main__':  #只有直接运行此文件时才会执行下面的代码，如果此文件被其他文件导入，不会执行这部分代码

    try:   #try。。。。except 异常捕获块
        acc = Account(rate=6.6)  #创建一个rate=6.6的account账户
        acc.deposit(100)         #存款100
        print(f"存款后余额: ${acc.amount}")
        print(f"人民币金额: ¥{acc.cny:.2f}")

        acc.withdraw(30)    #提现30
        print(f"取款后余额: ${acc.amount}")

        # 尝试负数存款（会抛出异常）
        acc.deposit(-50)
    except ValueError as e:
        print(f"操作错误: {e}")