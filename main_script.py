# encoding=utf-8
"""
直接将评论写入到Excel
"""
from comment.utils import get_comments, check_validation
import pandas as pd

def get_url():
	with open('w.txt', 'r') as f:
		for line in f.readlines():
			line = line.strip('\n').strip()
			yield line

for each in get_url():
	info = (check_validation(each))
	print(info)
	comments = get_comments(info)
	pf = pd.DataFrame(comments)
	order = ['url', 'author_name', 'post_time', 'content', 'like_num']
	columns_map = {'url': '链接' , 'author_name': '作者名', 'post_time': '评论时间', 'content': '内容', 'like_num': '点赞数' }
	pf.rename(columns=columns_map, inplace=True)
	pf.to_csv('weibo3.csv', mode='a', header=False)