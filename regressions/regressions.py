import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.datasets import utils as du
import pandas as pd
import numpy as np
import pdb

def fixed_effect_logit(df, y_var, x_var, fe_var):
    pdb.set_trace()
    df["green"] = df["green"].astype('float')
    df["green"] = df["green"].astype('Int32')
    #df["green"] = np.int64(df["green"])
    # get unique values
    unique_values = list(df[fe_var].unique())
    fe_var_list = []
    for i in range(1, len(unique_values)):
        uv = unique_values[i]
        df[fe_var + "_" + str(uv)] = np.int64(df[fe_var]==uv)
        fe_var_list.append(fe_var + "_" + str(uv))
    df = df[y_var+x_var+fe_var_list]
    df = df.dropna(axis=0)
    data = du.Dataset(data=df, names=list(df.columns), endog=df[y_var], exog=df[x_var+fe_var_list])
    pdb.set_trace()
    data.exog = sm.add_constant(data.exog, prepend=False)
    #logitmodel = sm.GLM(data.endog, data.exog, family=sm.families.Binomial(link=statsmodels.genmod.families.links.logit))
    logitmodel = sm.GLM(data.endog, data.exog, family=sm.families.Binomial(), link=statsmodels.genmod.families.links.logit)
    gaussianmodel = sm.GLM(data.endog, data.exog, family=statsmodels.genmod.families.Gaussian())
    return logitmodel, gaussianmodel
    #res = model.fit()
    #return res

def analysis(data):
    # need to transform dataset??
    ##data = sm.datasets.get_rdataset("dietox", "geepack").data
    if False:
        md = smf.mixedlm("pagerank ~ green", data, groups=data["granted_year"])
        # fails with: IndexError: index 6221293 is out of bounds for axis 0 with size 6026927
        mdf = md.fit()
        print(mdf.summary())
    #pdb.set_trace()
    ml, mg = fixed_effect_logit(data, ["pagerank"], ["green"], "granted_year")
    mlf = ml.fit()
    mgf = mg.fit()
    print(mlf.summary())
    print(mgf.summary())
    md = smf.mixedlm("forward_citations ~ green", data, groups=data["granted_year"])
    mdf = md.fit()
    print(mdf.summary())
    ml, mg = fixed_effect_logit(data, ["forward_citations"], ["green"], "granted_year")
    mlf = ml.fit()
    mgf = mg.fit()
    print(mlf.summary())
    print(mgf.summary())
    

def test():
    df = pd.DataFrame({"pagerank": [0.01, 0.01, 0.09, 0.01, 0.11, 0.01, 0.02, 0.011, 0.01, 0.06, 0.12, 0.015],
                       "forward_citations": [1, 1, 12, 1, 10, 2, 1, 1, 1, 4, 10, 1],
                       "green": [True, True, False, False, True, False, False, False, False, True, True, False],
                       "granted_year": [1977, 1977, 1977, 1977, 1977, 1978, 1978, 1978, 1978, 1978, 1978, 1978]})
    #analysis(df)
    df = pd.DataFrame({"pagerank": [0.01, 0.01, 0.09, 0.01, 0.11, 0.01, 0.02, 0.011, 0.01, 0.06, 0.12, 0.015],
                       "forward_citations": [1, 1, 12, 1, 10, 2, 1, 1, 1, 4, 10, 1],
                       "green": [True, False, True, False, True, False, False, False, False, True, True, False],
                       "granted_year": [1977, 1977, 1977, 1977, 1977, 1978, 1978, 1978, 1978, 1978, 1978, 1978]})
    analysis(df)
    
    
def load():
    """To avoid copying dataframes, we do not drag them through different functions."""
    df = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")
    df.rename(columns={'Pagerank (all)': 'pagerank', 'Received citations (all)': 'forward_citations', 'granted year': 'granted_year'}, inplace=True)
    df["green"] = df["Envtech"]
    #analysis(pddf)
    #ml, mg = fixed_effect_logit(data, ["pagerank"], ["green"], "granted_year")
    y_var, x_var, fe_var = ["pagerank"], ["green"], "granted_year"
    #df["green"] = df["green"].astype('float')
    #df["green"] = df["green"].astype('Int32')
    #pdb.set_trace()
    model = smf.logit(formula="{0:s} ~ {1:s} + C({2:s})".format(y_var[0], x_var[0], fe_var), data=df)
    mf = model.fit()
    print(mf.summary())
    #gaussian
    model = smf.ols(formula="{0:s} ~ {1:s} + C({2:s})".format(y_var[0], x_var[0], fe_var), data=df)
    mf = model.fit()
    print(mf.summary())
    
if __name__ == "__main__":
    #test()
    load()
