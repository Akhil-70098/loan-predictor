import pickle
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as nu
from numpy import *

data = pd.read_csv("modified.csv")
idcol = ['Loan_ID']
data.drop(['Unnamed: 0'], axis=1, inplace=True)

predictors = ['Gender', 'married', 'Education', 'selfemployment', 'applicantincome', 'coapplicantincome', 'loanamount', 'Loan_amount_term',
              'Credit_history', 'dependents_0', 'dependents_1', 'dependents_2', 'dependents_3', 'Property_area_0', 'Property_area_1', 'Property_area_2']
target = ['loan_status']
train = data.loc[data['source'] == 'train']
test = data.loc[data['source'] == 'test']
'''
correlation = train.corr()
correlation['loan_status'].sort_values(ascending = False)
'''

regressor = RandomForestClassifier()
regressor.fit(train[predictors], train[target])

y_pred = regressor.predict(test[predictors])

metrics.accuracy_score(y_pred, test[target])

with open('mlModel.pickle', 'wb') as handle:
    pickle.dump(regressor, handle, pickle.HIGHEST_PROTOCOL)
