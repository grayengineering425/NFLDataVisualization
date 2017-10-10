import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import string
from sklearn import preprocessing

pd.options.mode.chained_assignment = None

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

def getNumpyData(panda_frame, features, label):
    panda_frame['intercept'] = 1
    features = ['intercept'] + features
    features_frame = panda_frame[features]
    feature_matrix = features_frame.as_matrix()
    label_sarray = panda_frame[label]
    label_array = label_sarray.as_matrix()
    return(feature_matrix, label_array)

def predict_probability(feature_matrix, coefficients):
    dot = np.dot(feature_matrix, coefficients)
    predictions = 1/(1+np.exp(-dot))
    
    return predictions

def feature_derivative(errors, feature):
    derivative = np.dot(errors, feature)
    return derivative

def compute_log_likelihood(feature_matrix, winner, coefficients):
    indicator = (winner==+1)
    scores = np.dot(feature_matrix, coefficients)
    logexp = np.log(1. + np.exp(-scores))

    mask = np.isinf(logexp)
    logexp[mask] = -scores[mask]
        
    lp = np.sum((indicator-1)*scores - logexp)
    return lp

def logistic_regression(feature_matrix, winner, initial_coefficients, step_size, max_iter):
    coefficients = np.array(initial_coefficients)
    for itr in range(max_iter):
        predictions = predict_probability(feature_matrix, coefficients)
        indicator = (winner==+1)
        errors = indicator - predictions
        for j in range(len(coefficients)):
            derivative = feature_derivative(errors, feature_matrix[:,j])
            coefficients[j] += step_size*derivative
        if itr <= 15 or (itr <= 100 and itr % 10 == 0) or (itr <= 1000 and itr %100 == 0) or (itr <= 10000 and itr % 1000 == 0) or itr % 10000 == 0:
            lp = compute_log_likelihood(feature_matrix, winner, coefficients)
    return coefficients

