import pandas as pd

df = pd.read_csv('demo.csv')

df.to_csv("new_demo.csv", index=False)
