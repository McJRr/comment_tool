import json
import requests
import dateparser
import time
# import logging
import random
try:
	from id_zh import trans_10id
except ImportError:
	from .id_zh import trans_10id

# logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',level=logging.INFO)
# LOGGER = logging.getLogger(__name__)

class WeiboComment():
	
	l1_comment_api = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&' \
		'id={post_id}&is_show_bulletin=2&is_mix=0&max_id={max_id}&count=20'
	l2_comment_api = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1' \
		'&id={l1_id}&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id={max_id}&count=20'

	headers = {
		'referer': 'https://weibo.com/',
		'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"macOS"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin',
		'traceparent': '00-a9eb2ee4095dd8f62516601a56fd5479-8d24445384f16e97-00',
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
		'x-requested-with': 'XMLHttpRequest',
		'x-xsrf-token': 'm2gt7Mtq2GTCM5dksQj4E4IU',
		'Cookie': 'XSRF-TOKEN=4wzAy6kpFT_MVLm7-R8Xxo-Y'
	}

	comments = []

	def __init__(self, post_id, url) -> None:
		self.s = requests.Session()
		print('Get Weibo ID %s ' % post_id)
		self.post_id = trans_10id(post_id)
		self.url = url

	def get_comment(self, max_id=0):
		try:
			l1_req = self.l1_comment_api.format(max_id=max_id,post_id=self.post_id)
			time.sleep(random.randint(0,3))
			# print('Request %s ...' % l1_req)
			r1 = self.s.get(l1_req, headers=self.headers)
			r1 = json.loads(r1.text)
			d1 = r1['data']
			if not d1:
				print('获取评论失败...Break')
				return 
			for each in d1:
				item1 = self.extract_comment(each)
				l1_id = item1['id']
				has_child = each['total_number']
				if has_child > 0:
					self.get_child_comment(l1_id=l1_id)
				self.comments.append(item1)
			max_id = r1['max_id']
		except Exception as e:
			print(e)
		if max_id != 0:
			print('Total count %s L1 Continue SCROLLING... ...' % len(self.comments))
			return self.get_comment(max_id=max_id)
			
	def get_child_comment(self, l1_id, max_id=0):
		try:
			l2_req = self.l2_comment_api.format(l1_id=l1_id, max_id=max_id)
			time.sleep(random.randint(0,3))
			s2= self.s.get(l2_req, headers=self.headers)
			r2 = json.loads(s2.text)
			d2 = r2['data']
			if not d2:
				return
			for each in d2:
				item2 = self.extract_comment(each)
				self.comments.append(item2)
			max_id = r2['max_id']
		except Exception as e:
			print(e)
		if max_id != 0:
			print('Total count %s L2 Continue SCROLLING... ...' %len(self.comments))
			return self.get_child_comment(l1_id=l1_id,max_id=max_id)
		
	def extract_comment(self, data):
		author_name = data['user']['name']
		id_ = data['id']
		time_str = data['created_at'].replace('+0800 ', '')
		post_time = dateparser.parse(time_str)
		like_num = data['like_counts']
		content = data['text_raw']
		return {
			"id": id_,
			"url": self.url,
			"author_name": author_name,
			"post_time": post_time,
			"content": content,
			"like_num": like_num
		}

if __name__ == '__main__':
	t = WeiboComment('4689423801253985')
	comment = t.get_comment()