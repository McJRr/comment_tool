#encoding=utf-8
import re
import scrapy
from pipeline import CommentItem
import json
import time
import dateparser
from scrapy import Request
from id_zh import trans_10id

def get_url():
	with open('w.txt', 'r') as f:
		for line in f.readlines():
			line = line.strip('\n').strip()
			time.sleep(1)
			yield line

class Weibo(scrapy.Spider):
	name = 'weibo_comment'

	l1_comment_api = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&' \
		'id={post_id}&is_show_bulletin=2&is_mix=0&max_id={max_id}&count=20'
	l2_comment_api = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1' \
		'&id={l1_id}&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id={max_id}&count=20'
	
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
				max_id = 0
				l1_req = self.l1_comment_api.format(max_id=max_id,post_id=post_id)
				yield Request(l1_req, headers=self.headers, callback=self.parse_l1_comment, meta={ "url": url, "post_id": post_id})

	def parse_l1_comment(self, response):
		url = response.meta['url']
		post_id = response.meta['post_id']
		r = json.loads(response.body)
		d1 = r['data']
		if not d1:
			return 
		for each in d1:
			item = self.extract_comment(each)
			l1_id = item['id']
			item['url'] = url
			has_child = each['total_number']
			if has_child > 0:
				l2_req = self.l2_comment_api.format(l1_id=l1_id, max_id=0)
				yield Request(l2_req, headers=self.headers, callback=self.parse_l2_comment, meta={'l1_id': l1_id,  'url': url})
			yield item
		max_id = r['max_id']
		if max_id > 0 and len(r['data']):
			l1_req = self.l1_comment_api.format(max_id=max_id,post_id=post_id)
			yield Request(l1_req, headers=self.headers, callback=self.parse_l1_comment, meta={"url": url, "post_id": post_id})

	def parse_l2_comment(self, response):
		l1_id = response.meta['l1_id']
		url = response.meta['url']
		r = json.loads(response.text)
		d2 = r['data']
		if not d2:
			return
		for each in d2:
			item = self.extract_comment(each)
			item['url'] = url
		max_id = r.get('max_id', 0)
		if max_id > 0 and len(r['data']):
			l2_req = self.l2_comment_api.format(l1_id=l1_id, max_id=max_id)
			yield Request(l2_req, headers=self.headers, callback=self.parse_l2_comment, meta={'l1_id': l1_id, 'url': url})

	def extract_comment(self, data):
		author_name = data['user']['name']
		id_ = data['id']
		time_str = data['created_at'].replace('+0800 ', '')
		post_time = dateparser.parse(time_str).strftime('%Y-%m-%d %H:%M:%S')
		like_num = data['like_counts']
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
		"DOWNLOAD_DELAY": 1,
		"DOWNLOADER_MIDDLEWARES": {"proxy.RandomProxy" : 200},
		"PROXY_MODE": "la",
		"FEEDS": {
			pathlib.Path('weibo_comment_18_01.csv'): {
				'format': 'csv',
				'fields': ['like_num', 'author_name', 'content', 'post_time', 'url'],
			},
		}
	})
	process.crawl(Weibo)
	process.start()