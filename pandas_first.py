import pandas as pd

data  = pd.read_csv('wine.csv')

# print(data.head())
# print(data.count())

# print(data.shape)
# print(data.size())
# print(data.info())
# print(data.describe())

# # print(data.isna().sum())
# print(data.loc[10:15, ['country', 'price']])

print(data[(data.price > 300) & (data.country == 'US')][('country', 'price')])
