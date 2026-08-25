import math

def longest_side(a, b):
    """
    三个引号为string备注打印说明
    Function to find the length of the longest side of a right triangle.

    :arg a: Side a of the triangle
    :arg b: Side b of the triangle

    :return: Length of the longest side c as float
    """
    return math.sqrt(a*a + b*b)

if __name__ == '__main__':
    print(longest_side.__doc__)  #输出文档字符串
    print(longest_side(4,5))