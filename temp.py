import pandas as pd
import matplotlib.pyplot as plt


df =pd.read_csv('results/wildboar05_result_1611707062.csv')

# print(df)

label_cnt = df['label'].value_counts()
print(label_cnt.sort_index())

a = pd.DataFrame(label_cnt)
a = a.reset_index()
a.sort_index
print(a, type(a))


# x_list = label_cnt.index
# y_list = label_cnt
# print(y_list) 

# grouped = df['accuracy'].groupby(df['label'])

# acc = grouped.mean()
# acc.sort_values()
# print(acc)
# print(acc.index)
# print(acc)
# print(grouped.std())
# print(grouped.size())
# print(grouped.sum())
# plt.plot(label_cnt)
# plt.show()

