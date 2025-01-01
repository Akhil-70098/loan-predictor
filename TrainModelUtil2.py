import pandas as pd
import numpy as nu
from numpy import *

data = pd.read_csv("interest.csv")
idcol = ['index']

predictors = ['loanamount','applicant_income']
target = ['Interest_rate']
train = data.loc[data['source'] == 'train']
test = data.loc[data['source'] == 'test']
'''
correlation = train.corr()
correlation['loan_status'].sort_values(ascending = False)
'''

from sklearn.ensemble import RandomForestRegressor
regressor = RandomForestRegressor() 
regressor.fit(train[predictors], train[target])

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Assuming y_pred and test[target] contain continuous values
y_pred = regressor.predict(test[predictors])
y_true = test[target]

mae = mean_absolute_error(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

print(f'Mean Absolute Error: {mae}')
print(f'Mean Squared Error: {mse}')
print(f'R-squared: {r2}')

import pickle
with open('interest.pickle','wb') as handle:
    pickle.dump(regressor,handle,pickle.HIGHEST_PROTOCOL)
