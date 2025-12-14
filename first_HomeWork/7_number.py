import pandas as pd

df = pd.read_csv('titanic.csv')

age_by_survival = df.groupby('Survived')['Age'].mean().round(2)

print(f"Выжившие: {age_by_survival.loc[1]}")
print(f"Погибшие: {age_by_survival.loc[0]}")