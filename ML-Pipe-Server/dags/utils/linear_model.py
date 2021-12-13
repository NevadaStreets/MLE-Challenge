"""
Module that implements Lineal Model class.

LinearModel was designed to predict milk prices.

"""
import numpy as np
import pandas as pd
import pickle
import os

from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.feature_selection import SelectKBest, mutual_info_regression

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


class LinearModel:
    """
    Linear model to make prediction in milk prices
    """
    def __init__(self):
        self.model_path = f"{CUR_DIR}/../model/"
        self.data_path = f"{CUR_DIR}/../data/"
        self.model = None

    
    def train(self):
        # generate random data-set
        np.random.seed(0)
        X = pd.read_csv(self.data_path + "X.csv")
        y = pd.read_csv(self.data_path + "y.csv", header=None)[0]


        pipe = Pipeline([('scale', StandardScaler()),
                         ('selector', SelectKBest(mutual_info_regression)),
                         ('poly', PolynomialFeatures()),
                         ('model', Ridge())])
        k=[3, 4, 5, 6, 7, 10]
        alpha=[1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
        poly = [1, 2, 3, 5, 7]
        clf = GridSearchCV(estimator = pipe,
                            param_grid = dict(selector__k=k,
                                              poly__degree=poly,
                                              model__alpha=alpha),
                            cv = 3,
                           scoring = 'r2')
        clf.fit(X, y)
        self.model = clf

    def save(self):
        file_path = self.model_path + 'final_model.sav'
        pickle.dump(self.model, open(file_path, 'wb'))