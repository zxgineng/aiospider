from lxml import html

from frame import Request, Item, Spider


class DoubanItem(Item):
    row = ["rank", 'name', 'score']


class DoubanSpider(Spider):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

    def first_request(self):
        url = 'https://movie.douban.com/top250'
        yield Request(url=url, call_back=self.parse, headers=self.headers)

    def parse(self, response):
        item = DoubanItem()
        tree = html.fromstring(response.content.decode())
        movies = tree.xpath('//ol[@class="grid_view"]/li')
        for m in movies:
            item['rank'] = m.xpath(
                './/div[@class="pic"]/em/text()')[0]
            item['name'] = m.xpath(
                './/div[@class="hd"]/a/span[1]/text()')[0]
            item['score'] = m.xpath(
                './/div[@class="star"]/span[@class="rating_num"]/text()'
            )[0]
            print(item['name'])
            yield item

        next_url = tree.xpath('//span[@class="next"]/a/@href')

        if next_url:
            next_url = 'https://movie.douban.com/top250' + next_url[0]
            yield Request(url=next_url, call_back=self.parse, headers=self.headers)


if __name__ == "__main__":
    s = DoubanSpider()
    s.run()
