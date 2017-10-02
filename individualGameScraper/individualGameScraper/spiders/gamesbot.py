# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import csv
from .offensivePlayerGame import OffensivePlayerGame

def getFileFromName(name):
    firstLastName = name.split()
    fileName = firstLastName[1] + '_' + firstLastName[0] + '.csv'
    return fileName

    
class GamesbotSpider(scrapy.Spider):
    name = 'gamesbot'
    start_url = 'http://www.footballdb.com'
    games = pd.read_csv('../NFLScraper/games.csv')
    links = games['link']
    date = ''
    home = ''
    visitor = ''
    players = {}

    def start_requests(self):
        for link in self.links:
            yield scrapy.Request(url=self.start_url+link, callback=self.parse)
            
    def parse(self, response):
        self.players.clear()

        #parsing box score from website
        teamStats                = response        .xpath('//div[contains(@id, "divBox_team")]')
        
        leftTable                = teamStats       .xpath('.//div[@class = "section_left"]')
        leftTableBody            = leftTable       .xpath('.//tbody')
                
        rightTable               = teamStats       .xpath('.//div[@class = "section_right"]')
        rightTableBody           = rightTable      .xpath('.//tbody')
        
        #parsing tables for individual player statistics
        playerStats              = response        .xpath('//div[@id = "divBox_stats"]')
        
        passerDiv                = playerStats     .xpath('.//div[@class = "table-responsive"][1]')
        passerTable              = passerDiv       .xpath('.//table[@class = "statistics"]')
        
        rusherDiv                = playerStats     .xpath('.//div[@class = "table-responsive"][2]')
        rusherTable              = rusherDiv       .xpath('.//table[@class = "statistics"]')

        receiverDiv              = playerStats     .xpath('.//div[@class = "table-responsive"][3]')
        receiverTable            = receiverDiv     .xpath('.//table[@class = "statistics"]')

        kickoffReturnDiv         = playerStats     .xpath('.//div[@class = "table-responsive"][4]')
        kickoffReturnTable       = kickoffReturnDiv.xpath('.//table[@class = "statistics"]')

        puntReturnDiv		 = playerStats     .xpath('.//div[@class = "table-responsive"][5]')
        puntReturnTable          = puntReturnDiv   .xpath('.//table[@class = "statistics"]')

        kickingDiv		 = playerStats     .xpath('.//div[@class = "table-responsive"][7]')
        kickingTable             = kickingDiv      .xpath('.//table[@class = "statistics"]')

        defenseDiv		 = playerStats     .xpath('.//div[@class = "table-responsive"][9]')
        defenseTable             = defenseDiv      .xpath('.//table[@class = "statistics"]')

        fumblesDiv		 = playerStats     .xpath('.//div[@class = "table-responsive"][10]')
        fumblesTable             = fumblesDiv      .xpath('.//table[@class = "statistics"]')

        currentDate              = response        .xpath('//div[@id = "leftcol"]/center/div/text()').extract_first()
        currentVisitor           = response        .xpath('//button[@id = "btnBox_visitor"]/text()') .extract_first()
        currentHome              = response        .xpath('//button[@id = "btnBox_home"]/text()')    .extract_first()
        

        visitor = True
        count = 0
        for passer in passerTable.xpath('.//tr'):            
            playerName   = passer.xpath('.//td[1]/span/a/text()').extract_first()
            passAttempts = passer.xpath('.//td[2]/text()')       .extract_first()
            passComp     = passer.xpath('.//td[3]/text()')       .extract_first()
            passYds      = passer.xpath('.//td[4]/text()')       .extract_first()
            passAvg      = passer.xpath('.//td[5]/text()')       .extract_first()
            passTD       = passer.xpath('.//td[6]/text()')       .extract_first()
            passInt      = passer.xpath('.//td[7]/text()')       .extract_first()
            passLg       = passer.xpath('.//td[8]/text()')       .extract_first()
            sacks        = passer.xpath('.//td[9]/text()')       .extract_first()
            loss         = passer.xpath('.//td[10]/text()')      .extract_first()
            rate         = passer.xpath('.//td[11]/text()')      .extract_first()

            if passAttempts != 'Att':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)
                
                self.players[playerName].passAtt       = int(passAttempts)
                self.players[playerName].passCmp       = int(passComp)
                self.players[playerName].passYds       = int(passYds)
                self.players[playerName].passYPA       = float(passAvg)
                self.players[playerName].passTD        = int(passTD)
                self.players[playerName].interceptions = int(passInt)
                self.players[playerName].passLG        = passLg
                self.players[playerName].sack          = int(sacks)
                self.players[playerName].loss          = int(loss)
                self.players[playerName].rate          = float(rate)

            else:
                count += 1
                if count == 2:
                    visitor = False

        visitor = True
        count = 0
        for rusher in rusherTable.xpath('.//tr'):
            playerName   = rusher.xpath('.//td[1]/span/a/text()').extract_first()
            rushAtt      = rusher.xpath('.//td[2]/text()')       .extract_first()
            rushYds      = rusher.xpath('.//td[3]/text()')       .extract_first()
            rushAvg      = rusher.xpath('.//td[4]/text()')       .extract_first()
            rushLg       = rusher.xpath('.//td[5]/text()')       .extract_first()
            rushTD       = rusher.xpath('.//td[6]/text()')       .extract_first()
            rushFD       = rusher.xpath('.//td[7]/text()')       .extract_first()

            if rushAtt != 'Att':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)
                    
                self.players[playerName].rushAtt        = int(rushAtt)
                self.players[playerName].rushYds        = rushYds
                self.players[playerName].rushAvg        = float(rushAvg)
                self.players[playerName].rushLg         = rushLg
                self.players[playerName].rushTD         = int(rushTD)
                self.players[playerName].rushFirstDowns = int(rushFD)

            else:
                count += 1
                if count == 2:
                    visitor = False

        visitor = True
        count = 0
        for receiver in receiverTable.xpath('.//tr'):
            playerName = receiver.xpath('.//td[1]/span/a/text()').extract_first()
            rec        = receiver.xpath('.//td[2]/text()')       .extract_first()
            yds        = receiver.xpath('.//td[3]/text()')       .extract_first()
            avg        = receiver.xpath('.//td[4]/text()')       .extract_first()
            lg         = receiver.xpath('.//td[5]/text()')       .extract_first()
            td         = receiver.xpath('.//td[6]/text()')       .extract_first()
            fd         = receiver.xpath('.//td[7]/text()')       .extract_first()

            if rec != 'Rec':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)

                self.players[playerName].rec           = int(rec)
                self.players[playerName].recYds        = int(yds)
                self.players[playerName].recAvg        = float(avg)
                self.players[playerName].recLg         = lg
                self.players[playerName].recTD         = int(td)
                self.players[playerName].recFirstDowns = int(fd)

            else:
                count += 1
                if count == 2:
                    visitor = False

        visitor = True
        count = 0
        for kickoffReturner in kickoffReturnTable.xpath('.//tr'):
            playerName = kickoffReturner.xpath('.//td[1]/span/a/text()').extract_first()
            num        = kickoffReturner.xpath('.//td[2]/text()')       .extract_first()
            yds        = kickoffReturner.xpath('.//td[3]/text()')       .extract_first()
            avg        = kickoffReturner.xpath('.//td[4]/text()')       .extract_first()
            fc         = kickoffReturner.xpath('.//td[5]/text()')       .extract_first()
            lg         = kickoffReturner.xpath('.//td[6]/text()')       .extract_first()
            td         = kickoffReturner.xpath('.//td[7]/text()')       .extract_first()

            if num != 'Num':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)

                self.players[playerName].kickReturns   = int(num)
                self.players[playerName].kickReturnYds = int(yds)
                self.players[playerName].kickReturnAvg = float(avg)
                self.players[playerName].kickFC        = int(fc)
                self.players[playerName].kickLG        = lg
                self.players[playerName].kickTD        = int(td)

            else:
                count += 1
                if count == 2:
                    visitor = False
                    
        visitor = True
        count = 0
        for puntReturner in puntReturnTable.xpath('.//tr'):
            playerName = puntReturner.xpath('.//td[1]/span/a/text()').extract_first()
            num        = puntReturner.xpath('.//td[2]/text()')       .extract_first()
            yds        = puntReturner.xpath('.//td[3]/text()')       .extract_first()
            avg        = puntReturner.xpath('.//td[4]/text()')       .extract_first()
            fc         = puntReturner.xpath('.//td[5]/text()')       .extract_first()
            lg         = puntReturner.xpath('.//td[6]/text()')       .extract_first()
            td         = puntReturner.xpath('.//td[7]/text()')       .extract_first()

            if num != 'Num':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)

                self.players[playerName].puntReturns   = int(num)
                self.players[playerName].puntReturnYds = int(yds)
                self.players[playerName].puntReturnAvg = float(avg)
                self.players[playerName].puntFC        = int(fc)
                self.players[playerName].puntLG        = lg
                self.players[playerName].puntTD        = int(td)

            else:
                count += 1
                if count == 2:
                    visitor = False
                
        #for kicker in kickingTable.xpath('.//tr'):
        #    playerName = kicker.xpath('.//td[1]/span/a/text()').extract_first()
        
        #for defender in defenseTable.xpath('.//tr'):
         #   playerName = defender.xpath('.//td[1]/span/a/text()').extract_first()

        visitor = True
        count = 0
        for fumbler in fumblesTable.xpath('.//tr'):
            fumblerName = fumbler.xpath('.//td[1]/span/a/text()').extract_first()
            fum         = fumbler.xpath('.//td[2]/text()')       .extract_first()
            lost        = fumbler.xpath('.//td[3]/text()')       .extract_first()
            forced      = fumbler.xpath('.//td[4]/text()')       .extract_first()
            own         = fumbler.xpath('.//td[5]/text()')       .extract_first()
            opp         = fumbler.xpath('.//td[6]/text()')       .extract_first()
            tot         = fumbler.xpath('.//td[7]/text()')       .extract_first()
            yds         = fumbler.xpath('.//td[8]/text()')       .extract_first()
            td          = fumbler.xpath('.//td[9]/text()')       .extract_first()

            if fum != 'Fum':
                if playerName not in self.players.keys():
                    if visitor:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentHome)
                    else:
                        self.players[playerName] = OffensivePlayerGame(playerName, currentVisitor)

                self.players[playerName].fum    = int(fum)
                self.players[playerName].lost   = int(lost)
                self.players[playerName].forced = int(forced)
                self.players[playerName].own    = int(own)
                self.players[playerName].opp    = int(opp)
                self.players[playerName].tot    = int(tot)
                self.players[playerName].yds    = int(yds)
                self.players[playerName].fumTD  = int(td)

            else:
                count += 1
                if count == 2:
                    visitor = False
        
        visitorFirstDowns        = leftTableBody.xpath('.//tr[1]/td[2]/text()')  .extract_first()
        visitorRushingFirstDowns = leftTableBody.xpath('.//tr[2]/td[2]/text()')  .extract_first()
        visitorPassingFirstDowns = leftTableBody.xpath('.//tr[3]/td[2]/text()')  .extract_first()
        visitorPenalties         = leftTableBody.xpath('.//tr[4]/td[2]/text()')  .extract_first()
        visitorNetYards          = leftTableBody.xpath('.//tr[5]/td[2]/text()')  .extract_first()
        visitorNetYardsRushing   = leftTableBody.xpath('.//tr[6]/td[2]/text()')  .extract_first()
        visitorRushingPlays      = leftTableBody.xpath('.//tr[7]/td[2]/text()')  .extract_first()
        visitorAverageRush       = leftTableBody.xpath('.//tr[8]/td[2]/text()')  .extract_first()
        visitorNetYardsPassing   = leftTableBody.xpath('.//tr[9]/td[2]/text()')  .extract_first()
        visitorPassingSplits     = leftTableBody.xpath('.//tr[10]/td[2]/text()') .extract_first()
        visitorSackSplits        = leftTableBody.xpath('.//tr[11]/td[2]/text()') .extract_first()
        visitorGrossPassing      = leftTableBody.xpath('.//tr[12]/td[2]/text()') .extract_first()
        visitorYardsPerPass      = leftTableBody.xpath('.//tr[13]/td[2]/text()') .extract_first()

        homeFirstDowns        	 = leftTableBody.xpath('.//tr[1]/td[3]/text()')  .extract_first()
        homeRushingFirstDowns 	 = leftTableBody.xpath('.//tr[2]/td[3]/text()')  .extract_first()
        homePassingFirstDowns 	 = leftTableBody.xpath('.//tr[3]/td[3]/text()')  .extract_first()
        homePenalties         	 = leftTableBody.xpath('.//tr[4]/td[3]/text()')  .extract_first()
        homeNetYards          	 = leftTableBody.xpath('.//tr[5]/td[3]/text()')  .extract_first()
        homeNetYardsRushing   	 = leftTableBody.xpath('.//tr[6]/td[3]/text()')  .extract_first()
        homeRushingPlays      	 = leftTableBody.xpath('.//tr[7]/td[3]/text()')  .extract_first()
        homeAverageRush       	 = leftTableBody.xpath('.//tr[8]/td[3]/text()')  .extract_first()
        homeNetYardsPassing   	 = leftTableBody.xpath('.//tr[9]/td[3]/text()')  .extract_first()
        homePassingSplits     	 = leftTableBody.xpath('.//tr[10]/td[3]/text()') .extract_first()
        homeSackSplits        	 = leftTableBody.xpath('.//tr[11]/td[3]/text()') .extract_first()
        homeGrossPassing      	 = leftTableBody.xpath('.//tr[12]/td[3]/text()') .extract_first()
        homeYardsPerPass      	 = leftTableBody.xpath('.//tr[13]/td[3]/text()') .extract_first()

        visitorPuntSplitsAvg     = rightTableBody.xpath('.//tr[1]/td[2]/text()') .extract_first()
        visitorPuntsBlocked	 = rightTableBody.xpath('.//tr[2]/td[2]/text()') .extract_first()
        visitorPuntReturnSplits  = rightTableBody.xpath('.//tr[3]/td[2]/text()') .extract_first()
        visitorKickReturnSplits  = rightTableBody.xpath('.//tr[4]/td[2]/text()') .extract_first()
        visitorIntReturnSplits   = rightTableBody.xpath('.//tr[5]/td[2]/text()') .extract_first()
        visitorPenaltySplits     = rightTableBody.xpath('.//tr[6]/td[2]/text()') .extract_first()
        visitorFumbleSplits      = rightTableBody.xpath('.//tr[7]/td[2]/text()') .extract_first()
        visitorFieldGoals        = rightTableBody.xpath('.//tr[8]/td[2]/text()') .extract_first()
        visitorThirdDownSplits   = rightTableBody.xpath('.//tr[9]/td[2]/text()') .extract_first()
        visitorFourthDownSplits  = rightTableBody.xpath('.//tr[10]/td[2]/text()').extract_first()
        visitorTotalPlays        = rightTableBody.xpath('.//tr[11]/td[2]/text()').extract_first()
        visitorAvgGain	         = rightTableBody.xpath('.//tr[12]/td[2]/text()').extract_first()
        visitorTimeOfPossession  = rightTableBody.xpath('.//tr[13]/td[2]/text()').extract_first()

        homePuntSplitsAvg     	 = rightTableBody.xpath('.//tr[1]/td[3]/text()') .extract_first()
        homePuntsBlocked	 = rightTableBody.xpath('.//tr[2]/td[3]/text()') .extract_first()
        homePuntReturnSplits  	 = rightTableBody.xpath('.//tr[3]/td[3]/text()') .extract_first()
        homeKickReturnSplits  	 = rightTableBody.xpath('.//tr[4]/td[3]/text()') .extract_first()
        homeIntReturnSplits   	 = rightTableBody.xpath('.//tr[5]/td[3]/text()') .extract_first()
        homePenaltySplits     	 = rightTableBody.xpath('.//tr[6]/td[3]/text()') .extract_first()
        homeFumbleSplits      	 = rightTableBody.xpath('.//tr[7]/td[3]/text()') .extract_first()
        homeFieldGoals        	 = rightTableBody.xpath('.//tr[8]/td[3]/text()') .extract_first()
        homeThirdDownSplits   	 = rightTableBody.xpath('.//tr[9]/td[3]/text()') .extract_first()
        homeFourthDownSplits  	 = rightTableBody.xpath('.//tr[10]/td[3]/text()').extract_first()
        homeTotalPlays        	 = rightTableBody.xpath('.//tr[11]/td[3]/text()').extract_first()
        homeAvgGain	         = rightTableBody.xpath('.//tr[12]/td[3]/text()').extract_first()
        homeTimeOfPossession  	 = rightTableBody.xpath('.//tr[13]/td[3]/text()').extract_first()

        teamStats = {
            'visitor_first_downs'           : visitorFirstDowns,
            'visitor_rushing_first_downs'   : visitorRushingFirstDowns,
            'visitor_passing_first_downs'   : visitorPassingFirstDowns,
            'visitor_penalties'             : visitorPenalties,
            'visitor_net_yards'             : visitorNetYards,
            'visitor_net_yards_rushing'     : visitorNetYardsRushing,
            'visitor_rushing_plays'         : visitorRushingPlays,
            'visitor_avg_rush'              : visitorAverageRush,
            'visitor_net_yards_passing'     : visitorNetYardsPassing,
            'visitor_passing_splits'        : visitorPassingSplits,
            'visitor_sack_splits'           : visitorSackSplits,
            'visitor_gross_passing'         : visitorGrossPassing,
            'visitor_yards_per_pass'        : visitorYardsPerPass,
            'visitor_punt_splits_avg'	    : visitorPuntSplitsAvg,
            'visitor_punts_blocked'         : visitorPuntsBlocked, 	
            'visitor_punt_return_splits'    : visitorPuntReturnSplits,
            'visitor_kick_return_splits'    : visitorKickReturnSplits,
            'visitor_int_return_splits'	    : visitorIntReturnSplits, 
            'visitor_penalty_splits'	    : visitorPenaltySplits,   
            'visitor_fumble_splits'	    : visitorFumbleSplits,   
            'visitor_field_goals'           : visitorFieldGoals,      
            'visitor_third_down_splits'     : visitorThirdDownSplits, 
            'visitor_fourth_down_splits'    : visitorFourthDownSplits,
            'visitor_total_plays'           : visitorTotalPlays,      
            'visitor_avg_gain'              : visitorAvgGain,	       
            'visitor_time_of_possession'    : visitorTimeOfPossession, 
            'home_first_downs'              : homeFirstDowns,
            'home_rushing_first_downs'      : homeRushingFirstDowns,
            'home_passing_first_downs'      : homePassingFirstDowns,
            'home_penalties'                : homePenalties,
            'home_net_yards'                : homeNetYards,
            'home_net_yards_rushing'        : homeNetYardsRushing,
            'home_rushing_plays'            : homeRushingPlays,
            'home_avg_rush'                 : homeAverageRush,
            'home_net_yards_passing'        : homeNetYardsPassing,
            'home_passing_splits'           : homePassingSplits,
            'home_sack_splits'              : homeSackSplits,
            'home_gross_passing'            : homeGrossPassing,
            'home_yards_per_pass'           : homeYardsPerPass,
            'home_punt_splits_avg'	    : homePuntSplitsAvg,
            'home_punts_blocked'            : homePuntsBlocked, 	
            'home_punt_return_splits'	    : homePuntReturnSplits,
            'home_kick_return_splits'	    : homeKickReturnSplits,
            'home_int_return_splits'	    : homeIntReturnSplits, 
            'home_penalty_splits'	    : homePenaltySplits,   
            'home_fumble_splits'	    : homeFumbleSplits,   
            'home_field_goals'              : homeFieldGoals,      
            'home_third_down_splits'        : homeThirdDownSplits, 
            'home_fourth_down_splits'       : homeFourthDownSplits,
            'home_total_plays'              : homeTotalPlays,      
            'home_avg_gain'                 : homeAvgGain,	       
            'home_time_of_possession'       : homeTimeOfPossession, 
        }

        for key in self.players:
            fileName = getFileFromName(key)
            playerFolder = '../NFLPlayerScraper/players/'
            playerFile = open(playerFolder+fileName, 'a')
            if (playerFile):
               writer = csv.writer(playerFile)
               writer.writerow([currentDate                          ,
                                    self.players[key].opponent       ,
                                    self.players[key].passAtt        ,
				    self.players[key].passCmp        ,
				    self.players[key].passYds        ,
				    self.players[key].passYPA        ,
				    self.players[key].passTD         ,
				    self.players[key].interceptions  ,
				    self.players[key].passLG         ,
				    self.players[key].sack           ,
				    self.players[key].loss           ,
				    self.players[key].rate           ,
				    self.players[key].rushAtt        ,
				    self.players[key].rushYds        ,
				    self.players[key].rushAvg        ,
				    self.players[key].rushLg         ,
				    self.players[key].rushTD         ,
				    self.players[key].rushFirstDowns ,
				    self.players[key].rec            ,
				    self.players[key].recYds         ,
				    self.players[key].recAvg         ,
				    self.players[key].recLg          ,
				    self.players[key].recTD          ,
				    self.players[key].recFirstDowns  ,
				    self.players[key].YAC            ,
				    self.players[key].puntReturns    ,
				    self.players[key].puntReturnYds  ,
				    self.players[key].puntReturnAvg  ,
				    self.players[key].puntFC         ,
				    self.players[key].puntLG         ,
				    self.players[key].puntTD         ,
				    self.players[key].kickReturns    ,
				    self.players[key].kickReturnYds  ,
				    self.players[key].kickReturnAvg  ,
				    self.players[key].kickFC         ,
				    self.players[key].kickLG         ,
				    self.players[key].kickTD         ,
				    self.players[key].fum            ,
				    self.players[key].lost           ,
				    self.players[key].forced         ,
				    self.players[key].own            ,
				    self.players[key].opp            ,
				    self.players[key].tot            ,
				    self.players[key].yds            ,
				    self.players[key].fumTD
                                ])
            playerFile.close()
        
        yield teamStats

