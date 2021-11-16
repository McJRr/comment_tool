from scrapy.item import Item, Field


class CommentItem(Item):
	id = Field()
	like_num = Field()
	author_name = Field()
	content = Field()
	post_time = Field()
	url = Field()