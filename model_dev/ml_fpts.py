import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.linear_model import LinearRegression

import statsmodels as ols

def main():
    df = pd.read_csv('data/qb_historical.csv')

    X_train, X_test, y_train, y_test, X_holdout, y_holdout = preprocess(df)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f'MSE: {mse}')
    print(f'r2: {r2}')


def preprocess(df):
    #drop irrelevant columns
    df = df.drop(['passer_player_name', 'player_id', 'two_pt_sum', 'rusher_player_name', 'cur_fpts'], axis=1)

    #fix missingness in target variable
    df['next_fpts'] = df['next_fpts'].fillna(0)
    df = df.query('next_fpts != 0')

    #create input and outputs
    X = df.drop('next_fpts', axis=1)
    y = df['next_fpts']

    #recode categorical variables
    cat_cols = ['team', 'year']
    num_cols = [col for col in list(X.columns) if col not in ['team', 'year']]

    one_hot_encoder = OneHotEncoder()

    X_cat = pd.DataFrame(one_hot_encoder.fit_transform(X[cat_cols]).toarray(), columns=one_hot_encoder.get_feature_names_out(cat_cols),index=X.index)
    X_enc = pd.concat([X[num_cols], X_cat],axis=1)

    #create holdout sets
    X_holdout = X_enc.query('year_2023 == 1 or year_2024 == 1')
    holdout_indicies = list(X_holdout.index)
    y_holdout = y.loc[holdout_indicies]

    X_enc = X_enc.query('year_2023 != 1 and year_2024 != 1')
    keep_indicies = list(X_enc.index)
    y = y.loc[keep_indicies]

    #create training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X_enc, y)

    #scale data
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return(X_train, X_test, y_train, y_test, X_holdout, y_holdout)



if __name__ == '__main__':
    main()