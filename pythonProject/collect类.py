from collections import *
#namedtuple 命名元组，可命名访问 小型数据库记录
#deque 双端队列，高效头尾操作 队列、栈、滑动窗口
#Counter 计数器，统计元素频率 词频统计、投票计数
#OrderedDict 有序字典（Python 3.7+ 默认有序）保持插入顺序
#defaultdict 默认字典，自动初始化值 分组统计、图结构（默认None，default_factory）
#ChainMap 链式映射，合并多个字典 配置管理、作用域链


#定义元组类型
point =namedtuple("point", ["x", "y"]) #定义point的名称/
#带默认值元组
Employee = namedtuple('Employee', ['name', 'id', 'department'], defaults=['未分配'])
emp1 = Employee("李四", 1001)
print(emp1)  # Employee(name='李四', id=1001, department='未分配')

# 场景1：名单系统
# 定义命名元组类型
Point = namedtuple('Point', ['x', 'y'])
Color = namedtuple('Color', 'red green blue')
Student = namedtuple('Student', 'name age grade')

# 创建实例
p1 = Point(10, 20)
p2 = Point(x=5, y=15)
color_red = Color(255, 0, 0)
student = Student("张三", 18, "A+")

# 访问属性
print(f"点坐标: ({p1.x}, {p1.y})")    # (10, 20)
print(f"学生姓名: {student.name}")     # 张三
print(f"红色RGB: {color_red.red}")    # 255

# 索引访问
print(f"第一个元素: {p1[0]}")          # 10
print(f"第二个元素: {p1[1]}")          # 20

# 迭代
for coord in p1:
    print(f"坐标: {coord}")

# 转换为字典，为什么转换为字典，转换为更清晰的键值队展示josn，当然也可以字典转为元组，适用于api-json返回取值时

p3 = p1._asdict()
print(p3) # {'x': 10, 'y': 20}

# 替换字段值
p4 = p1._replace(x=100)
print(f"新坐标: {p4}")  # Point(x=100, y=20)

#字典从元组中取值，tuple(dict)--键的元组，tuple(dict.values())--只取值，tuple(dict.items())--键值对，tuple()+ 解包灵活元组
p5 = tuple(p3.items())
print(p5) #（'x':10,'y':20）

#双端队列用法------------------------
Deque = deque(['a','b','c'])
print(f"初始化Deque: {Deque}")

#添加元素
Deque.append('d') #右侧添加单个
Deque.extend(['e','f']) #右侧拓展多个，顺序添加
Deque.appendleft('g') #左侧添加单个
Deque.extendleft(['h','i'])#左侧添加多个，倒序

print(f"添加元素后:{Deque}") #['i', 'h', 'g', 'a', 'b', 'c', 'd', 'e', 'f']

# 2. 删除元素 pop()
try:   #跳过报错代码的方法--try-except-pass（最简单）
  Deque.pop() #右侧删除最后一个
  Deque.popleft(2) #左侧删除第一个
  print(f"删除元素后:{Deque}") #['h', 'g', 'a', 'b', 'c', 'd', 'e']
except TypeError as e:
  print(e)


#3旋转rotate(2)/(-2)
Deque.rotate(2)
print(f"旋转2位元素后:{Deque}")

# 4. 其他操作
print(f"队列长度: {len(Deque)}")      # 7
print(f"是否为空: {not Deque}")       # False
print(f"元素'c'的数量: {Deque.count('c')}")  # 1
print(f"'b'的索引: {Deque.index('b')}")     # 3
Deque.remove('b')  # 删除第一个'b'
print(f"删除'b'后: {Deque}")

# 5. 清空
Deque.clear()
print(f"清空后: {Deque}")  # deque([])

# 1. 设置最大长度
limited_deque = deque(maxlen=3)
for i in range(5):
    limited_deque.append(i)
    print(f"添加 {i}: {limited_deque}")
# 输出:
# 添加 0: deque([0], maxlen=3)
# 添加 1: deque([0, 1], maxlen=3)
# 添加 2: deque([0, 1, 2], maxlen=3)
# 添加 3: deque([1, 2, 3], maxlen=3)  # 自动删除最早的
# 添加 4: deque([2, 3, 4], maxlen=3)

