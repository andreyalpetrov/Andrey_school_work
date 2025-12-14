import pandas as pd
df = pd.read_csv('titanic.csv')

print(df.describe())

ccols = df.select_dtypes(include='object').columns
for col in ccols:
    print(df[col].value_counts())

men = (df['Sex'] == 'male').sum()
print("Мужчин на корабле:", men)

first_class = (df['Pclass'] == 1).sum()
print("Пассажиров первого класса:", first_class)