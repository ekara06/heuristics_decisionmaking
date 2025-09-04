import pandas as pd
df = pd.read_csv("chatgpt_unknown2_problems.csv")

df["xg"]=df["Object_1 Feature_1 value"] > df["Object_2 Feature_1 value"]
df["yg"]=df["Object_1 Criterion value"] > df["Object_2 Criterion value"]

# compute how often xg and yg are the same
df["same"]=df["xg"]==df["yg"]
print(df["same"].mean())

df["xg"]=df["Object_1 Feature_2 value"] > df["Object_2 Feature_2 value"]
df["yg"]=df["Object_1 Criterion value"] > df["Object_2 Criterion value"]

# compute how often xg and yg are the same
df["same"]=df["xg"]==df["yg"]
print(df["same"].mean())