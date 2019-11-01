import statsmodels
import statsmodels.stats.api as sms
import statsmodels.formula.api as smf
import statsmodels.iolib.smpickle
from statsmodels.datasets import utils as du
import pandas as pd
import numpy as np
import pickle
import sys
import pdb

class RegressionSetup():
    def __init__(self, chunk=None):
        self.chunk = chunk 
        assert chunk is None or chunk in [1, 2, 3]
        self.filename_infix = "_" + str(chunk) if chunk is not None else ""
        
        self.df = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")
        self.df.rename(columns={'Pagerank (all)': 'pagerank', \
                                'Received citations (all)': 'forward_citations', \
                                'Pagerank (assignee citations only)': 'pagerank_AssigneeOnly', \
                                'Received citations (assignee citations only)': 'forward_citations_AssigneeOnly', \
                                '5_year_lag_citations': 'five_year_lag_citations', \
                                '10_year_lag_citations': 'ten_year_lag_citations', \
                                '20_year_lag_citations': 'twenty_year_lag_citations', \
                                '30_year_lag_citations': 'thirty_year_lag_citations', \
                                'granted year': 'granted_year'}, inplace=True)
                                
        """Convert bools to numeric, otherwise regressions will be run on two y values (one for True, one fore False)"""
        self.df["urban"] = self.df["urban"].astype('float64')
        self.df["private"] = self.df["private"].astype('float64')
        
        #self.fitting_results_detail = {}
        self.fitting_results = {}
        self.fitting_failures = {}
        with open("fitting_results{0:s}.txt".format(self.filename_infix), "w") as wfile:
            wfile.write("")
        
    def run_regression(self, scheme, regressiontype, y_var, x_var, fe_var):
        """interpret scheme"""
        greenness_Envtech = True if "Envtech" in scheme else False
        greenness_IPCGI = True if "IPCGI" in scheme else False
        greenness_Y_Codes = True if "Y_Codes" in scheme else False
        self.df["green"] = (self.df["Envtech"]==greenness_Envtech) & (self.df["IPCGI"]==greenness_IPCGI) \
                                                                        & (self.df["Y_Codes"]==greenness_Y_Codes)
        if scheme == "Any":
            self.df["green"] = (self.df["Envtech"]==True) | (self.df["IPCGI"]==True) | (self.df["Y_Codes"]==True)
        
        """make formula"""
        if not isinstance(x_var, (frozenset, list, set, tuple,)):
            x_var = [x_var]
        if not isinstance(fe_var, (frozenset, list, set, tuple,)):
            fe_var = [fe_var]
        try:
            assert not isinstance(y_var, (frozenset, list, set, tuple,))
        except:
            pdb.set_trace()
        formula = "{0:s} ~ ".format(y_var)
        firstelement = True
        for element in x_var:
            if firstelement:
                formula += "{0:s} ".format(element)
                firstelement = False
            else:
                formula += "+ {0:s} ".format(element)
        for element in fe_var:
            formula += "+ C({0:s}) ".format(element)
        
        print("Running " + formula + "as " + regressiontype)
        
        """compile filename for saving individual regression result"""
        filename = "fit_{0:s}_greenness_{1:s}_{2:s}".format(scheme, regressiontype, formula).\
                    replace("~", "=").replace(" ", "")#.replace("(", "\(").replace(")", "\)")
        
        """run regression"""
        if regressiontype == "logit":
            regression_function = smf.logit
        elif regressiontype == "ols":
            regression_function = smf.ols
        else:
            print("Error: Regression type not implemented: {0:s}".format(regressiontype))
        try:
            model = regression_function(formula=formula, data=self.df)
            print("    Model setup done")
            model_fit = model.fit()
            print("    Regression done")
        except:
            exc_info = str(sys.exc_info())
            self.fitting_failures[filename] = exc_info
            print(exc_info)
            return
        
        """generate prediction iff we have only year dummy and only greenness x"""
        prediction_df = None
        if fe_var == ["granted_year"] and x_var == ["green"]:
            prediction_df = pd.DataFrame({'green': [True]*(2019-1976), 'granted_year': np.arange(1976,2019)})
            prediction_df["prediction"] = model_fit.predict(prediction_df[["green", "granted_year"]])
            prediction_df_nongreen = pd.DataFrame({'green': [False]*(2019-1976), 'granted_year': np.arange(1976,2019)})
            prediction_df_nongreen["prediction"] = model_fit.predict(prediction_df[["green", "granted_year"]])
            print("    Prediction done")
        
        """save and reload fit while removing data"""
        #model_fit.model.data.orig_exog = None
        #model_fit.model.data.orig_endog = None
        #model_fit.model.data.frame = None
        #model_fit.save(filename + ".pkl", remove_data=True)
        #print("    Model saved")
        #model_fit = statsmodels.iolib.smpickle.load_pickle(filename + ".pkl")
        #print("    Model reloaded")
        #self.fitting_results_detail[filename] = model_fit
        parameter_table = pd.concat([model_fit.params, model_fit.bse, model_fit.tvalues, model_fit.pvalues, \
                                                                                    model_fit.conf_int()], axis=1)
        parameter_table.columns = ["Coefficient", "Standard_deviation", "t_statistic", "p_value", \
                                                    "Confidence_interval_low_0.025", "Confidence_interval_high_0.975"]
        self.fitting_results[filename] = {"greenness_scheme": scheme,
                                             "type": regressiontype,
                                             "formula": formula,
                                             "filename": filename,
                                             "y": y_var,
                                             "x": x_var,
                                             "fe": fe_var,
                                             "coefficient": model_fit.params.loc["green[T.True]"],
                                             "sign": np.sign(model_fit.params.loc["green[T.True]"]).astype(int),
                                             "p_value": model_fit.pvalues.loc["green[T.True]"],
                                             "prediction": prediction_df,
                                             "prediction_nongreen": prediction_df_nongreen,
                                             "parameters": parameter_table
                                             }
        
        #pdb.set_trace()
        if regressiontype == "logit":
            """ Hosmer-Lemeshow test like here https://jbhender.github.io/Stats506/F18/GP/Group13.html
                does not make too much sense because the predictions for the individual data values are 
                going to be the same for each combination of categories if we have only dummies and fixed
                effects.
                Hosmer-Lemeshow is not part of statsmodels and would have to be re-implemented."""
            Wald_test = model_fit.wald_test("green[T.True]=0")
            Wald_v, Prob_wald = Wald_test.statistic[0][0], float(Wald_test.pvalue)
            add_to_results_dict = {"converged": model_fit.mle_retvals["converged"],   # if False, results are nonsensical
                                   "Log_Likelihood": model_fit.llf,             # LL of formula
                                   "Log_Likelihood_Null": model_fit.llnull,     # LL of flat (intercept) model
                                   "Log_Likelihood_Ratio": model_fit.llr,       # LLR
                                   "Prob_LLR": model_fit.llr_pvalue,            # prop of observing LLR w flat model
                                   "Pseudo_R_squared": model_fit.prsquared,     # 1 - LL/LLnull
                                   "AIC": model_fit.aic,                        # Akaike info criterion
                                   "BIC": model_fit.bic,                        # Bayesian info criterion
                                   "Num_Obs": model_fit.nobs,
                                   "df_Model": model_fit.df_model,
                                   "df_residuals": model_fit.df_resid
                                   }
        elif regressiontype == "ols":
            #https://www.statsmodels.org/stable/diagnostic.html
            JB_v, JB_Chi2_2tail_prob, JB_skew, JB_kurtosis = sms.jarque_bera(model_fit.resid)  # Normality
            Omni_Chi2, Omni_2tail_prob = sms.omni_normtest(model_fit.resid)         # Normality
            """Skipping heteroskedasticity tests, since regressors are all categorical anyway."""
            #test = sms.het_breuschpagan(model_fit.resid, model_fit.model.exog)      # Heteroskedasticity
            #test = sms.het_goldfeldquandt(model_fit.resid, model_fit.model.exog)    # Heteroskedasticity
            #Observation influence check, requires this library: from statsmodels.stats.outliers_influence import OLSInfluence
            #test_class = OLSInfluence(model_fit).dfbetas
            # HC_v = sms.linear_harvey_collier(model_fit)                            # Linearity
            # DW_v = sms.durbin_watson(model_fit.resid)                              # Heteroskedasticity, No serial correlation
            Condition_Number = np.linalg.cond(model_fit.model.exog)                 # Multicollinearity
            add_to_results_dict = {"R_squared": model_fit.rsquared,
                                   "R_squared_adj": model_fit.rsquared_adj,
                                   "F_statistic": model_fit.fvalue,
                                   "Prob_F": model_fit.f_pvalue,
                                   "Log_Likelihood": model_fit.llf,
                                   "AIC": model_fit.aic,
                                   "BIC": model_fit.bic,
                                   "Num_Obs": model_fit.nobs,
                                   "df_Model": model_fit.df_model,
                                   "df_residuals": model_fit.df_resid,
                                   "Omnibus": Omni_Chi2,
                                   "Prob_Omnibus": Omni_2tail_prob,
                                   "Skew": JB_skew,
                                   "Kurtosis": JB_kurtosis,
                                   #"Durbin_Watson": DW_v,
                                   "Jarque_Bera": JB_v,
                                   "Prob_Jarque_Bera": JB_Chi2_2tail_prob,
                                   "Condition_Number": Condition_Number
                                   }
        else:
            pass
        
        self.fitting_results[filename].update(add_to_results_dict)
        
        """write fit to text file"""
        with open("fitting_results{0:s}.txt".format(self.filename_infix), "a") as wfile:
            wfile.write(str(model_fit.model.formula) + "\n" + str(model_fit.summary()) + "\n\n")
        self.save()
        
        print("    Everything done")

    
    def save(self):
        #with open("fitting_results_detail.pkl", "wb") as wfile:
        #    pickle.dump(self.fitting_results_detail, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        with open("fitting_results{0:s}.pkl".format(self.filename_infix), "wb") as wfile:
            pickle.dump(self.fitting_results, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        with open("fitting_failures{0:s}.pkl".format(self.filename_infix), "wb") as wfile:
            pickle.dump(self.fitting_failures, wfile, protocol=pickle.HIGHEST_PROTOCOL)
    
    def run(self):
        schemes = ["Envtech", "IPCGI", "Y_Codes", "Envtech_IPCGI", "IPCGI_Y_Codes", "Y_Codes_Envtech", \
                                                                            "Envtech_IPCGI_Y_Codes", "Any"]
        y_vars = ['pagerank', 'forward_citations', 'five_year_lag_citations', 'ten_year_lag_citations', \
                'twenty_year_lag_citations', 'thirty_year_lag_citations', 'urban', 'private', \
                'pagerank_AssigneeOnly', 'forward_citations_AssigneeOnly']
        if self.chunk is not None:
            y_vars = [['pagerank', 'forward_citations', 'five_year_lag_citations'], 
                ['ten_year_lag_citations', 'twenty_year_lag_citations', 'thirty_year_lag_citations'], 
                ['urban', 'private', 'pagerank_AssigneeOnly', 'forward_citations_AssigneeOnly']]
            y_vars = y_vars[self.chunk-1]
        for scheme in schemes:
            for y_var in y_vars:
                self.run_regression(scheme, 'logit', y_var, ["green"], ["granted_year"])
                self.run_regression(scheme, 'ols', y_var, ["green"], ["granted_year"])
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        RS = RegressionSetup(int(sys.argv[1]))
    else:
        RS = RegressionSetup()
    RS.run()
