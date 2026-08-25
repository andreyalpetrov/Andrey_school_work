import pandas as pd

df = pd.read_csv('titanic.csv')

print(f"Количество строк: {df.shape[0]}")
print(f"Количество столбцов: {df.shape[1]}")
print("Типы данных:")
print(df.dtypes)
print("Количество пропущенных значений:")
print(df.isna().sum())

total_passengers = df.shape[0]
print(f"Всего пассажиров на Титанике: {total_passengers}")

missing_age_count = df['Age'].isnull().sum()
print(f"Строк с пропущенным возрастом: {missing_age_count}")