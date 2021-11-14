import json
import requests
import time
# import logging
import traceback
import random

# logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',level=	print)
# LOGGER = logging.getLogger(__name__)

class ToutiaoComment():
	l1_comment_api = 'https://www.toutiao.com/article/v2/tab_comments/?' \
		'aid=24&app_name=toutiao_web&offset={offset}&count=20&group_id={post_id}'
	l2_comment_api = 'https://www.toutiao.com/2/comment/v2/reply_list/?' \
		'aid=24&app_name=toutiao_web&id={l1_id}&offset={offset}&count=20&repost=0'
	headers = {
		"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
	}

	comments = []

	def __init__(self, post_id, url) -> None:
		self.s = requests.Session()
		print('Get Toutiao ID %s ' % post_id)
		self.post_id = post_id
		self.url = url

	def get_comment(self, offset=0):
		try:
			time.sleep(random.randint(0,3))
			l1_req = self.l1_comment_api.format(offset=offset,post_id=self.post_id)
			#	print('Request %s ...' % l1_req)
			r1 = self.s.get(l1_req, headers=self.headers)
			r1 = json.loads(r1.text)
			d1 = r1['data']
			if not d1:
				return 
			for each in d1:
				item1 = self.extract_comment(each)
				l1_id = item1['id']
				has_child = each['comment']['reply_count']
				if has_child > 0:
					self.get_child_comment(l1_id=l1_id)
				self.comments.append(item1)
			has_more = r1.get('has_more')
		except Exception:
			traceback.print_exc()
		print('Total count %s L1 Continue SCROLLING... ....' % len(self.comments))
		if has_more:
			offset = r1['offset']
			return self.get_comment(offset=offset)
			
	def get_child_comment(self, l1_id, offset=0):
		l2_req = self.l2_comment_api.format(l1_id=l1_id, offset=offset)
		time.sleep(0.5)
		s2= self.s.get(l2_req, headers=self.headers)
		r2 = json.loads(s2.text)['data']
		d2 = r2['data']
		if not d2:
			return
		for each in d2:
			item2 = self.extract_comment(each)
			self.comments.append(item2)
		has_more = r2.get('has_more')
		if has_more:
			print('Total count %s  L2 Continue SCROLLING...  ....' % len(self.comments))
			offset = r2['offset']
			return self.get_child_comment(l1_id,offset=offset)
		
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
		return {
			"id": id_,
			"url": self.url,
			"author_name": author_name,
			"post_time": post_time,
			"content": content,
			"like_num": like_num
		}

if __name__ == '__main__':
	t = ToutiaoComment('7029929014202630687')
	comment = t.get_comment()