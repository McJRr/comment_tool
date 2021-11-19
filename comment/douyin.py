import scrapy
from pipeline import DouyinHudongItem
from scrapy import Request
import json
import re
import time

def get_url():
	with open('d.txt', 'r') as f:
		for line in f.readlines():
			line = line.strip('\n').strip()
			time.sleep(1.5)
			yield line


class DouyinHudong(scrapy.Spider):
    name = "douyin_hudong"
    headers = {
        "User-Agent": "PostmanRuntime/7.28.4"
    }
    def start_requests(self):
        for url in get_url():
        # url = 'http://www.iesdouyin.com/share/video/7029343833901124879'
            post_id = re.search('/video/(\d+)', url)
            if post_id:
                post_id = post_id.group(1)
                req_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='+ str(post_id)
                yield Request(req_url, headers=self.headers, callback=self.parse_statistics, meta={'url': url})

    def parse_statistics(self, response):
        url = response.meta['url']
        item = DouyinHudongItem()
        item['url'] = url
        try:
            res = json.loads(response.body)['item_list'][0]
            statistic = res['statistics']
            item['like_num'] = statistic['digg_count']
            item['comment_num'] = statistic['comment_count']
            item['share_num'] = statistic['share_count']
        except Exception as e:
            print(e)
            item['like_num'] = None
            item['comment_num'] = None
            item['share_num'] = None
        yield item



if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    import pathlib
    process = CrawlerProcess(settings={
        "DOWNLOAD_DELAY": 2,
        "FEEDS": {
            pathlib.Path('douyin_17_01.csv'): {
                'format': 'csv',
                'fields': ['like_num', 'comment_num', 'share_num', 'url'],
            },
        }
    })
    process.crawl(DouyinHudong)
    process.start()