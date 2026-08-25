file_path = '/Users/tu/Desktop/lean/log.txt'
# with open(file_path, 'r', encoding='utf-8') as infile:
#     content = infile.read()   # 这里是直接阅读全部文件
#     print(content)
# 这里推荐每一行读取并加上文件异常情况报错
print('-' * 10)
try:
    with open(file_path, 'w', encoding='utf-8') as outfile:
        outfile.write('test123\n')
        outfile.write('two123\n')
        outfile.close()
    with open(file_path, 'r', encoding='utf-8') as outfile:
        for line in outfile:
            print(line, end='')
        outfile.close()
except FileNotFoundError:
    print(f"找不到该文件")
except FileExistsError:
    print(f"文件有异常无法打开")