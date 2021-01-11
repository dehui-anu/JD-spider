# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MallSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



#定义商品的类别，大中小的名字，URL
class Category(scrapy.Item):
    #大分类名称
    b_category_name = scrapy.Field()
    b_category_url = scrapy.Field()
    #中
    m_category_name = scrapy.Field()
    m_category_url = scrapy.Field()
    #小
    s_category_name = scrapy.Field()
    s_category_url = scrapy.Field()

#定义商品的相关数据
class Product(object):
    product_category = scrapy.Field() #类别
    product_category_id = scrapy.Field()
    product_sku_id = scrapy.Field() #ID
    product_name = scrapy.Field()
    product_img_url= scrapy.Field()
    product_book_info= scrapy.Field() #书的信息，作者等
    product_option= scrapy.Field()
    product_shop = scrapy.Field()
    product_comments = scrapy.Field()
    product_price = scrapy.Field()




