import statsmodels
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.datasets import utils as du
import pandas as pd
import numpy as np
import pdb
import sys

class RegressionSetup():
    def __init__(self):
        self.df = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")
        self.df.rename(columns={'Pagerank (all)': 'pagerank', \
                                'Received citations (all)': 'forward_citations', \
                                'Pagerank (assignee citations only)': 'pagerank_AssigneeOnly', \
                                'Received (assignee citations only)': 'forward_citations_AssigneeOnly', \
                                'granted year': 'granted_year'}, inplace=True)
        self.fitting_results_detail = {}
        self.fitting_results = {}
        self.fitting_failures = {}
        with open("fitting_results.txt", "w") as wfile:
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
                formula += " {0:s} ".format(element)
                firstelement = False
            else:
                formula += "+ {0:s} ".format(element)
        for element in fe_var:
            formula += "+ C({0:s}) ".format(element)
        
        print("Running " + formula)
        
        """compile filename for saving individual regression result"""
        filename = "fit_{0:s}_greenness_{1:s}_{2:s}".format(scheme, regressiontype, formula).\
                    replace("~", "=").replace(" ", "")#.replace("(", "\(").replace(")", "\)")
        
        with open(filename, "w") as wfile:
            wfile.write("")
        
        """run regression"""
        if regressiontype == "logit":
            regression_function = smf.logit
        elif regressiontype == "ols":
            regression_function = smf.ols
        else:
            print("Error: Regression type not implemented: {0:s}".format(regressiontype))
        try:
            model = regression_function(formula=formula, data=self.df)
            model_fit = model.fit()
        except:
            exc_info = str(sys.exc_info())
            self.fitting_failures[filename] = exc_info
            print(exc_info)
            return
        
        """generate prediction iff we have only year dummy and only greenness x"""
        prediction_df = None
        if fe_var == ["granted_year"] and x_var == ["green"]:
            prediction_df = pd.DataFrame({'green':[True]*(2019-1976), 'granted_year': np.arange(1976,2019)})
            prediction_df["prediction"] = model_fit.predict(prediction_df[["green", "granted_year"]])
        
        """save and reload fit while removing data"""
        model_fit.save(filename, remove_data=True)
        import statsmodels.iolib.smpickle
        model_fit = statsmodels.iolib.smpickle.load_pickle(filename)
        self.fitting_results_detail[filename] = model_fit
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
                                             "prediction": prediction_df
                                             }
        
        """write fit to text file"""
        with open("fitting_results.txt", "a") as wfile:
            wfile.write(str(model_fit.formula) + "\n" + str(model_fit.summary()) + "\n\n")
    
    def save(self):
        with open("fitting_results_detail.pkl", "wb") as wfile:
            pickle.dump(self.fitting_results_detail, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        with open("fitting_results.pkl", "wb") as wfile:
            pickle.dump(self.fitting_results, wfile, protocol=pickle.HIGHEST_PROTOCOL)
        with open("fitting_failures.pkl", "wb") as wfile:
            pickle.dump(self.fitting_failures, wfile, protocol=pickle.HIGHEST_PROTOCOL)
    
    def run(self):
        schemes = ["Envtech", "IPCGI", "Y_Codes", "Envtech_IPCGI", "IPCGI_Y_Codes", "Y_Codes_Envtech", \
                                                                            "Envtech_IPCGI_Y_Codes", "Any"]
        #y_vars = ["pagerank", "forward_citations"]
        y_vars = ["pagerank", "forward_citations", '5_year_lag_citations', '10_year_lag_citations', \
                '20_year_lag_citations', '30_year_lag_citations', 'urban', 'officialtype', 'private', \
                "pagerank_AssigneeOnly", "forward_citations_AssigneeOnly"]
        for scheme in schemes:
            for y_var in y_vars:
                self.run_regression(scheme, 'logit', y_var, ["green"], ["granted_year"])
                self.run_regression(scheme, 'ols', y_var, ["green"], ["granted_year"])
        self.save()
    
if __name__ == "__main__":
    RS = RegressionSetup()
    RS.run()
