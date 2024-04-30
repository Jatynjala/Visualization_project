import pandas as pd

dat = pd.read_csv("losses_russia.csv")
dat.drop(["sub_model", "captured and stripped", "defected and captured", "destroyed in a non-combat related incident"], axis=1, inplace=True)
dat = dat.fillna(0)
dat["lost_by"] = "russia"
dat.to_csv("losses_russia_preproccessed.csv")
dat = pd.read_csv("losses_ukraine.csv")
dat.drop(dat.columns[5], axis=1, inplace=True)
dat.drop(["sub_model", "scuttled", "sunk but raised by Russia"], axis=1, inplace=True)
dat = dat.fillna(0)
dat["lost_by"] = "ukraine"
dat.to_csv("losses_ukraine_preproccessed.csv")
dat = pd.read_csv("losses_russia_preproccessed.csv")
dat2 = pd.read_csv("losses_ukraine_preproccessed.csv")
dat_final = pd.concat([dat, dat2])
dat_final.to_csv("all_losses.csv")