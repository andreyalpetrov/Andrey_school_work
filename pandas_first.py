import pandas as pd

data  = pd.read_csv('wine.csv')

# print(data.head())
# print(data.count())

# print(data.shape)
# print(data.size())
# print(data.info())
# print(data.describe())

print(data.isna().sum())