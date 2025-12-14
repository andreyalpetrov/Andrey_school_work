import pandas as pd

df = pd.read_csv('titanic.csv')

numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
print(df[numeric_cols].describe())

categorical_cols = df.select_dtypes(include=['object', 'category']).columns
for col in categorical_cols:
    print(f"Столбец: {col}")
    print(df[col].value_counts(dropna=False))


men_count = df[df['Sex'] == 'male'].shape[0]
print(f"Количество мужчин на корабле: {men_count}")


first_class_cabins = df[df['Pclass'] == 1]['Cabin'].dropna()
all_cabins = first_class_cabins.str.split().explode()
unique_cabins_count = all_cabins.nunique()
print(f"Количество уникальных кают первого класса: {unique_cabins_count}")