#Counter - 计数器
# 1. 从可迭代对象创建
words = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple']
word_counts = Counter(words)
print(f"单词计数: {word_counts}")  # Counter({'apple': 3, 'banana': 2, 'orange': 1})

# 2. 从字典创建，已知计数
counts = Counter({'a': 4, 'b': 2, 'c': 1})
print(f"字典创建: {counts}")  #Counter({'a': 4, 'b': 2, 'c': 1})

# 3. 从关键字参数创建
letter_counts = Counter(a=3, b=2, c=1)
print(f"关键字创建: {letter_counts}") #Counter({'a': 3, 'b': 2, 'c': 1})

# 4. 从字符串创建
text = "abracadabra"
char_counts = Counter(text)
print(f"字符计数: {char_counts}") # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(f"字符a的计数：{char_counts['a']}") #单个字符的a的数量

#OrderedDict有序字典（Python 3.7+ 默认有序）保持插入顺序
#LRU缓存实现
class LRUCache:
    """最近最少使用缓存"""

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict() #有序存储

    def get(self, key):
        """获取缓存值"""
        if key not in self.cache:
            return -1

        #这里解释一下为什么if后面没有带else，因为有return，所以执行之后自动进入下一步运行，什么时候需要用else呢，
        #当有明确的二选一时就用，什么时候不带呢，反之亦然，当if存在很多嵌套判断时就尽量用if return，可读性强

        # 移动到最后表示最近使用
        self.cache.move_to_end(key)
        return self.cache[key] #返回缓存中对应键的值

    def put(self, key, value):
        """添加缓存"""
        if key in self.cache:
            # 更新值并移动到最后
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            self.cache[key] = value #添加新值

        # 如果超出容量，移除最旧的
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False) #popitem弹出最旧的（不是最新的）

    def __str__(self):
        return f"LRUCache({list(self.cache.items())})"
#__str__(self)：特殊方法名，定义对象字符串表示形式
#self.cache：LRUCache 实例的缓存字典
#self.cache.items()：返回键值对的视图
#list(...)：转换为列表
#f"LRUCache(...)"：格式化字符串
# 测试LRU缓存
cache = LRUCache(3)
cache.put(1, 'A')
cache.put(2, 'B')
cache.put(3, 'C')
print(f"添加3个: {cache}")

print(f"获取键2: {cache.get(2)}")
print(f"获取后: {cache}")

cache.put(4, 'D')  # 应该移除键1
print(f"添加第4个: {cache}")

###defaultdict - 默认字典----defaultdict(list)用于"分组收集"/defaultdict(int)用于"计数统计"/defaultdict(set)用于"去重分组"
#场景1：分组统计
def group_by_category(items):
    """按类别分组"""
    grouped = defaultdict(list)

    for item, category in items:  #这里会自动解包，不需要声明，格式和下面items需要统一
        grouped[category].append(item)

    return dict(grouped)  # 转换为普通字典

items = [
    ("苹果手机", "电子产品"),
    ("香蕉", "水果"),
    ("笔记本电脑", "电子产品"),
    ("橙子", "水果"),
    ("牛奶", "食品"),
    ("iPhone", "电子产品"),
    ("面包", "食品"),
]

grouped_items = group_by_category(items)
print("按类别分组:")
for category, items in grouped_items.items():
    print(f"  {category}: {items}")

####ChainMap - 链式映射
# 1. 创建ChainMap
dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 3, 'c': 4}
dict3 = {'c': 5, 'd': 6}

chain = ChainMap(dict1, dict2, dict3)
print(f"ChainMap: {chain}")  # ChainMap({'a': 1, 'b': 2}, {'b': 3, 'c': 4}, {'c': 5, 'd': 6})

# 2. 访问元素
print(f"a: {chain['a']}")  # 1 (来自dict1)
print(f"b: {chain['b']}")  # 2 (来自dict1，第一个找到的)
print(f"c: {chain['c']}")  # 4 (来自dict2，第一个找到的)
print(f"d: {chain['d']}")  # 6 (来自dict3)

# 3. 遍历
print("所有键:")
for key in chain:
    print(f"  {key}")  # 注意：重复键只出现一次 c d b a,遍历顺序是倒叙

