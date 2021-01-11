# 在项目文件夹下创建 add_category_to_redis.py
# 实现方法 add_category_to_redis:
# 链接MongoDB
# 链接Redis
# 读取MongoDB中分类信息, 序列化后, 添加到商品爬虫redis_key指定的list
# 关闭MongoDB
# 在if __name__ == '__main__':中调用add_category_to_redis方法

from redis import StrictRedis
from pymongo import MongoClient
import pickle

from mall_spider.settings import MONGODB_URL, REDIS_URL
from mall_spider.spiders.jd_product import JdProductSpider

# 把MongoDB中分类信息, 添加到Redis中
def add_category_to_redis():
    # 链接MongoDB
    client = MongoClient(MONGODB_URL)
    # 链接Redis
    redis = StrictRedis.from_url(REDIS_URL)

    cursor = client['jd']['category'].find() #[]mongo里有JD，JD里有CATEGORY,获取数据库中分类集合
    # 读取MongoDB中分类信息, 序列化后, 添加到商品爬虫redis_key指定的list
    for category in cursor:
        # 序列化字典数据
        data = pickle.dumps(category)
        # 添加商品爬虫redis_key指定的list
        redis.rpush(JdProductSpider.redis_key, data)

    # 关闭MongoDB的链接
    client.close()

if __name__ == '__main__':   #在if __name__ == '__main__':中调用add_category_to_redis方法
    add_category_to_redis()





