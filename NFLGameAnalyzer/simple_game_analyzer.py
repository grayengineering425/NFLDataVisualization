import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import string

months = { 'January'   : '1',
           'February'  : '2',
           'March'     : '3',
           'April'     : '4',
           'May'       : '5',
           'June'      : '6',
           'July'      : '7',
           'August'    : '8',
           'September' : '9',
           'October'   : '10',
           'November'  : '11',
           'December'  : '12',
    }

def convertDate(date):
    dateNoPunc = date.replace(',', '')
    splitDate = dateNoPunc.split()
    
    newDate = ''
    i=0
    
    for d in splitDate:
        if i == 0:
            newDate += months[d]
        else:
            newDate += d
            
        if i != 2:
            newDate += '-'
        i += 1
        
    return newDate
    
def read_nfl_game_csv():
    games = pd.read_csv('../NFLScraper/games.csv')
    print('Max Visitor Score: ', games['visitor_score'].max())
    print('Max Home Score: ', games['home_score'].max())
    print('Total Jets Games: ', games[games['visitor'] == 'New York Jets']['visitor'].count() + games[games['home'] == 'New York Jets']['home'].count())

    brady = pd.read_csv('../NFLPlayerScraper/players/Brady_Tom.csv')
    brady['date'] = brady['date'].apply(lambda x : convertDate(x))
    brady['date'] = pd.to_datetime(brady['date'], format='%m-%d-%Y')
    brady = brady.sort_values(by = 'date', ascending = True)
    
    brady_dolphins = brady[brady['opponent'] == 'Miami']
    brady_dolphins.plot(x='date', y=['passYds', 'rate'], kind='bar')

    plt.tight_layout()
    plt.show()
    
def main():
    read_nfl_game_csv()

if __name__ == "__main__":
    main()
