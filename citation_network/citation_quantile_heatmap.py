import numpy as np
import pandas as pd
import matplotlib
from matplotlib import gridspec

""" Set to non-GUI environment before importing pyplot"""
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def quantile_heatmap(df, vs, separ, name_postfix):
    """"""
    years = np.arange(1976, 2019)
    quantiles = [.5, .8, .9, .95, .98, .99, .995, .998, .999]
    
    """collect data"""
    plot_data = pd.DataFrame(index=quantiles)
    for year in years:
        dfp = df[df["granted year"] == year]
        qs = dfp[vs].quantile(quantiles)
        pdseries = []
        for q in qs:
            dfps = dfp[dfp[vs]>= q]
            pdseries.append(dfps[separ].sum()/len(dfps))
        plot_data[year] = pdseries
    
    """heatmap plot"""
    plotfilename = "Shares_by_Quantile_Year" + name_postfix + ".pdf"
    plot_title = "Shares of green patents by quantile and year - " + separ
    print("\nPlotting " + plot_title)
    
    plt.figure()
    plt.pcolor(plot_data)
    xlabels = [cat if i//5==i/5. else "" for i, cat in enumerate(plot_data.columns)]
    plt.yticks(np.arange(0.5, len(plot_data.index), 1), plot_data.index)
    plt.xticks(np.arange(0.5, len(plot_data.columns), 1), xlabels)
    plt.ylabel("Quantiles by # of citations")
    plt.colorbar()
    plt.title(plot_title)
    plt.tight_layout()
    plt.savefig(plotfilename)

def main():
    df = pd.read_pickle("green_patents_combined_df.pkl")
    df = df[['granted year', 'Received citations (all)', 'Received citations (assignee citations only)', 'Shapira et al. GI pattern', 'envtech', 'IPCGI']]
    df['Received citations (all)'].fillna(0, inplace=True)
    df['Received citations (assignee citations only)'].fillna(0, inplace=True)


    voluntary_settings = ['Received citations (all)', 'Received citations (assignee citations only)']
    voluntary_setting_name_postfix = {'Received citations (all)':'', 'Received citations (assignee citations only)':'_voluntaryonly'}
    green_separations = ['Shapira et al. GI pattern', 'envtech', 'IPCGI']
    green_separation_name_postfix = {'Shapira et al. GI pattern': '_keyword_shapira', 'envtech': '_envtech', 'IPCGI': '_IPCGI'}

    for vs in voluntary_settings:
        for separ in green_separations:
            quantile_heatmap(df, vs, separ, green_separation_name_postfix[separ] + voluntary_setting_name_postfix[vs])

if __name__ == '__main__':
    main()
