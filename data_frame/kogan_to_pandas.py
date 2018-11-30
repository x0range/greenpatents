# kogan
import pandas as pd
import numpy as np

kogan_df = pd.read_csv("kogan_patents.csv", index_col=0, usecols = [0, 8], header=0)
kogan_df.index = kogan_df.index.astype(str)
kogan_df = kogan_df[np.isfinite(kogan_df['xi'])]

relevant_df = pd.read_pickle("patents_dates_years.pkl")
relevant_df.drop(relevant_df.columns, inplace=True, axis=1)

kogan_df = pd.merge(relevant_df, kogan_df, left_index=True, right_index=True)
kogan_df.columns = ["Kogan et al. value"]

kogan_df.to_pickle("patents_value_kogan.pkl")
