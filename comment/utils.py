#encoding=utf8
import re

try:
	from .toutiao import ToutiaoComment
	from .weibo import WeiboComment
except ImportError:
	from toutiao import ToutiaoComment
	from weibo import WeiboComment

from urllib.parse import urlparse

supported_domain_expression = {
	"www.toutiao.com": ['/a(\d+)/?.*'],
	"weibo.com": ['/\d+/(\w+)']
}

def check_validation(url):
	"""
	域名和链接检查
	"""
	domain = urlparse(url).netloc
	expre_list = supported_domain_expression.get(domain)
	if expre_list:
		for each in expre_list:
			post_id = re.search(each, url)
			if post_id:
				post_id = post_id.group(1)
				return {"message": "链接有效", "post_id": post_id, "domain": domain, 'url': url}
			else:
				return {"message": "x.x 链接格式错误 x.x", "url": url}
	else:
		return {"message": "x.x 该域名%s暂不支持 x.x" %(domain), "url": url}
		

def get_comment(data: dict):
	map_ = {
		"www.toutiao.com": ToutiaoComment,
		"weibo.com": WeiboComment
	}
	if data.get('domain'):
		t = map_[data['domain']]
		t(data['post_id'], data['url']).get_comment()
		return t.comments
	

if __name__ == '__main__':
	#info = (check_validation('https://www.toutiao.com/a7029929014202630687/?log_from=39cf6cf11248b_1636861144204'))
	info = (check_validation('https://weibo.com/1853098262/KBwjW5gdz'))
	comments = get_comment(info)