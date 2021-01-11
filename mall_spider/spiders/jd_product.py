import scrapy
import json
from jsonpath import jsonpath
from mall_spider.items import Product
from scrapy_redis.spiders import RedisSpider
import pickle


#    修改继承关系
#    指定redis_key
#    把重写start_requests 改为 重写 make_request_from_data
#     使用return返回一个请求对象. 不能使用yield
class JdProductSpider(RedisSpider):
    name = 'jd_product'
    allowed_domains = ['jd.com']

    #  指定redis_key,指定起始URL列表，在redis数据库中的key
    redis_key = 'jd_product:start_category'

    # #重写start_requests方法，后面不需要了，去看视频，得重写掉，前期用来分类逻辑，用上数据库就不用这个了
    # def make_request_from_data(self, data):
    #     #根据分类信息构建列表页的请求
    #     category = {"b_category_name" : "家用电器",
    #                   "b_category_url" : "https://jiadian.jd.com",
    #                   "m_category_name" : "洗衣机",
    #                   "m_category_url" : "https://list.jd.com/list.html?cat=737,794,880",
    #                   "s_category_name" : "洗衣机配件",
    #                   "s_category_url" : "https://list.jd.com/list.html?cat=737,794,877"}
    #
    #     #根据小分类的URL，构建列表页请求
    #     yield scrapy.Request(category['s_category_url'], callback=self.parse, meta={'category': category})


    # 重写start_requests 改为 重写 make_request_from_data
    def make_request_from_data(self, data):
        # 把从Redis中读取到分类信息, 转换为字典。根据redis的二进制数据构建请求。param分类信息的二进制数据。return构建的请求对象
        # 使用return返回一个请求对象. 不能使用yield
        category = pickle.loads(data)
        return scrapy.Request(category['s_category_url'], self.parse, meta={'category': category})


    def parse(self, response):
        # 获取类别信息
        category = response.meta['category']
        # 获取类别的URL
        category_url = response.url.split('&')[0]
        #提取skuid
        sku_ids = response.xpath('//div[contains(@class, "j-sku-item")]/@data-sku').extract()
        # 遍历sku_ids, 构建基本详情信息的请求
        for sku_id in sku_ids:
            item = {
                'product_category': category,
                'product_sku_id': sku_id
            }
            product_url = 'https://cdnware.m.jd.com/c1/skuDetail/apple/7.3.0/{}.json'.format(sku_id)
            yield scrapy.Request(product_url, callback=self.parse_product, meta={'item': item})


        # 获取下一页的URL
        next_url = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_url:
            # 补全URL
            next_url = response.urljoin(next_url)
            # 构建下一页请求
            yield scrapy.Request(next_url, callback=self.parse, meta={'category': category})

    def parse_product(self, response):
        # 取出传递过来的数据
        item = response.meta['item']
        # 把响应数据数据转为字典
        product_dic = json.loads(response.text)

        # 获取商品名称
        item['product_name'] = product_dic['wareInfo']['basicInfo']['name']
        if  item['product_name']:
            # 获取类别id, 把 `;` 替换为 ,
            item['product_category_id'] = product_dic['wareInfo']['basicInfo']['category'].replace(';', ',')

            # 获取店铺信息
            product_shop = jsonpath(product_dic, '$..shop')
            if product_shop:
                product_shop = product_shop[0]
                if product_shop is None:
                    item['product_shop'] = {'name':'京东自营'}
                else:
                    item['product_shop'] = {
                        "shopId": product_shop['shopId'],
                        "name": product_shop['name'],
                        "score": product_shop['score'],
                        "url": product_shop['url'],
                    }

            # 如果是书, 记录书的信息
            if product_dic['wareInfo']['basicInfo']['bookInfo']['display']:
                item['product_book_info'] = product_dic['wareInfo']['basicInfo']['bookInfo']
                # 删除display
                del item['book_info']['display']


            # 获取商品选购信息
            color_sizes = jsonpath(product_dic, '$..colorSize')
            product_option = {}
            if color_sizes:
                for color_size in color_sizes[0]:
                    title = color_size['title']
                    texts = jsonpath(color_size, '$..text')
                    product_option.update({title:texts})
                    # print(product_option)
            item['product_option'] = product_option
            # 商品图片
            item['product_img_url'] = jsonpath(product_dic, '$..wareImage[0].small')[0]

            # 构建促销信息的请求
            ad_url = 'https://cd.jd.com/promotion/v2?skuId={}&area=1_72_4137_0&cat={}'.format(item['product_sku_id'], item['product_category_id'])
            yield scrapy.Request(ad_url, callback=self.parse_ad, meta={'item': item})

    def parse_ad(self, response):
        #获取商品促销信息
        item = response.meta['item']
        ad_dic = json.loads(response.body.decode('GB18030'))
        ad = ad_dic['ads'][0]['ad']
        item['product_ad'] = ad

        # for key, value in item.items():
        #     print('{} = {}'.format(key, value))

        # 构建平均信息请求
        comments_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(
            item['product_sku_id'])
        yield scrapy.Request(comments_url, callback=self.parse_comments, meta={'item': item})

    def parse_comments(self, response):
        #解析商品评论信息
        item = response.meta['item']
        comments_dic = json.loads(response.text)
        comments = {
            'comment_count': jsonpath(comments_dic, '$..CommentCount')[0],
            'good_rate': jsonpath(comments_dic, '$..GoodRate')[0],
            'poor_count': jsonpath(comments_dic, '$..PoorCount')[0],
        }
        item['product_comments'] = comments
        # print(item)
        # 构建价格请求
        price_url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['product_sku_id'])
        yield scrapy.Request(price_url, callback=self.parse_price, meta={'item': item})

    def parse_price(self, response):
        #解析价格
        item = response.meta['item']
        item['product_price'] = json.loads(response.text)[0]['p']
        # print(item)
        yield item