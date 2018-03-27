# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy_redis.spiders import RedisSpider


class TbSpider(RedisSpider):
    name = 'tb'
    allowed_domains = ['taobao.com']

    def start_requests(self):
        for i in range(5):
            page = i*48
            url = "https://s.taobao.com/search?data-key=s&data-value={}&ajax=true&callback=jsonp622&q=%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91&imgfile=&js=1&stats_click=search_radio_all:1&initiative_id=staobaoz_20180326&ie=utf8&p4ppushleft=5,48".format(page)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        data = re.findall(r"spus\":(.*?])}},", response.text, flags=re.S)
        data = data[0].replace("\\\"屏幕", "屏幕")
        data = json.loads(data)
        for i in data:
            item = dict()
            item['title'] = i["title"]
            item['price'] = i["price"]
            # item['screen'] = i["importantKey"]
            item['buyer_num'] = i["month_sales"]
            item['tags'] = ",".join([i["tag"] for i in i["tag_info"]])
            pspuid = re.findall(r"pspuid=(\d+)&", i["url"])
            if len(pspuid) > 0:
                url = "https://s.taobao.com/api?pspuid={}&callback=jsonp643&app=api&m=spudetail&detail_tab=params".format(pspuid[0])
                yield scrapy.Request(url, callback=self.detail, meta={"item": item})

    def detail(self, response):
        item = response.meta["item"]
        data = re.sub(r"jsonp\d+\(|\);", "", response.text)
        data = json.loads(data)
        temp = dict()
        for i in data["params"]:
            temp[i["pname"]] = i["pvalue"]
        temp.update(item)
        if "锂电池电芯数量" not in temp:
            temp["锂电池电芯数量"] = "0"
        print(temp)
        yield temp

