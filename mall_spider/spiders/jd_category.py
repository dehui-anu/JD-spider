import scrapy
import json
from mall_spider.items import Category

class JdCategorySpider(scrapy.Spider):
    name = 'jd_category'
    allowed_domains = ['jd.com']
    start_urls = ['https://dc.3.cn/category/get'] #起始url

    def parse(self, response):
        result = json.loads(response.body.decode('GBK'))
        datas =result['data']
        #遍历数据列表
        for data in datas:

            item = Category

            b_category = data['s'][0]
            b_category_info = b_category['n']
            item['b_category_name'], item['b_category_url'] =self.get_category_name_rul(b_category_info)

            m_category_s = b_category['s']
            for m_category in m_category_s:
                m_category_info = m_category['n']
                item['m_category_name'], item['m_category_url'] = self.get_category_name_rul(m_category_info)


                s_category_s = m_category['s']
                for s_category in s_category_s:
                    s_category_info = s_category['n']
                    item['s_category_name'], item['s_category_url'] = self.get_category_name_rul(s_category_info)

                    #把数据给引擎
                    yield item


    def get_category_name_rul(self,category_info):
        #根据分类信息，提取名字，网址，有的网址杠，逗号啥的不一样，去网页点上去看看
        #用|解，然后分类url和名字
        category = category_info.split('|')
        category_url = category[0]
        category_name = category[1]

        if category_url.count('jd.com') == 1:#处理URL
            #补全
            category_url = 'https://' + category_url
        elif category_url.count('-') == 1:
            category_url = 'https://channel.jd.com/{}.html'.format(category_url)
        else:
            #上面这个填到下面
            category_url = category_url.replace('-',',')
            category_url = 'https://list.jd.com/list.html?cat={}'.format(category_url)

        return  category_name, category_url