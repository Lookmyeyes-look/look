while True:
    password = input("请输入密码（需8位以上，包含大小写字母，且无特殊字符）：")

    # 条件1: 检查密码长度是否至少8位
    if len(password) < 8:
        print("错误：密码长度不足8位，请重新输入。")
        continue  # 跳过后续检查，直接重新输入[4](@ref)

    # 条件2: 检查是否包含至少一个大写字母
    if not any(char.isupper() for char in password):
        print("错误：密码必须包含至少一个大写字母（A-Z），请重新输入。")
        continue

    # 条件3: 检查是否包含至少一个小写字母
    if not any(char.islower() for char in password):
        print("错误：密码必须包含至少一个小写字母（a-z），请重新输入。")
        continue

    # 条件4: 检查是否包含特殊字符（只允许字母和数字）
    if not password.isalnum():  # 如果字符串包含非字母数字字符（如@、#、空格），返回False
        print("错误：密码不能包含特殊字符或空格，只允许字母和数字，请重新输入。")
        continue

    # 所有条件均满足
    print("密码合法，设置成功！")
    break  # 退出循环[7](@ref)