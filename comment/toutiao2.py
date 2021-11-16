#encoding=utf-8
import re
import scrapy
from pipeline import CommentItem
import json
import time
from scrapy import Request

class Toutiao(scrapy.Spider):
	name = 'jrtt_comment'

	l1_comment_api = 'https://www.toutiao.com/article/v2/tab_comments/?' \
	'aid=24&app_name=toutiao_web&offset={offset}&count=20&group_id={post_id}'
	l2_comment_api = 'https://www.toutiao.com/2/comment/v2/reply_list/?' \
		'aid=24&app_name=toutiao_web&id={l1_id}&offset={offset}&count=20&repost=0'
	
	headers = {
		"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
	}

	def start_requests(self):
		urls = ['http://www.toutiao.com/a1716229829213195/', 'http://www.toutiao.com/a7029627438833353248/']
		for url in urls:
			post_id = re.search('/a(\d+)/?.*', url)
			if post_id:
				post_id = post_id.group(1)
				offset = 0
				l1_req = self.l1_comment_api.format(offset=offset,post_id=post_id)
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
			has_child = each['comment']['reply_count']
			if has_child > 0:
				l2_req = self.l2_comment_api.format(l1_id=l1_id, offset=0)
				yield Request(l2_req, headers=self.headers, callback=self.parse_l2_comment, meta={'l1_id': l1_id,  'url': url})
			yield item
		has_more = r.get('has_more', '')
		if has_more:
			offset = r['offset']
			l1_req = self.l1_comment_api.format(offset=offset,post_id=post_id)
			yield Request(l1_req, headers=self.headers, callback=self.parse_l1_comment, meta={"url": url, "post_id": post_id})

	def parse_l2_comment(self, response):
		l1_id = response.meta['l1_id']
		url = response.meta['url']
		r = json.loads(response.text)['data']
		if not r:
			return
		for each in r['data']:
			item = self.extract_comment(each)
			item['url'] = url
		has_more = r.get('has_more', '')
		if has_more:
			offset = r['offset']
			l2_req = self.l2_comment_api.format(l1_id=l1_id, offset=offset)
			yield Request(l2_req, headers=self.headers, callback=self.parse_l2_comment, meta={'l1_id': l1_id, 'url': url})

	def extract_comment(self, data):
		comment = data.get('comment')
		if comment:
			author_name = comment['user_name']
		else:
			comment = data
			author_name = comment['user']['name']
		id_ = comment['id']
		post_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(comment['create_time'])))
		like_num = comment['digg_count']
		content = comment['text']
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
			pathlib.Path('item_toutiao.csv'): {
				'format': 'csv',
				'fields': ['like_num', 'author_name', 'content', 'post_time', 'url'],
			},
		}
	})
	process.crawl(Toutiao)
	process.start()