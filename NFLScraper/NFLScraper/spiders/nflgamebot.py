import scrapy

class NFLSpider(scrapy.Spider):
    name = "NFLGameSpider"
    start_urls = ['http://www.footballdb.com/games/index.html',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2016',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2015',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2014',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2013',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2012',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2011',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2010',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2009',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2008',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2007',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2006',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2005',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2004',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2003',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2002',
                  'http://www.footballdb.com/games/index.html?lg=NFL&yr=2001']

    def start_request(self):
        for start in start_urls:   
            yield scrapy.Request(url=start, callback=self.parse)
            
    def parse(self, response):
        for game in response.xpath('//tr'):
            link         = game.xpath('td/a/@href')       .extract_first()
            date         = game.xpath('td/span/text()')   .extract_first()
            visitor      = game.xpath('td[2]/span/text()').extract_first()
            visitorScore = game.xpath('td[3]/text()')     .extract_first()
            home         = game.xpath('td[4]/span/text()').extract_first()
            homeScore    = game.xpath('td[5]/text()')     .extract_first()

            if link and date and visitor and visitorScore and home and homeScore:
                scraped_info = {
                    'date'          : date,
                    'visitor'       : visitor,
                    'visitor_score' : visitorScore,
                    'home'          : home,
                    'home_score'    : homeScore,
                    'link'          : link,
                }
                yield scraped_info