#todo: apply to all seahawks data and start working on machine learning algorithm to predict games; (add last five games played against this opponent : only in certain timespan?),
#                                                                                                   (booleans for specific info, i.e. same QB, coaches, etc)#
def game_predictor():
    #reading all box scores
    games = pd.read_csv("../individualGameScraper/box_scores.csv")

    #extracting games in which only seattle has played
    seahawks_games = games[(games['visitor'] == 'Seattle') | (games['home'] == 'Seattle')]

    #creating new columns for hawks and opponent scores
    seahawks_games['hawks_score']                = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_score']            , seahawks_games['home_score']               )
    seahawks_games['hawks_first_downs']          = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_first_downs']      , seahawks_games['home_first_downs']         )
    seahawks_games['hawks_penalties']            = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_penalties']        , seahawks_games['home_penalties']           )

    seahawks_games['hawks_net_yards']            = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_net_yards']        , seahawks_games['home_net_yards']           )
    seahawks_games['hawks_net_yards_rushing']    = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_net_yards_rushing'], seahawks_games['home_net_yards_rushing']   )
    seahawks_games['hawks_net_yards_passing']    = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_net_yards_passing'], seahawks_games['home_net_yards_passing']   )
    seahawks_games['hawks_avg_gain']             = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['visitor_avg_gain']         , seahawks_games['home_avg_gain'])

    seahawks_games['opponent_score']             = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_score']               , seahawks_games['visitor_score']            )
    seahawks_games['opponent_first_downs']       = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_first_downs']         , seahawks_games['visitor_first_downs']      )
    seahawks_games['opponent_penalties']         = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_penalties']           , seahawks_games['visitor_penalties']        )
                                                                                                                                                
    seahawks_games['opponent_net_yards']         = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_net_yards']           , seahawks_games['visitor_net_yards']        )
    seahawks_games['opponent_net_yards_rushing'] = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_net_yards_rushing']   , seahawks_games['visitor_net_yards_rushing'])
    seahawks_games['opponent_net_yards_passing'] = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_net_yards_passing']   , seahawks_games['visitor_net_yards_passing'])
    seahawks_games['opponent_avg_gain']          = np.where(seahawks_games['visitor'] == 'Seattle', seahawks_games['home_avg_gain']            , seahawks_games['visitor_avg_gain']         )

    #finding which games in which seattle has won
    seahawks_games['winner'] = np.where(seahawks_games['hawks_score'] >= seahawks_games['opponent_score'], 1, -1)

    #sorting by date
    seahawks_games['date'] = seahawks_games['date'].apply(lambda x : convertDate(x))
    seahawks_games['date'] = pd.to_datetime(seahawks_games['date'], format='%m-%d-%Y')
    seahawks_games         = seahawks_games.sort_values(by = 'date', ascending = True)

    seahawks_games = seahawks_games.reset_index(drop=True)
    
    #creating test set
    test_set = seahawks_games

    #summizing data from last five games for each feature
    test_set['hawks_last_five_scores']               = 0
    test_set['hawks_last_five_first_downs']          = 0
    test_set['hawks_last_five_penalties']            = 0
    test_set['hawks_last_five_net_yards']            = 0
    test_set['hawks_last_five_net_yards_rushing']    = 0
    test_set['hawks_last_five_net_yards_passing']    = 0
    test_set['hawks_last_five_avg_gain']             = 0.0
	
    test_set['opponent_last_five_scores']            = 0
    test_set['opponent_last_five_first_downs']       = 0
    test_set['opponent_last_five_penalties']         = 0
    test_set['opponent_last_five_net_yards']         = 0
    test_set['opponent_last_five_net_yards_rushing'] = 0
    test_set['opponent_last_five_net_yards_passing'] = 0
    test_set['opponent_last_five_avg_gain']          = 0.0

    i = 0
    for index, row in test_set.iterrows():
        if i > 4:
            test_set.set_value(index, 'hawks_last_five_scores'                , test_set[i - 5:i]['hawks_score']               .sum())
            test_set.set_value(index, 'hawks_last_five_first_downs'           , test_set[i - 5:i]['hawks_first_downs']         .sum())
            test_set.set_value(index, 'hawks_last_five_penalties'             , test_set[i - 5:i]['hawks_penalties']           .sum())
            test_set.set_value(index, 'hawks_last_five_net_yards'             , test_set[i - 5:i]['hawks_net_yards']           .sum())
            test_set.set_value(index, 'hawks_last_five_net_yards_rushing'     , test_set[i - 5:i]['hawks_net_yards_rushing']   .sum())
            test_set.set_value(index, 'hawks_last_five_net_yards_passing'     , test_set[i - 5:i]['hawks_net_yards_passing']   .sum())
            test_set.set_value(index, 'hawks_last_five_avg_gain'              , test_set[i - 5:i]['hawks_avg_gain']            .sum())

            test_set.set_value(index, 'opponent_last_five_scores'             , test_set[i - 5:i]['opponent_score']            .sum())
            test_set.set_value(index, 'opponent_last_five_first_downs'        , test_set[i - 5:i]['opponent_first_downs']      .sum())
            test_set.set_value(index, 'opponent_last_five_penalties'          , test_set[i - 5:i]['opponent_penalties']        .sum())
            test_set.set_value(index, 'opponent_last_five_net_yards'          , test_set[i - 5:i]['opponent_net_yards']        .sum())
            test_set.set_value(index, 'opponent_last_five_net_yards_rushing'  , test_set[i - 5:i]['opponent_net_yards_rushing'].sum())
            test_set.set_value(index, 'opponent_last_five_net_yards_passing'  , test_set[i - 5:i]['opponent_net_yards_passing'].sum())
            test_set.set_value(index, 'opponent_last_five_avg_gain'           , test_set[i - 5:i]['opponent_avg_gain']         .sum())
            
        else:
            test_set.set_value(index, 'hawks_last_five_scores'                , 0)
            test_set.set_value(index, 'hawks_last_five_first_downs'           , 0)
            test_set.set_value(index, 'hawks_last_five_penalties'             , 0)
            test_set.set_value(index, 'hawks_last_five_net_yards'             , 0)
            test_set.set_value(index, 'hawks_last_five_net_yards_rushing'     , 0)
            test_set.set_value(index, 'hawks_last_five_net_yards_passing'     , 0)
            test_set.set_value(index, 'hawks_last_five_avg_gain'              , 0)

            test_set.set_value(index, 'opponent_last_five_scores'             , 0)
            test_set.set_value(index, 'opponent_last_five_first_downs'        , 0)
            test_set.set_value(index, 'opponent_last_five_penalties'          , 0)
            test_set.set_value(index, 'opponent_last_five_net_yards'          , 0)
            test_set.set_value(index, 'opponent_last_five_net_yards_rushing'  , 0)
            test_set.set_value(index, 'opponent_last_five_net_yards_passing'  , 0)
            test_set.set_value(index, 'opponent_last_five_avg_gain'           , 0)
            
        i += 1

    #dropping rows with missing data
    test_set = test_set.drop(test_set[test_set.hawks_last_five_scores == 0].index)

    #normalize features
    features = ['hawks_last_five_scores_norm',         
    'hawks_last_five_first_downs_norm',          
    'hawks_last_five_penalties_norm',            
    'hawks_last_five_net_yards_norm',            
    'hawks_last_five_net_yards_rushing_norm',    
    'hawks_last_five_net_yards_passing_norm',    
    'hawks_last_five_avg_gain_norm',             
    'opponent_last_five_scores_norm',            
    'opponent_last_five_first_downs_norm',       
    'opponent_last_five_penalties_norm',         
    'opponent_last_five_net_yards_norm',       
    'opponent_last_five_net_yards_rushing_norm',
    'opponent_last_five_net_yards_passing_norm',
    'opponent_last_five_avg_gain_norm'          ]
               
    hawks_last_five_scores_norm               = []
    hawks_last_five_first_downs_norm          = []
    hawks_last_five_penalties_norm            = []
    hawks_last_five_net_yards_norm            = []
    hawks_last_five_net_yards_rushing_norm    = []
    hawks_last_five_net_yards_passing_norm    = []
    hawks_last_five_avg_gain_norm             = []
    
    opponent_last_five_scores_norm            = []
    opponent_last_five_first_downs_norm       = []
    opponent_last_five_penalties_norm         = []
    opponent_last_five_net_yards_norm         = []
    opponent_last_five_net_yards_rushing_norm = []
    opponent_last_five_net_yards_passing_norm = []
    opponent_last_five_avg_gain_norm          = []

    test_set = test_set.reset_index(drop=True)

    i = 0
    for index, row in test_set.iterrows():
        hawks_last_five_scores_norm.append((float(test_set['hawks_last_five_scores'][i] - test_set['hawks_last_five_scores'].min()))/
                     (float(test_set['hawks_last_five_scores'].max() - test_set['hawks_last_five_scores'].min())))
           
        hawks_last_five_first_downs_norm.append((float(test_set['hawks_last_five_first_downs'][i] - test_set['hawks_last_five_first_downs'].min()))/
                    (float(test_set['hawks_last_five_first_downs'].max() - test_set['hawks_last_five_first_downs'].min())))
            
        hawks_last_five_penalties_norm.append((float(test_set['hawks_last_five_penalties'][i] - test_set['hawks_last_five_penalties'].min()))/
                     (float(test_set['hawks_last_five_penalties'].max() - test_set['hawks_last_five_penalties'].min())))
        
        hawks_last_five_net_yards_norm.append((float(test_set['hawks_last_five_net_yards'][i] - test_set['hawks_last_five_net_yards'].min()))/
                     (float(test_set['hawks_last_five_net_yards'].max() - test_set['hawks_last_five_net_yards'].min())))
        
        hawks_last_five_net_yards_rushing_norm.append((float(test_set['hawks_last_five_net_yards_rushing'][i] - test_set['hawks_last_five_net_yards_rushing'].min()))/
                     (float(test_set['hawks_last_five_net_yards_rushing'].max() - test_set['hawks_last_five_net_yards_rushing'].min())))
        
        hawks_last_five_net_yards_passing_norm.append((float(test_set['hawks_last_five_net_yards_passing'][i] - test_set['hawks_last_five_net_yards_passing'].min()))/
                     (float(test_set['hawks_last_five_net_yards_passing'].max() - test_set['hawks_last_five_net_yards_passing'].min())))
        
        hawks_last_five_avg_gain_norm.append((float(test_set['hawks_last_five_avg_gain'][i] - test_set['hawks_last_five_avg_gain'].min()))/
                     (float(test_set['hawks_last_five_avg_gain'].max() - test_set['hawks_last_five_avg_gain'].min())))
        
        opponent_last_five_scores_norm.append((float(test_set['opponent_last_five_scores'][i] - test_set['opponent_last_five_scores'].min()))/
                     (float(test_set['opponent_last_five_scores'].max() - test_set['opponent_last_five_scores'].min())))
        
        opponent_last_five_first_downs_norm.append((float(test_set['hawks_last_five_scores'][i] - test_set['hawks_last_five_scores'].min()))/
                    (float(test_set['hawks_last_five_scores'].max() - test_set['hawks_last_five_scores'].min())))
        
        opponent_last_five_penalties_norm.append((float(test_set['opponent_last_five_first_downs'][i] - test_set['opponent_last_five_first_downs'].min()))/
                    (float(test_set['opponent_last_five_first_downs'].max() - test_set['opponent_last_five_first_downs'].min())))
        
        opponent_last_five_net_yards_norm.append((float(test_set['opponent_last_five_penalties'][i] - test_set['opponent_last_five_penalties'].min()))/
                     (float(test_set['opponent_last_five_penalties'].max() - test_set['opponent_last_five_penalties'].min())))
        
        opponent_last_five_net_yards_rushing_norm.append((float(test_set['opponent_last_five_net_yards'][i] - test_set['opponent_last_five_net_yards'].min()))/
                    (float(test_set['opponent_last_five_net_yards'].max() - test_set['opponent_last_five_net_yards'].min())))
        
        opponent_last_five_net_yards_passing_norm.append((float(test_set['opponent_last_five_net_yards_rushing'][i] - test_set['opponent_last_five_net_yards_rushing'].min()))/
                     (float(test_set['opponent_last_five_net_yards_rushing'].max() - test_set['opponent_last_five_net_yards_rushing'].min())))
    
        opponent_last_five_avg_gain_norm.append((float(test_set['opponent_last_five_net_yards_passing'][i] - test_set['opponent_last_five_net_yards_passing'].min()))/
                     (float(test_set['opponent_last_five_net_yards_passing'].max() - test_set['opponent_last_five_net_yards_passing'].min())))
        
        i+=1
    
    test_set['hawks_last_five_scores_norm'               ] = pd.Series(hawks_last_five_scores_norm)
    test_set['hawks_last_five_first_downs_norm'          ] = pd.Series(hawks_last_five_first_downs_norm)
    test_set['hawks_last_five_penalties_norm'            ] = pd.Series(hawks_last_five_penalties_norm)
    test_set['hawks_last_five_net_yards_norm'            ] = pd.Series(hawks_last_five_net_yards_norm)
    test_set['hawks_last_five_net_yards_rushing_norm'    ] = pd.Series(hawks_last_five_net_yards_rushing_norm)
    test_set['hawks_last_five_net_yards_passing_norm'    ] = pd.Series(hawks_last_five_net_yards_passing_norm)
    test_set['hawks_last_five_avg_gain_norm'             ] = pd.Series(hawks_last_five_avg_gain_norm)
    test_set['opponent_last_five_scores_norm'            ] = pd.Series(opponent_last_five_scores_norm)
    test_set['opponent_last_five_first_downs_norm'       ] = pd.Series(opponent_last_five_first_downs_norm)
    test_set['opponent_last_five_penalties_norm'         ] = pd.Series(opponent_last_five_penalties_norm)
    test_set['opponent_last_five_net_yards_norm'         ] = pd.Series(opponent_last_five_net_yards_norm)
    test_set['opponent_last_five_net_yards_rushing_norm' ] = pd.Series(opponent_last_five_net_yards_rushing_norm)
    test_set['opponent_last_five_net_yards_passing_norm' ] = pd.Series(opponent_last_five_net_yards_passing_norm)
    test_set['opponent_last_five_avg_gain_norm'          ] = pd.Series(opponent_last_five_avg_gain_norm)

    #perform logistic regression over multiple values to find best step size
    feature_matrix, winner = getNumpyData(test_set, features, 'winner')
    num_won = test_set[test_set['winner'] == 1]['winner'].sum()
    min_wrong = num_won + 1
    best_step_size = 0
    for i in range(-100,400):
        coefficients = logistic_regression(feature_matrix, winner, initial_coefficients=np.zeros(15), step_size=i, max_iter=301)
        scores = np.dot(feature_matrix, coefficients)
        count_pos = 0
        count_neg = 0

        for score in scores:
            if score > 0:
                count_pos += 1
            else:
                count_neg += 1

        count_wrong = abs(num_won - count_pos)
        if count_wrong < min_wrong:
            best_step_size = i
            min_wrong = count_wrong

    #use best value and compute accuracy
    coefficients = logistic_regression(feature_matrix, winner, initial_coefficients=np.zeros(15), step_size=best_step_size, max_iter=301)
    scores = np.dot(feature_matrix, coefficients)
    count_pos = 0
    count_neg = 0
    
    for score in scores:
        if score > 0:
            count_pos += 1
        else:
            count_neg += 1
    
    print(count_pos, "out of,", num_won)
    
def main():
    game_predictor()

if __name__ == "__main__":
    main()
