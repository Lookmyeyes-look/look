import sys
def hours(minutes):
    if minutes < 0:
        raise ValueError("输入参数不能为负值")
    else:
        print("{} H, {} M, {} S".format(int(minutes / 60), int(minutes % 60), int(minutes % 2 * 60 )))
# 函数调用及异常处理逻辑
try:
    # 从命令行参数获取分钟数并转换为整数
    minutes = int(sys.argv[1])
    # 调用 hours 函数
    hours(minutes)
except (ValueError, IndexError) as e:
    # 处理异常情况：
    # 1. 参数不是有效数字 (ValueError)
    # 2. 没有提供参数 (IndexError)
    # 3. 参数是负数 (hours函数抛出的ValueError)
    print("Parameter Error")

hours(80.65)