import math

try:
    a = int(input("Enter value of a: "))
    b = int(input("Enter value of b: "))
    c = int(input("Enter value of c: "))

    if a == 0:
        print("错误：a不能为0，这不是一元二次方程")
    else:
        d = b * b - 4 * a * c

        if d < 0:
            print("ROOTS are imaginary (负数根)")
            real_part = -b / (2 * a)
            # match.sqrt是数学函数非负数平方根
            imag_part = math.sqrt(-d) / (2 * a)
            print(f"Root 1 = {real_part} + {imag_part}i")
            print(f"Root 2 = {real_part} - {imag_part}i")
        elif d == 0:
            root = -b / (2 * a)
            print(f"方程有重根: {root}")
        else:
            print("ROOTS are imaginary (正数根)")
            root1 = (-b + math.sqrt(d)) / (2 * a)
            root2 = (-b - math.sqrt(d)) / (2 * a)
            print("Root 1 =", root1)
            print("Root 2 =", root2)

except ValueError:
    print("错误：请输入有效的数字")
except Exception as e:
    print(f"发生错误: {e}")