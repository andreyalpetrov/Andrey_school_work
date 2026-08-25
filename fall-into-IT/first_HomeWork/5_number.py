import pandas as pd

df = pd.read_csv('titanic.csv')

median_age = df['Age'].median()
print(f"Медианный возраст = {median_age}")

df['Age'] = df['Age'].fillna(median_age)