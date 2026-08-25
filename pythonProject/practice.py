import pandas as pd
from collections import Counter
import os
import sys


def score_to_grade(score):
    """
    将分数转换为等级
    规则: 80-100为A, 70-80为B, 60-70为C, 60以下为D
    """
    if score is None or pd.isna(score): #pd.isna是 pandas 库中的一个函数，用于检测缺失值。
        return None

    try:
        # 转换为数字
        if isinstance(score, str): #isinstance是 Python 内置函数，用于判断一个对象是否是指定类或类型的实例，或者是否是该类/类型所在元组中任意一个的实例
            score = score.strip() #strip()是字符串的方法，它用于移除字符串首尾的空白字符（包括空格、换行符、制表符等）
            # 尝试转换数字字符串
            try:
                score_float = float(score)
            except ValueError:
                # 如果已经是等级，直接返回
                if score.upper() in ['A', 'B', 'C', 'D']:
                    return score.upper()
                return None
        else:
            score_float = float(score)

        # 根据分数范围返回等级
        if 80 <= score_float <= 100:
            return 'A'
        elif 70 <= score_float < 80:
            return 'B'
        elif 60 <= score_float < 70:
            return 'C'
        elif 0 <= score_float < 60:
            return 'D'
        else:
            return None  # 无效分数

    except (ValueError, TypeError):
        return None

class Person:
    """基类"""

    def __init__(self, name, grade): #self是类的方法（特别是实例方法）的第一个参数，它代表类的当前实例。通过 self，我们可以访问实例的属性和其他方法
        self.name = name #这里通过self来访问name实例属性
        self.grade = grade

    def get_grade(self):
        """基类中的get_grade方法，子类中补充"""
        raise NotImplementedError("子类必须实现 get_grade() 方法")  # 单纯触发一个报错提示

    def __str__(self): #转为字符串格式
        return f"{self.__class__.__name__}: {self.name}, 成绩: {self.grade}" #内置属性__name__，它表示类的名称，打印当前类的名称

class Student(Person):
    """学生类"""

    def __init__(self, name, grade=None):
        super().__init__(name, grade)  # super().__int__，这里等价调用Person.__init__,主要是为了继承父类的name，grade
        self.grade = grade

    def get_grade(self):
        """重新定义get_grade
        统计学生自己的成绩情况
        规则: A, B, C 为 Pass, D 为 Fail
        返回格式: "Pass: X, Fail: X"
        """
        if self.grade is None:
            return f"{self.name}: 无成绩"
        # 转换分数为等级
        grade_letter = score_to_grade(self.grade)

        if grade_letter is None:
            return f"{self.name}: {self.grade} (无效成绩)"

        if grade_letter in ['A', 'B', 'C']:
            return f"{self.name}: 原始分数({self.grade}) -> 等级({grade_letter}) (Pass: 1, Fail: 0)"
        elif grade_letter == 'D':
            return f"{self.name}: 原始分数({self.grade}) -> 等级({grade_letter}) (Pass: 0, Fail: 1)"
        else:
            return f"{self.name}: 原始分数({self.grade}) -> 等级({grade_letter}) (无效等级)"

    def get_score_and_grade(self):
        """同时返回分数和等级"""
        if self.grade is None or pd.isna(self.grade):
           return None, None

        grade_letter = score_to_grade(self.grade)
        return self.grade, grade_letter

class Teacher(Person):
    """教师类"""

    def __init__(self, name, grades=None):
        super().__init__(name, None)  # 教师的grade参数不直接使用
        self.grades = grades if grades else []

    def _convert_grades(self):
        """转换所有分数为等级"""
        converted = []
        for grade in self.grades:
            converted_grade = score_to_grade(grade)
            if converted_grade:
                converted.append(converted_grade)
        return converted

    def get_grade(self):
        """统计全班学生的成绩情况
        规则: 统计每个等级的人数
        返回格式: "A: X, B: X, C: X, D: X"
        """
        if not self.converted_grades:
            return f"{self.name}: 班级无有效成绩"

        grade_counter = Counter(self.converted_grades)

        # 构建结果
        result_parts = []
        for grade in ['A', 'B', 'C', 'D']:
            count = grade_counter.get(grade, 0)
            result_parts.append(f"{grade}: {count}")

        return f"{self.name}: 等级统计({', '.join(result_parts)})"

    def get_grade_details(self):
        """获取详细的成绩统计"""
        if not self.grades:
            return f"{self.name}: 无成绩数据"

        details = []
        for i, score in enumerate(self.grades, 1):
            grade = score_to_grade(score)
            if grade:
                details.append(f"学生{i}: 分数({score}) -> 等级({grade})")
            else:
                details.append(f"学生{i}: 分数({score}) -> 无效")

        return f"{self.name} 班级详情:\n" + "\n".join(details)

    def get_passing_rate(self):
        """计算班级通过率"""
        if not self.grades:
            return 0.0

        valid_grades = [str(g).upper() for g in self.grades if str(g).upper() in ['A', 'B', 'C', 'D']]
        if not valid_grades:
            return 0.0

        pass_count = sum(1 for g in valid_grades if g in ['A', 'B', 'C'])
        return (pass_count / len(valid_grades)) * 100


