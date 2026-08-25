import random

class Add_list:
    def __init__(self,self_data,pangle_data,top_data):
        self.self_data = self_data
        self.pangle_data = pangle_data
        self.top_data = top_data
        self.combined_list= self_data + pangle_data
        self.pinned_items = []
        ## 等级权重映射（s+ > s > a > b > c）
        self.rank_weight = {'s+': 5, 's': 4, 'a': 3, 'b': 2, 'c': 1}
        self.remaining_items = self.combined_list.copy()
        self.final_list = []

    def extract_pinned_items(self):
        """提取置顶元素"""
        for top_id in self.top_data:
    # 初始化变量为空，记录是否完全查询完成
            found_item = None

            if not self.remaining_items:
               print(f"跳过ID {top_id}，因为剩余项目为空")
               continue # 跳过本次循环的剩余代码

    # 字典item方法为遍历在全量表格里面，然后去匹配top
            for item in self.remaining_items:
        # 因为全量表里面带有等级这里就取第二个【1】ID
                if item[1] == top_id:
                    found_item = item
                    break

            # 如果不为空
            if found_item:
                # 将found_item放到pinned_item末尾里
                self.pinned_items.append(found_item)
                # 将发现的重复的ID从合并表中移除，不然会重复展示
                self.remaining_items.remove(found_item)
        # 在if完成后再打印结果
        print("确认后的ID:")
        print(self.pinned_items)

    def group_and_shuffle_remaining(self):
        """对剩余元素按等级分组并在组内随机打乱"""
        groups = {}
        for item in self.remaining_items:
            rank = item[0]
            if rank not in groups:
                groups[rank] = []
            groups[rank].append(item)

        for rank in groups:
            random.shuffle(groups[rank])
        print('再rank分组后的groups：')
        print(groups)

        return groups

# 按等级权重降序连接各组（s+排最前）
# groups.keys(): 获取字典 groups中所有的键（Key），即不同的等级标签（如 'S+', 'A', 'B'）。
# sorted(): Python 内置的排序函数。
# key=lambda r: rank_weight[r]: 这是排序的关键。它通过一个名为 rank_weight的字典，将每个等级标签 rank映射为一个可比较的数值（权重），排序实际依据的是这个权重值。例如，rank_weight可能是 {'S+': 5, 'A': 4, 'B': 3, ...}。
# reverse=True: 表示按权重降序排列。权重最高的等级将排在最前面。
# 按权重降序排序等级标签
# sorted_remaining = []: 初始化一个空列表，用于存放最终排序后的所有项目。
# for rank in sorted_ranks: 循环遍历已经按权重降序排好的等级标签列表。
# sorted_remaining.extend(groups[rank]): 在每一轮循环中，根据当前等级标签 rank，从分组字典 groups中取出该等级对应的整个项目列表，并将其中的所有元素逐个添加到 sorted_remaining的末尾

    def sort_remaining_by_rank(self, groups):
        """按等级权重排序剩余元素"""
        sorted_ranks = sorted(groups.keys(), key=lambda r: self.rank_weight[r], reverse=True)
        sorted_remaining = []
        for rank in sorted_ranks:
            sorted_remaining.extend(groups[rank]) # 将组内元素按等级顺序连接
        return sorted_remaining

# 4. 合并最终列表：置顶元素在前，剩余元素在后
    def build_final_list(self):
        """构建最终列表"""
        self.extract_pinned_items()
        groups = self.group_and_shuffle_remaining()
        sorted_remaining = self.sort_remaining_by_rank(groups)
        self.final_list = self.pinned_items + sorted_remaining
        return self.final_list

    def print_debug_info(self):
        """打印调试信息（可选）"""
        print("整合后:", self.combined_list)
        print("置顶元素:", self.pinned_items)
        print("剩余元素分组并打乱后:", self.group_and_shuffle_remaining())
        print("最终列表:")
        for item in self.final_list:
            print(f"  {item}")


if __name__ == "__main__":
    # 原始数据
    self_data = [['s+', 90001], ['a', 90002], ['s+', 90003], ['s', 90004], ['a', 90005], ['b', 90006], ['c', 90007]]
    pangle_data = [['s+', 10001], ['a', 10002], ['s+', 10003], ['s', 10004], ['a', 10005], ['b', 10006], ['c', 10007]]
    top_data = [90001, 10001, 90007, 1010588, 10006]  # 置顶ID列表（100001不存在，自动跳过）

    adder = Add_list(self_data, pangle_data, top_data)
    final = adder.build_final_list()
    adder.print_debug_info()