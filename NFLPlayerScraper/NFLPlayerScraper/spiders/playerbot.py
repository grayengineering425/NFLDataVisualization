# -*- coding: utf-8 -*-
import scrapy
from string import ascii_lowercase
import csv

class PlayerbotSpider(scrapy.Spider):
    name = 'playerbot'
    start_url = 'http://www.footballdb.com/players/current.html?pos='
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'P']

    def start_requests(self):
        for position in self.positions:
            yield scrapy.Request(url=self.start_url+position, callback=self.parse)
    
    def parse(self, response):
        playerTable = response.xpath('//table[@class = "statistics"]')

        for player in playerTable.xpath('.//tr'):
            playerName      = player.xpath('.//td/a/text()')        .extract_first()
            playerPosition  = player.xpath('.//td[2]/text()')       .extract_first()
            playerTeam      = player.xpath('.//td[3]/span/a/text()').extract_first()
            playerCollege   = player.xpath('.//td[4]/text()')       .extract_first()
            
            playerResult = {
                'player_name'     : playerName,
                'player_position' : playerPosition,
                'player_team'     : playerTeam,
                'player_college'  : playerCollege,
            }
            fileName = str(playerName).replace(', ', '_')+'.csv'
            print(fileName)
            with open('players/'+fileName, 'w') as player_csv:
                writer = csv.writer(player_csv)
                writer.writerow(['date','passAtt','passCmp','passYds','passYPA','passTD','interceptions','passLG',
                                 'sack','loss','rate','rushAtt','rushYds','rushAvg','rushLg','rushTD','rushFirstDowns',
                                 'rec','recYds','recAvg','recLg','recTD','recFirstDowns','YAC','numPuntReturns','puntReturnYds',
                                 'avgPuntReturn','puntFC','puntLg','puntTD','kickReturns','kickReturnYds','kickreturnAvg',
                                 'kickFC','kickLG','kickTD','fum','lost','forced','own','opp','tot','yds','fumTD'])
                
        
