import numpy as np
import pandas as pd
import sys
from datetime import timedelta

import pandas as pd
from sklearn.linear_model import Ridge, BayesianRidge, ElasticNet, RidgeCV, ElasticNetCV
from sklearn.model_selection import cross_val_score, ShuffleSplit
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
import numpy as np
from generateData import *

try:
    import cpickle as pickle
except:
    import pickle




#today=0
day_to_run=2


train,test=createTrainTestSets(day_to_run)




#sort into positions and clean
positions = sorted(train['FD pos'].unique())
if 0.0 in positions:
	positions.remove(0.0)




"""Uncomment which regression algorithm you'd like run"""
estimators = ["Ridge",
             #"ElasticNet",
              #"RandomForestRegressor",
              #"GradientBoostingRegressor",
              # 	"SVM"
              ]

types = ['train', 'cv', 'test']

# Dataframe index, e.g. Ridge_train
rmse_names = [x + '_' + y for y in types for x in estimators]

# Initialize a matrix filled with 0s
df_rmse = pd.DataFrame([[0.0] * len(positions) for j in range(len(rmse_names))], 
    index = rmse_names, columns = positions)

final=pd.DataFrame([])
""" Machine Learning """
for position in positions:
    # Iterate through all positions
    print ('Learning for Position %s ...' % position)
    df_pos_train = train.ix[train['FD pos'] == position,]
    df_pos_test = test.ix[test['FD pos'] == position,]



    for i in range(len(estimators)):
        est = estimators[i]

        if(est == "GradientBoostingRegressor"):
            n_estimators = [47]
            learning_rate = [0.1]
            param_grid = {'n_estimators': n_estimators, 'learning_rate': learning_rate}
            grid_search = GridSearchCV(GradientBoostingRegressor(max_depth=3), param_grid, cv=5)
            grid_search.fit(df_pos_train.ix[:,:-1], df_pos_train['FDP'])

        elif(est == "RandomForestRegressor"):
            n_estimators = [47]
            param_grid = {'n_estimators': n_estimators}
            grid_search = GridSearchCV(RandomForestRegressor(max_depth=3), param_grid, cv=5)
            grid_search.fit(df_pos_train.ix[:,:-1], df_pos_train['FDP'])

        elif(est == "ElasticNet"):
	    
            grid_search = ElasticNetCV().fit(df_pos_train.ix[:,:-1], df_pos_train['FDP'])

        elif(est == "BayesianRidge"):
            alpha_1 = [1e-6, 1e-5, 1e-7]
            alpha_2 = [1e-6, 1e-5, 1e-7]
            lambda_1 = [1e-6, 1e-5, 1e-7]
            lambda_2 = [1e-6, 1e-5, 1e-7]
            param_grid = {'alpha_1': alpha_1, 'alpha_2':alpha_2, 'lambda_1':lambda_1, 'lambda_2':lambda_2}
            grid_search = GridSearchCV(BayesianRidge(), param_grid, cv=5)
            grid_search.fit(df_pos_train.ix[:,:-1], df_pos_train[target])

        elif(est == "Ridge"):
            grid_search = RidgeCV().fit(df_pos_train.ix[:,:-1], df_pos_train['FDP'])

        elif(est == "SVM"):
            C = [47]
            gamma = [0.3]
            param_grid = {'C': C, 'gamma': gamma}
            grid_search = GridSearchCV(SVC(), param_grid, cv=5)
            grid_search.fit(df_pos_train.ix[:,:-1], df_pos_train['FDP'])

        else:
            print est
            print "Cannot find the algorithm"
            exit()

        train_rmse = np.sqrt(np.mean( (df_pos_train['FDP'] - \
                    grid_search.predict(df_pos_train.ix[:,:-1]))**2.0 ))
        test_rmse = np.sqrt(np.mean( (df_pos_test['FDP'] - \
                    grid_search.predict(df_pos_test.ix[:,:-2]))**2.0 ))
	

	prediction=grid_search.predict(df_pos_test.ix[:,:-2])
	x=df_pos_test[['FDP','fdp mean', 'FD Sal']]#.to_frame()
	x['pos']=position
	x['predictions_'+est]=prediction.tolist()
	final=final.append(x)

        
	# Deprecating "mean_squared_error". Use "neg_mean_squared_error" instead.
        cv_rmse = np.sqrt(np.abs( cross_val_score(grid_search, train, train['FDP'],\
            cv = 5, scoring = 'neg_mean_squared_error').mean() ))

        # Given the variable name in a string, get the variable value and import into dataframe
        for val in types:
            df_rmse.loc[estimators[i] + "_" + val, position] = eval(val + '_rmse')


df_rmse.to_csv('rmse.csv', header = True, index=True)

final.to_csv("final.csv")



