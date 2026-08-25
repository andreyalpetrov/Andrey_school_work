import pandas as pd

df = pd.read_csv('titanic.csv')

first_class_sr = df[df['Pclass'] == 1]['Fare'].mean()
print(f"Средняя стоимость билета для первого класса: {first_class_sr.round(2)}")

third_class_df = df[df['Pclass'] == 3]
third_class_survival_rate = (third_class_df['Survived'].sum() / len(third_class_df) * 100).round(2)
print(f"Выживаемость для третьего класса: {third_class_survival_rate}")