import pandas as pd

df = pd.read_csv('titanic.csv')

df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
result = df.loc[df['PassengerId'] == 888, 'FamilySize']
print(result)