# N = 100
# a = 2
# while a < N:
#     print(str(a))
#     a *= a


# 使用更具描述性的变量名
harmonic_sum = 0.0

print("项数  部分和")
print("-" * 15)
# range范围
for i in range(1, 11):
    harmonic_sum += 1.0 / i
    print(f"{i:2d} {harmonic_sum:8.4f}")