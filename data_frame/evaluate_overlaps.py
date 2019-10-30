from matplotlib import pyplot as plt
from matplotlib_venn import venn3
import pickle
import pandas as pd
import numpy as np
import scipy.sparse

def generate_index_plots(jaccard_indices_all, tversky_indices_all):
    n_classes = len(jaccard_indices_all)
    n_plots = 4
    year_seq = np.arange(1976, 2019)
    f, a = plt.subplots(n_classes, n_plots, figsize=(5 * n_plots, 4 * n_classes))
    for cl_idx, cl in enumerate(jaccard_indices_all):
        # jaccard index plot
        a[cl_idx, 0].set_title("Section " + cl + " Jaccard indices")
        a[cl_idx, 0].set_xlabel("Year")
        a[cl_idx, 0].set_ylabel("Jaccard index")
        a[cl_idx, 0].plot(year_seq, jaccard_indices_all[cl]["egy"], label="All")
        a[cl_idx, 0].plot(year_seq, jaccard_indices_all[cl]["eg"], label="Envtech, IPC GI")
        a[cl_idx, 0].plot(year_seq, jaccard_indices_all[cl]["ey"], label="Envtech, Y Codes")
        a[cl_idx, 0].plot(year_seq, jaccard_indices_all[cl]["gy"], label="IPC GI, Y Codes")
        a[cl_idx, 0].legend(loc="best")
        
        f2, a2 = plt.subplots(1, 1, figsize=(5, 4))
        a2.set_title("Class " + cl + " Jaccard indices")
        a2.set_xlabel("Year")
        a2.set_ylabel("Jaccard index")
        a2.plot(year_seq, jaccard_indices_all[cl]["egy"], label="All")
        a2.plot(year_seq, jaccard_indices_all[cl]["eg"], label="Envtech, IPC GI")
        a2.plot(year_seq, jaccard_indices_all[cl]["ey"], label="Envtech, Y Codes")
        a2.plot(year_seq, jaccard_indices_all[cl]["gy"], label="IPC GI, Y Codes")
        a2.legend(loc="best")
        f2.savefig("jaccard_indices_" + cl + ".pdf")
        plt.close(f2)
        
        labels = [["Envtech", "IPC GI"], ["Envtech", "Y Codes"], ["Y Codes", "IPC GI"]]
        for c_idx, combi in enumerate([["eg", "ge"], ["ey", "ye"], ["yg", "gy"]]):
            # tversky index plot
            a[cl_idx, c_idx + 1].set_title("Group " + cl + " " + labels[c_idx][0] + " " + labels[c_idx][1])
            a[cl_idx, c_idx + 1].set_xlabel("Year")
            a[cl_idx, c_idx + 1].set_ylabel("Tversky index (TI)")
            a[cl_idx, c_idx + 1].plot(year_seq, tversky_indices_all[cl][combi[0]], label="TI (" + labels[c_idx][0] + ", " + labels[c_idx][1] + ")")
            a[cl_idx, c_idx + 1].plot(year_seq, tversky_indices_all[cl][combi[1]], label="TI (" + labels[c_idx][1] + ", " + labels[c_idx][0] + ")")
            a[cl_idx, c_idx + 1].legend(loc="best")
            
            f2, a2 = plt.subplots(1, 1, figsize=(5, 4))
            a2.set_title("Group " + cl + " Tversky indices " + labels[c_idx][0] + " " + labels[c_idx][1])
            a2.set_xlabel("Year")
            a2.set_ylabel("Tversky index (TI)")
            a2.plot(year_seq, tversky_indices_all[cl][combi[0]], label="TI (" + labels[c_idx][0] + ", " + labels[c_idx][1] + ")")
            a2.plot(year_seq, tversky_indices_all[cl][combi[1]], label="TI (" + labels[c_idx][1] + ", " + labels[c_idx][0] + ")")
            a2.legend(loc="best")            
            f2.savefig("tversky_indices_" + cl + "_" + combi[0] + "_" + combi[1] + ".pdf")
            plt.close(f2)
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    f.savefig("indices_all_figure.pdf")
    

