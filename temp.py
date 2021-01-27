import pandas as pd

df =pd.read_csv('results/wildboar04_result_1611756794.csv')

# print(df)


x_= df['label'].value_counts()

xx = pd.DataFrame(x_).reset_index()


print(xx)

x_list = list(xx['index'])
y_list = list(xx['label'])

print(y_list)