import pandas as pd

df = pd.read_csv('nh_imgs.csv')

df = df.rename(columns = {'Unnamed: 0':'img_no'})

df.to_csv("nh_imgs.csv", index=False)
