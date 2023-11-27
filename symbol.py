# 定义一个商品类
class Symbol:
    # 定义构造方法，初始化商品的基本属性
    def __init__(self, id, name, price, producer):
        self.id = id # 商品号
        self.name = name # 商品名
        self.price = price # 商品价格
        self.producer = producer # 生产商
        self.history = [] # 商品历史价格数据，用列表存储

    # 定义一个方法，用于向商品历史价格数据中添加新的价格
    def add_price(self, new_price):
        self.history.append(new_price)

    # 定义一个方法，用于从商品历史价格数据中读取指定索引的价格
    def get_price(self, index):
        if index >= 0 and index < len(self.history):
            return self.history[index]
        else:
            return None

    # 定义一个方法，用于查询商品历史价格数据的长度
    def get_history_length(self):
        return len(self.history)

    # 定义一个方法，用于评估商品的价值，根据商品历史价格数据的平均值和标准差进行评估
    def evaluate_value(self):
        # 如果商品历史价格数据为空，返回None
        if len(self.history) == 0:
            return None
        # 否则，计算商品历史价格数据的平均值和标准差
        else:
            # 导入math模块，用于计算平方根
            import math
            # 计算平均值
            mean = sum(self.history) / len(self.history)
            # 计算标准差
            variance = sum([(x - mean) ** 2 for x in self.history]) / len(self.history)
            std = math.sqrt(variance)
            # 返回平均值和标准差的元组
            return (mean, std)

# 定义一个子类，继承商品类
class MetalSymbol(Symbol):
    # 定义构造方法，初始化子类的属性
    def __init__(self, id, name, price, producer, discount):
        # 调用父类的构造方法，初始化父类的属性
        super().__init__(id, name, price, producer)
        # 添加子类特有的属性，折扣率
        self.discount = discount

    # 重写父类的evaluate_value方法，根据折扣率计算商品的价值
    def evaluate_value(self):
        # 如果商品历史价格数据为空，返回None
        if len(self.history) == 0:
            return None
        # 否则，计算商品历史价格数据的平均值
        else:
            mean = sum(self.history) / len(self.history)
            # 根据折扣率计算商品的价值
            value = mean * (1 - self.discount)
            # 返回商品的价值
            return value
