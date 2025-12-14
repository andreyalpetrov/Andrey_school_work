import pandas as pd

df = pd.read_csv('titanic.csv')

women_fc_survived = df[(df['Sex'] == 'female') & (df['Pclass'] == 1) & (df['Survived'] == 1)]
print(f"Количество выживших женщин: {len(women_fc_survived)}")

young_without = df[(df['Age'] < 18) & (df['Parch'] == 0)]
print(f"Кол-во пассажиров моложе 18 лет без родителей: {len(young_without)}")