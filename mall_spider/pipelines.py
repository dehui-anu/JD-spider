# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from mall_spider.spiders.jd_product import JdProductSpider
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pymongo import MongoClient
from mall_spider.spiders.jd_category import JdCategorySpider
from mall_spider.settings import MONGODB_URL

class CategoryPipeline:
    #当爬虫启动时，执行
    def open_spier(self,spider):
        if isinstance(spider,JdCategorySpider):
            self.client = MongoClient()
            self.collection = self.client['jd']['category']



    def process_item(self, item, spider):
        #向mongodb中插入数据
        if isinstance(spider,JdCategorySpider):
            self.collection.insert_one(dict(item))

        return item

    def close_spider(self,spider):
        #关闭mongodb的链接
        if isinstance(spider,JdCategorySpider):
            self.client.close()


#在 open_spider方法, 建立MongoDB数据库连接, 获取要操作的集合
#在 process_item方法, 把数据插入到MongoDB中
#在close_spider方法, 关闭数据库连接

class ProductPipeline(object):

    def open_spider(self, spider):
        if isinstance(spider, JdProductSpider):
            # 建立MongoDB数据库链接
            self.client = MongoClient(MONGODB_URL)
            # 获取要操作集合
            self.category = self.client['jd']['product']

    def process_item(self, item, spider):
        if isinstance(spider, JdProductSpider):
            # 把数据插入到mongo中
            self.category.insert_one(dict(item))

        return item

    def close_spider(self, spider):
        """关闭"""
        if isinstance(spider, JdProductSpider):
            self.client.close()


