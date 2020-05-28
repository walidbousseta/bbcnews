"""
this project it's about scrape the bbc news web site using the scrapy package
after scraping the content of the web site the data will be uploaded into MongoDb
after name BBCNews in table news.
"""

from numpy import unique
import scrapy
from ..items import BbcnewsItem

class BBCNews(scrapy.Spider):
	name = 'bbcnews' # this is the name we call in the command line to scrape the url content
	start_urls = ['https://www.bbc.com/'] # here's the url we want to scrape
	allowed_domains = ['bbc.com'] # use for not go into other website (avoiding to go to the shared urls)
	custom_settings = {
        'DOWNLOAD_TIMEOUT': '200', # I use this to avoid the timeout error 
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36', # use this value to avoid the socket error it's may cause an error you can try to remove it if the script not workin for you
    }

    # this is the imporatant method here we do the magic
	def parse(self, response):
		# here I get the part in html response content the data we want by the xpath
		news = response.xpath('//'+self.get_xpath('media__content'))
		# in each media content get the following data
		for content in news:
			# items here is to simple upload the data into database
			items = BbcnewsItem()
			# here we extrcat the article title and clean it from additionnel whitespaces and new lines
			items['title'] = self.get_first(content.xpath(self.get_xpath('media__title')+'/a/text()').extract()).strip(' \n')
			# we do same for summary as title
			items['summary'] = self.get_first(content.xpath(self.get_xpath('media__summary')+'/text()').extract()).strip(' \n')
			# here we get the tags declare under the article summary 
			items['tags'] = content.xpath(self.get_xpath('media__tag')+'/text()').extract()
			# here we get the url to the article so we can scrape it's content
			article_url = ''.join(content.xpath(self.get_xpath('media__title')+'/a/@href').extract())
			url = response.urljoin(article_url)
			# here is were we go into the url to scrape 
			yield scrapy.Request(url, callback=self.parse_dir_contents, meta=items)

	# in this method we go to the url so we can scrape it
	def parse_dir_contents(self, response):
		# here we get the data we have scraped from previos page
		items = response.meta
		# when I check diff urls in the web site I found out that the content has diff classes for each type (news, sport, future, ...) I just take three like follow
		# we go to the first type for news if the header that we get is empty so we are in a diff type, so when we got an not empty header we know in which type we are and which values the body xpath should take:
		body_xpath = 'story-body__inner'
		header = self.get_first(response.xpath('//'+self.get_xpath('story-body__h1')+'/text()').extract()).strip(' \n')
		if header == "":
			header = self.get_first(response.xpath('//'+self.get_xpath('vxp-media__headline')+'/text()').extract()).strip(' \n')
			if header=="":
				header = self.get_first(response.xpath('//'+self.get_xpath('story-headline')+'/text()').extract()).strip(' \n')
				body_xpath = '*[@id="story-body"]'
			else:
				body_xpath = 'vxp-media__summary'

		# here we scrape all <p> content and concatente them into one text
		body_list = response.xpath('//'+self.get_xpath(body_xpath)+'//p/text()').extract()
		body = ' '.join(body_list).strip(' \n')

		# under the body content we found some related topics we get them with this code
		related = list(unique(response.xpath('//'+self.get_xpath('tags-container')+'//a/text()').extract()))
		# and in all the top we have the datetime of the article publish
		datetime = self.get_first(response.xpath('//'+self.get_xpath('mini-info-list__item')+'//@data-datetime').extract())

		# in the end we effect into each item his value and return the data
		items['header'] = header
		items['url'] = response.url
		items['body'] = body
		items['related'] = related
		items['datetime'] = datetime
		yield items

	# here we got the xpath syntax by only changing the class name
	def get_xpath(self, classname):
		return "*[contains(concat(' ', @class, ' '), ' " + classname + " ')]"

	# to avoid an empty list error I use this method to get the first item if the return not empty else return an emty string
	def get_first(self, _list):
		if len(_list)>0:
			return _list[0]
		else:
			return ""



