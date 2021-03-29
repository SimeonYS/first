import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FirstItem
from itemloaders.processors import TakeFirst
import json
pattern = r'(\xa0)?'

class FirstSpider(scrapy.Spider):
	name = 'first'
	page = 1
	base = 'https://www.firstfoundationinc.com/api/expertise/results?_limit=10&_page={}&type=insight,press-release'
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['results'])):
			link = data['results'][index]['url']
			date = data['results'][index]['date']
			extensions = ['.mp3', '.pdf']
			if not any(file in link for file in extensions):
				yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))

		if not self.page == data['meta']['totalPages']:
			self.page += 1
			yield response.follow(self.base.format(self.page), self.parse)


	def parse_post(self, response, date):

		title = response.xpath('//span[@class="field field--name-title field--type-string field--label-hidden"]//text() | //span[@id="hs_cos_wrapper_name"]//text() | //span[@id="_ctrl0_ctl54_lblModuleDetailHeadline"]/text() | //h1/text() |//div[@class="standard-hero-title"]/text()').get()
		content = response.xpath('//span[@id="hs_cos_wrapper_post_body"]//text()[not (ancestor::blockquote)] | //div[@class="q4default"]//text()[not (ancestor::div[@class="bw-contact-info-wrapper"])] | //article[@class="expertise-detail-content"]//text() | //div[@class="polaris__simple-grid--main"][2]//text() |//div[@class="hs_cos_wrapper hs_cos_wrapper_widget hs_cos_wrapper_type_rich_text"]//text() |//div[@class="module_body"]//text()|//div[@class="polaris__simple-grid--main"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FirstItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