print("所有键值对:")
for key, value in chain.items():
    print(f"  {key}: {value}")

# 4. 检查键
print(f"'a'在chain中: {'a' in chain}")  # True
print(f"'e'在chain中: {'e' in chain}")  # False


# 场景1：配置优先级
def get_config():
    """获取配置，按优先级：命令行 > 用户配置 > 默认配置"""
    # 默认配置
    default_config = {
        'host': 'localhost',
        'port': 8080,
        'debug': False,
        'log_level': 'INFO'
    }

    # 用户配置（覆盖默认）
    user_config = {
        'host': '127.0.0.1',
        'log_level': 'DEBUG'
    }

    # 命令行参数（最高优先级）
    command_line_args = {
        'debug': True,
        'port': 8888
    }

    # 创建配置链
    config = ChainMap(command_line_args, user_config, default_config)

    return config


config = get_config()
print("最终配置:")
for key in ['host', 'port', 'debug', 'log_level']:
    print(f"  {key}: {config[key]}")

###组合示例
"""
综合示例：简单的社交媒体分析
"""
from collections import defaultdict, Counter, deque
from datetime import datetime, timedelta

class SocialMediaAnalyzer:
    """社交媒体分析器"""

    def __init__(self):
        self.posts = []  # 所有帖子
        self.user_posts = defaultdict(list)  # 用户帖子
        self.hashtag_counter = Counter()  # 话题统计
        self.recent_posts = deque(maxlen=100)  # 最近100个帖子

    def add_post(self, user, content, hashtags=None):
        """添加帖子"""
        post = {
            'user': user,
            'content': content,
            'hashtags': hashtags or [],
            'timestamp': datetime.now(),
            'likes': 0
        }

        self.posts.append(post)
        self.user_posts[user].append(post)
        self.recent_posts.append(post)

        # 统计话题
        for tag in hashtags or []:
            self.hashtag_counter[tag] += 1

        return post

    def get_user_stats(self, user):
        """获取用户统计"""
        if user not in self.user_posts:
            return None

        posts = self.user_posts[user]
        hashtags = []
        for post in posts:
            hashtags.extend(post['hashtags'])

        return {
            'post_count': len(posts),
            'total_likes': sum(post['likes'] for post in posts),
            'avg_likes': sum(post['likes'] for post in posts) / len(posts) if posts else 0,
            'top_hashtags': Counter(hashtags).most_common(5)
        }

    def get_trending_hashtags(self, limit=10):
        """获取热门话题"""
        return self.hashtag_counter.most_common(limit)

    def get_recent_posts(self):
        """获取最近帖子"""
        return list(self.recent_posts)

    def get_network_info(self):
        """获取网络信息"""
        # 计算用户互动
        interactions = defaultdict(Counter)

        for post in self.posts:
            for other_post in self.posts:
                if post['user'] != other_post['user']:
                    # 简单互动计算（实际会更复杂）
                    common_tags = set(post['hashtags']) & set(other_post['hashtags'])
                    if common_tags:
                        interactions[post['user']][other_post['user']] += len(common_tags)

        return interactions

# 使用示例
analyzer = SocialMediaAnalyzer()

# 添加帖子
analyzer.add_post("张三", "今天天气真好！", ["天气", "生活"])
analyzer.add_post("李四", "学习Python中", ["编程", "Python", "学习"])
analyzer.add_post("王五", "Python真有趣", ["Python", "编程"])
analyzer.add_post("张三", "又开始编程了", ["编程", "工作"])
analyzer.add_post("李四", "天气不错，适合编程", ["天气", "编程"])

# 获取统计
print("用户统计:")
for user in ["张三", "李四", "王五"]:
    stats = analyzer.get_user_stats(user)
    if stats:
        print(f"\n{user}:")
        print(f"  发帖数: {stats['post_count']}")
        print(f"  平均点赞: {stats['avg_likes']:.1f}")
        print(f"  常用话题: {[tag for tag, _ in stats['top_hashtags']]}")

print("\n热门话题:")
for tag, count in analyzer.get_trending_hashtags():
    print(f"  #{tag}: {count}次")

print("\n最近帖子:")
for post in analyzer.get_recent_posts():
    print(f"  {post['user']}: {post['content'][:20]}...")