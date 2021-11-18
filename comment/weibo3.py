#encoding=utf-8
from pathlib import PosixPath
import re
import scrapy
from pipeline import CommentItem
import json
import time
import dateparser
from scrapy import Request
from id_zh import trans_10id

def get_url():
    with open('./comment/w2.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n').strip()
            time.sleep(1)
            yield line

class Weibo(scrapy.Spider):
    name = 'weibo_repost'

    r_api = 'https://weibo.com/ajax/statuses/repostTimeline?id={post_id}&page={page}&moduleID=feed'
    
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }

    def start_requests(self):
        # url = 'https://weibo.com/1853098262/KBwjW5gdz'
        for url in get_url():
            post_id = re.search('/\d+/(\w+)', url)
            if post_id:
                post_id = post_id.group(1)
                post_id = trans_10id(post_id)
                page = 1
                r_req = self.r_api.format(post_id=post_id, page=page)
                yield Request(r_req, headers=self.headers, callback=self.parse_repost, meta={ "url": url, "post_id": post_id, 'page': page})

    def parse_repost(self, response):
        url = response.meta['url']
        page = response.meta['page']
        post_id = response.meta['post_id']
        r = json.loads(response.body)
        d1 = r['data']
        if not d1:
            return 
        for each in d1:
            item = self.extract_comment(each)
            item['url'] = url
            yield item
        max_page = r['max_page']
        if page <= max_page and len(r['data']):
            page = page + 1
            r_req = self.r_api.format(post_id=post_id, page=page)
            yield Request(r_req, headers=self.headers, callback=self.parse_repost, meta={ "url": url, "post_id": post_id, 'page': page})

    def extract_comment(self, data):
        author_name = data['user']['screen_name']
        id_ = data['id']
        time_str = data['created_at'].replace('+0800 ', '')
        post_time = dateparser.parse(time_str).strftime('%Y-%m-%d %H:%M:%S')
        like_num = data['attitudes_count']
        content = data['text_raw']
        item = CommentItem()
        item['author_name'] = author_name
        item['content'] = content
        item['post_time'] = post_time
        item['id'] = id_
        item['like_num'] = like_num
        return item



if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    import pathlib
    process = CrawlerProcess(settings={
        "DOWNLOAD_DELAY": 2,
        "FEEDS": {
            pathlib.Path('weibo_repost_18_01.csv'): {
                'format': 'csv',
                'fields': ['like_num', 'author_name', 'content', 'post_time', 'url'],
            },
        }
    })
    process.crawl(Weibo)
    process.start()