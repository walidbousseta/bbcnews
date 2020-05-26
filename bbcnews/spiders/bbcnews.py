

import scrapy


class BBCNews(scrapy.Spider):
	name = 'bbcnews'
	start_urls = ['https://www.bbc.com/']

	def parse(self, response):
		news = response.css('.media')[:3]
		for new in news:
			image = new.css('.media__image img::attr(src)').extract()
			content = new.css('.media__content')
			title = content.css('.media__title a::text').extract().trim()
			url = content.css('.media__title a::attr(href)').extract() 
			summary = content.css('.media__summary::text').extract().trim()
			tags = content.css('.media__tag::text').extract()

			yield {'image': image,
					'title': title,
					'url': url,
					'summary': summary,
					'tags': tags}



