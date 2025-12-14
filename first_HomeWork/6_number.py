import pandas as pd

df = pd.read_csv('titanic.csv')

df['FamilySize'] = df['SibSp'] + df['Parch'] + 1

family888 = df.loc[888, 'FamilySize']
print("Размер семьи:", family888)