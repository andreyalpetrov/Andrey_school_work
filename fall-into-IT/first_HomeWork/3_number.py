import pandas as pd

df = pd.read_csv('titanic.csv')

survived_total = df['Survived'].sum()
print(f"Количество выживших: {survived_total}")

survival_rate_total = (survived_total / len(df) * 100).round(2)
print(f"Процент выживших: {survival_rate_total}%")

women_df = df[df['Sex'] == 'female']
w_survived = women_df['Survived'].sum()
w_survival_rate = (w_survived / len(women_df) * 100).round(2)
print(f"Женщины: {w_survival_rate}%")

men_df = df[df['Sex'] == 'male']
men_survived = men_df['Survived'].sum()
men_survival_rate = (men_survived / len(men_df) * 100).round(2)
print(f"Мужчины: {men_survival_rate}%")