class ExcelGradeProcessor:
    """Excel 成绩处理器"""

    def __init__(self, excel_file_path):
        """
        初始化 Excel 处理器

        Args:
            excel_file_path: Excel 文件路径
        """
        self.excel_file_path = excel_file_path
        self.students = []
        self.teachers = []

    def load_excel_data(self):
        """从 Excel 文件加载数据"""
        try:
            if not os.path.exists(self.excel_file_path):
                print(f"错误: 文件不存在 - {self.excel_file_path}")
                return None

            # 读取 Excel 文件
            print(f"✅ 正在读取文件: {self.excel_file_path}")

            # 尝试读取所有工作表
            excel_data = pd.read_excel(
                self.excel_file_path,
                sheet_name=None,  # 读取所有工作表
                engine='openpyxl'
            )

            print(f"✅ 找到 {len(excel_data)} 个工作表: {list(excel_data.keys())}")
            return excel_data

        except Exception as e:
            print(f"❌ 读取 Excel 文件失败: {e}")
            return None

    def process_all_sheets(self, excel_data):
        """处理所有工作表"""
        for sheet_name, df in excel_data.items():
            print(f"\n{'=' * 50}")
            print(f"处理工作表: {sheet_name}")
            print(f"{'=' * 50}")

            # 显示工作表信息
            print(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
            print(f"列名: {list(df.columns)}")

            # 自动检测工作表类型
            if '姓名' in df.columns and '成绩' in df.columns:
                self.process_student_sheet(df, sheet_name)
            elif '教师' in df.columns:
                self.process_teacher_sheet(df, sheet_name)
            else:
                self.process_custom_format(df, sheet_name)

    def process_student_sheet(self, df, sheet_name="学生成绩"):
        """处理学生成绩表"""
        print(f"📊 检测到学生成绩表格式")

        # 创建学生对象
        student_count = 0
        for _, row in df.iterrows():
            if pd.isna(row['姓名']):
                continue

            student_name = str(row['姓名']).strip()
            student_grade = row['成绩'] if '成绩' in row and not pd.isna(row['成绩']) else None

            student = Student(student_name, student_grade)
            self.students.append(student)
            student_count += 1

        print(f"✅ 成功加载 {student_count} 名学生")

    def process_teacher_sheet(self, df, sheet_name="教师班级"):
        """处理教师班级表"""
        print(f"👨‍🏫 检测到教师班级表格式")

        # 按教师分组成绩
        teacher_grades = {}

        # 找出成绩列
        grade_columns = [col for col in df.columns if '成绩' in col or 'grade' in col.lower()]

        if not grade_columns:
            print(f"⚠️ 警告: 工作表 '{sheet_name}' 没有找到成绩列")
            return

        grade_column = grade_columns[0]  # 使用第一个成绩列

        for _, row in df.iterrows():
            if pd.isna(row['教师']):
                continue

            teacher_name = str(row['教师']).strip()

            if teacher_name not in teacher_grades:
                teacher_grades[teacher_name] = []

            if grade_column in row and pd.notna(row[grade_column]):
                teacher_grades[teacher_name].append(row[grade_column])

        # 创建教师对象
        teacher_count = 0
        for teacher_name, grades in teacher_grades.items():
            teacher = Teacher(teacher_name, grades)
            self.teachers.append(teacher)
            teacher_count += 1

        print(f"✅ 成功加载 {teacher_count} 名教师")

    def process_custom_format(self, df, sheet_name):
        """处理自定义格式的工作表"""
        print(f"🔍 检测到自定义格式工作表")
        print(f"列名: {list(df.columns)}")

        # 尝试查找包含"姓名"或"学生"的列
        name_columns = [col for col in df.columns if '姓名' in col or '学生' in col or 'name' in col.lower()]
        grade_columns = [col for col in df.columns if '成绩' in col or 'grade' in col.lower()]
        teacher_columns = [col for col in df.columns if '教师' in col or '老师' in col or 'teacher' in col.lower()]

        if name_columns and grade_columns:
            # 可能是学生成绩表
            name_col = name_columns[0]
            grade_col = grade_columns[0]

            print(f"✅ 检测到学生姓名列: '{name_col}', 成绩列: '{grade_col}'")

            student_count = 0
            for _, row in df.iterrows():
                if pd.isna(row[name_col]):
                    continue

                student_name = str(row[name_col]).strip()
                student_grade = row[grade_col] if grade_col in row and not pd.isna(row[grade_col]) else None

                student = Student(student_name, student_grade)
                self.students.append(student)
                student_count += 1

            print(f"✅ 从自定义格式加载 {student_count} 名学生")

        elif teacher_columns and grade_columns:
            # 可能是教师班级表
            teacher_col = teacher_columns[0]
            grade_col = grade_columns[0]

            print(f"✅ 检测到教师列: '{teacher_col}', 成绩列: '{grade_col}'")

            teacher_grades = {}
            for _, row in df.iterrows():
                if pd.isna(row[teacher_col]):
                    continue

                teacher_name = str(row[teacher_col]).strip()

                if teacher_name not in teacher_grades:
                    teacher_grades[teacher_name] = []

                if grade_col in row and pd.notna(row[grade_col]):
                    teacher_grades[teacher_name].append(row[grade_col])

            teacher_count = 0
            for teacher_name, grades in teacher_grades.items():
                teacher = Teacher(teacher_name, grades)
                self.teachers.append(teacher)
                teacher_count += 1

            print(f"✅ 从自定义格式加载 {teacher_count} 名教师")
        else:
            print(f"⚠️ 无法识别工作表 '{sheet_name}' 的格式")
            print("📄 前5行数据:")
            print(df.head())

    def generate_report(self, output_file=None):
        """生成报告"""
        report_lines = []

        report_lines.append("=" * 60)
        report_lines.append("📊 成绩统计报告")
        report_lines.append("=" * 60)
        report_lines.append(f"数据来源: {self.excel_file_path}")
        report_lines.append(f"生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)

        # 学生报告
        report_lines.append("\n🎓 一、学生成绩统计")
        report_lines.append("-" * 40)

        pass_count = 0
        fail_count = 0
        invalid_count = 0
        no_grade_count = 0

        for student in self.students:
            result = student.get_grade()
            report_lines.append(f"  {result}")

            if "(Pass: 1, Fail: 0)" in result:
                pass_count += 1
            elif "(Pass: 0, Fail: 1)" in result:
                fail_count += 1
            elif "无成绩" in result:
                no_grade_count += 1
            elif "无效成绩" in result:
                invalid_count += 1

        report_lines.append("\n📈 学生成绩统计:")
        report_lines.append(f"  学生总数: {len(self.students)} 人")
        report_lines.append(f"  通过人数: {pass_count} 人")
        report_lines.append(f"  不通过人数: {fail_count} 人")
        report_lines.append(f"  无成绩人数: {no_grade_count} 人")
        report_lines.append(f"  无效成绩人数: {invalid_count} 人")

        if (pass_count + fail_count) > 0:
            pass_rate = (pass_count / (pass_count + fail_count)) * 100
            report_lines.append(f"  通过率: {pass_rate:.1f}%")

        # 教师报告
        if self.teachers:
            report_lines.append("\n👨‍🏫 二、教师班级成绩统计")
            report_lines.append("-" * 40)

            for teacher in self.teachers:
                teacher_report = teacher.get_grade()
                report_lines.append(f"  {teacher_report}")

                if teacher.grades:
                    valid_grades = [str(g).upper() for g in teacher.grades if str(g).upper() in ['A', 'B', 'C', 'D']]
                    if valid_grades:
                        pass_rate = teacher.get_passing_rate()
                        report_lines.append(f"    通过率: {pass_rate:.1f}% ({len(valid_grades)} 名学生)")
                report_lines.append("")  # 空行分隔

        report_lines.append("\n" + "=" * 60)
        report_lines.append("报告生成完成")
        report_lines.append("=" * 60)

        report_text = "\n".join(report_lines)

        # 打印到控制台
        print(report_text)

        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\n✅ 报告已保存到: {output_file}")
            except Exception as e:
                print(f"❌ 保存报告失败: {e}")

        return report_text

    def print_summary(self):
        """打印简要统计"""
        print(f"\n📊 数据统计摘要:")
        print(f"  - 学生总数: {len(self.students)}")
        print(f"  - 教师总数: {len(self.teachers)}")

        if self.students:
            pass_students = sum(1 for s in self.students if s.get_grade() and "(Pass: 1, Fail: 0)" in s.get_grade())
            fail_students = sum(1 for s in self.students if s.get_grade() and "(Pass: 0, Fail: 1)" in s.get_grade())

            if (pass_students + fail_students) > 0:
                pass_rate = (pass_students / (pass_students + fail_students)) * 100
                print(f"  - 学生通过率: {pass_rate:.1f}%")


def get_excel_file_path():
    """获取Excel文件路径"""
    # 您的本地路径
    default_path = "/Users/tu/Desktop/lean/.xlsx"

    # 检查默认路径是否存在
    if os.path.exists(default_path):
        print(f"✅ 找到默认文件: {default_path}")
        return default_path

    # 如果没有找到，尝试查找lean文件夹中的Excel文件
    lean_dir = "/Users/tu/Desktop/lean"
    if os.path.exists(lean_dir):
        excel_files = [f for f in os.listdir(lean_dir) if f.endswith(('.xlsx', '.xls'))]

        if excel_files:
            print(f"\n在 {lean_dir} 中找到以下Excel文件:")
            for i, file in enumerate(excel_files, 1):
                print(f"  {i}. {file}")

            choice = input("请选择文件序号 (或直接输入路径): ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(excel_files):
                selected_file = excel_files[int(choice) - 1]
                return os.path.join(lean_dir, selected_file)
            elif os.path.exists(choice):
                return choice
            else:
                print("❌ 无效选择，将使用用户输入")

    # 用户手动输入
    while True:
        file_path = input("\n请输入Excel文件完整路径: ").strip()

        if not file_path:
            print("❌ 路径不能为空")
            continue

        # 处理相对路径
        if not os.path.isabs(file_path):
            current_dir = os.getcwd()
            file_path = os.path.join(current_dir, file_path)

        if os.path.exists(file_path):
            return file_path
        else:
            print(f"❌ 文件不存在: {file_path}")
            retry = input("是否重试？(y/n): ").lower()
            if retry != 'y':
                return None


def main():
    """主程序"""
    print("=" * 60)
    print("📊 Excel成绩处理系统")
    print("=" * 60)

    # 获取Excel文件路径
    file_path = get_excel_file_path()

    if not file_path:
        print("❌ 未提供有效文件路径，程序退出")
        return

    print(f"\n📁 处理文件: {file_path}")

    # 创建处理器
    processor = ExcelGradeProcessor(file_path)

    # 加载Excel数据
    excel_data = processor.load_excel_data()

    if excel_data is None:
        print("❌ 无法加载Excel文件，程序退出")
        return

    # 处理所有工作表
    processor.process_all_sheets(excel_data)

    # 生成报告
    print(f"\n{'=' * 60}")
    print("📄 生成最终报告")
    print(f"{'=' * 60}")

    # 询问是否保存报告
    save_report = input("是否将报告保存到文件？(y/n): ").lower().strip()

    if save_report == 'y':
        default_output = f"{os.path.splitext(os.path.basename(file_path))[0]}_report.txt"
        output_file = input(f"请输入输出文件名 (默认: {default_output}): ").strip()

        if not output_file:
            output_file = default_output

        processor.generate_report(output_file)
    else:
        processor.generate_report()

    # 打印简要统计
    processor.print_summary()

    # 交互式查询
    while True:
        print(f"\n{'=' * 60}")
        print("🔍 交互式查询")
        print("1. 查看特定学生")
        print("2. 查看特定教师")
        print("3. 重新生成报告")
        print("4. 查看所有学生")
        print("5. 查看所有教师")
        print("0. 退出")

        choice = input("\n请选择操作: ").strip()

        if choice == '0':
            print("👋 感谢使用，再见！")
            break
        elif choice == '1':
            student_name = input("请输入学生姓名: ").strip()
            found = False
            for student in processor.students:
                if student.name.lower() == student_name.lower():
                    print(f"  {student.get_grade()}")
                    found = True
                    break
            if not found:
                print(f"❌ 未找到学生: {student_name}")
        elif choice == '2':
            teacher_name = input("请输入教师姓名: ").strip()
            found = False
            for teacher in processor.teachers:
                if teacher.name.lower() == teacher_name.lower():
                    print(f"  {teacher.get_grade()}")
                    if teacher.grades:
                        pass_rate = teacher.get_passing_rate()
                        print(f"  通过率: {pass_rate:.1f}%")
                    found = True
                    break
            if not found:
                print(f"❌ 未找到教师: {teacher_name}")
        elif choice == '3':
            processor.generate_report()
        elif choice == '4':
            print("\n所有学生:")
            for i, student in enumerate(processor.students, 1):
                print(f"  {i}. {student.get_grade()}")
        elif choice == '5':
            if processor.teachers:
                print("\n所有教师:")
                for i, teacher in enumerate(processor.teachers, 1):
                    print(f"  {i}. {teacher.get_grade()}")
            else:
                print("暂无教师数据")
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    main()