def main():
    """load files"""
    level = "section"
    classification_matrix = scipy.sparse.load_npz("patent_classification_matrix_level_" + level + ".npz")    # matrix
    pddf = pd.read_pickle("CPC_sorted_green_patents_combined_df.pkl")    # dataframe
    with open("patent_classification_codes_level_" + level + ".pkl", "rb") as infile:
        classification_codes = pickle.load(infile)

    """overlaps for all codes and years (Envtech, IPCGI, Y Codes): {'111': 98094, '110': 52535, '101': 35298, '100': 36570, '011': 42345, '010': 454659, '001': 146203, '000': 5152545}"""
            
    """collect overlaps by classification code and year"""
    all_venns = {cl: {yr: {} for yr in range(1976, 2019)} for cl in classification_codes}
    jaccard_indices_all = {cl: {} for cl in classification_codes}
    tversky_indices_all = {cl: {} for cl in classification_codes}

    print("Everything prepared, commencing computation")
    for cl_idx, cl in enumerate(classification_codes):

        """obtain matching patent indices for class"""
        #column = classification_matrix[:, cl_idx].toarray().T[0]
        #patent_indices = np.where(column)
        patent_indices = scipy.sparse.find(classification_matrix[:, cl_idx])[0]
        
        """obtain dataframe subset"""
        df = pddf.iloc[patent_indices]

        jaccard_index = {"egy": [],  # all 3
                         "eg": [],   # envtech, IPC GI
                         "ey": [],   # envtech Y Codes
                         "gy": [],   # IPC GI, Y Codes
                         }
        tversky_index = {combi: [] for combi in ["eg", "ey", "gy", "ge", "ye", "yg"]}

        for year in range(1976, 2019):
            print("\rYear {3}, Section {0}/{1}: {2}".format(cl_idx + 1, len(classification_codes), cl, year), end="")
        
            """obtain dataframe subset"""
            df_year = df[df["granted year"]==year]

            """obtain venn quantities"""
            venn_q = {}
            for envtech_val in [True, False]:
                for IPCGI_val in [True, False]:
                    for Y_Code_val in [True, False]:
                        venn_code = str(int(envtech_val)) + str(int(IPCGI_val)) + str(int(Y_Code_val))
                        hits = len(df_year[(df_year["Envtech"]==envtech_val) & (df_year["IPCGI"]==IPCGI_val) & (df_year["Y_Codes"]==Y_Code_val)])
                        venn_q[venn_code] = hits
            f, a = plt.subplots(1, 1, figsize=(5, 4))
            a.set_title("Group " + cl + ", " + str(year))
            venn3(venn_q, set_labels = ('Envtech', 'IPC GI', 'Y Codes'), ax=a)
            f.savefig("venn_single" + "_" + cl + "_" + str(year) + ".pdf")
            plt.close(f)
            all_venns[cl][year] = venn_q

            """record indices"""
            jaccard_index["egy"].append(venn_q['111']/np.sum(list(venn_q.values())))
            jaccard_index["eg"].append((venn_q['111']+venn_q['110'])/ (np.sum(list(venn_q.values())) - venn_q['001']))
            jaccard_index["ey"].append((venn_q['111']+venn_q['101'])/ (np.sum(list(venn_q.values())) - venn_q['010']))
            jaccard_index["gy"].append((venn_q['111']+venn_q['011'])/ (np.sum(list(venn_q.values())) - venn_q['100']))
            tversky_index["eg"].append((venn_q['111']+venn_q['110'])/ (venn_q['111'] + venn_q['110'] + venn_q['101'] + venn_q['100']))
            tversky_index["ey"].append((venn_q['111']+venn_q['101'])/ (venn_q['111'] + venn_q['110'] + venn_q['101'] + venn_q['100']))
            tversky_index["gy"].append((venn_q['111']+venn_q['011'])/ (venn_q['111'] + venn_q['110'] + venn_q['011'] + venn_q['010']))
            tversky_index["ge"].append((venn_q['111']+venn_q['110'])/ (venn_q['111'] + venn_q['110'] + venn_q['011'] + venn_q['010']))
            tversky_index["ye"].append((venn_q['111']+venn_q['101'])/ (venn_q['111'] + venn_q['101'] + venn_q['011'] + venn_q['001']))
            tversky_index["yg"].append((venn_q['111']+venn_q['011'])/ (venn_q['111'] + venn_q['101'] + venn_q['011'] + venn_q['001']))

        jaccard_indices_all[cl] = jaccard_index
        tversky_indices_all[cl] = tversky_index

    print("\nDone. Saving")

    """pickle/save venn data"""
    with open("venn_data.pkl", "wb") as wfile:
        pickle.dump([all_venns, jaccard_indices_all, tversky_indices_all], wfile, protocol=pickle.HIGHEST_PROTOCOL)

    print("Done. Generating figures")
    """generate Jaccard/Tversky index plots"""
    generate_index_plots(jaccard_indices_all, tversky_indices_all)
    
    """generate combined figure"""
    n_classes = len(all_venns)
    n_years = len(all_venns[list(all_venns.keys())[0]])
    f, a = plt.subplots(n_classes, n_years, figsize=(5 * n_years, 4 * n_classes))
    for cl_idx, cl in enumerate(all_venns):
        for year_idx, year in enumerate(all_venns[cl]):
            a[cl_idx, year_idx].set_title("Group " + cl + ", " + str(year))
            venn_q = all_venns[cl][year]
            venn3(venn_q, set_labels = ('Envtech', 'IPC GI', 'Y Codes'), ax=a[cl_idx, year_idx])

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    f.savefig("venn_figure.pdf")


if __name__ == "__main__":
    main()
