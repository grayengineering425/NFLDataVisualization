import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
        
def read_nfl_game_csv():
    games = pd.read_csv('../NFLScraper/games.csv')
    print('Max Visitor Score: ', games['visitor_score'].max())
    print('Max Home Score: ', games['home_score'].max())
    print('Total Jets Games: ', games[games['visitor'] == 'New York Jets']['visitor'].count() + games[games['home'] == 'New York Jets']['home'].count())

def main():
    read_nfl_game_csv()

if __name__ == "__main__":
    main()
