import pandas as pd
import numpy as np

df = pd.read_csv('direction_centaur.csv')

df["answer_j"]=df["answer"].apply(lambda x: 1 if x=="J" else 0)
df_agg = df.groupby(["task_id", "feature"])[["answer_j", "confidence"]].agg("mean")

#add a new column compute the entropy answer J
df_agg["neg_entropy"] = df_agg["answer_j"]*np.log(df_agg["answer_j"])+(1-df_agg["answer_j"])*np.log(1-df_agg["answer_j"])

#average by task_id
df_agg = df_agg.groupby("task_id")[["neg_entropy", "confidence"]].agg("mean")
print(df_agg)

#filter out all confidence larger less than 3.5
df_agg = df_agg[df_agg["confidence"]>3.5]

#sort data frame based on answer J
df_agg = df_agg.sort_values(by="neg_entropy", ascending=False)

print(df_agg.head(20))

df_agg.to_csv('direction_processed.csv', index=True)