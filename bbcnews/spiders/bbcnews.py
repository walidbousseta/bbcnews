
import scrapy
from ..items import BbcnewsItem

class BBCNews(scrapy.Spider):
	name = 'bbcnews'
	start_urls = ['https://www.bbc.com/']

	

	def parse(self, response):
		news = response.xpath('//'+self.get_xpath('media__content'))[:3]
		# print('---'*45)
		# print(news)
		# print('---'*45)
		for content in news:
			items = BbcnewsItem()

			items['title'] = self.get_first(content.xpath(self.get_xpath('media__title')+'/a/text()').extract()).strip(' \n')
			items['summary'] = self.get_first(content.xpath(self.get_xpath('media__summary')+'/text()').extract()).strip(' \n')

			items['tags'] = self.get_first(content.xpath(self.get_xpath('media__tag')+'/text()').extract()).strip(' \n')

			article_url = ''.join(content.xpath(self.get_xpath('media__title')+'/a/@href').extract())
			url = response.urljoin(article_url)

			yield scrapy.Request(url, callback=self.parse_dir_contents, meta=items)

	def parse_dir_contents(self, response):
		items = response.meta
		# story = response.xpath(self.get_xpath('.story-body'))
		header = self.get_first(response.xpath('//'+self.get_xpath('story-body__h1')+'/text()').extract()).strip(' \n')

		body_list = response.xpath('//'+self.get_xpath('story-body__inner')+'//p/text()').extract()
		body = ' '.join(body_list).strip(' \n')

		items['header'] = header
		items['url'] = response.url
		items['body'] = body
		yield items

	def clean(self, txt):
		return ' '.join(txt.split()).replace('\n', '')

	def get_xpath(self, classname):
		return "*[contains(concat(' ', @class, ' '), ' " + classname + " ')]"

	def get_first(self, _list):
		if len(_list)>0:
			return _list[0]
		else:
			return ""



