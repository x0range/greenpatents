
# Green Patents Project

# Purpose

(todo)

# Install Dependencies

(todo)

# Date sources

(todo)

# Usage

Different scripts handle different aspects of the data parsing etc. They need to be run successively.

We could add a bash script, but experience shows that the entire proces is taking quite some time, requires some management but allows some parallelization. So far, it was convenient to do that manually.

Run in this order:

```## Obtain patent text

python3 download_and_parse/get_uspto_titles_and_abstracts.py

## Run keyword search

python3 detect/greenfinder.py

## Parse classifications

# This file can do distributed parsing; doing it on one core takes very long
python3 classifications/parse_CPC.py 

# Join resulting data
python3 classifications/join_CPC_dataframe.py
python3 classifications/join_CPC_matrices.py

## Parse citations

python3 citation_network/citation_parse_full_node_list.py
python3 citation_network/citation_parse.py

# Join resulting data
python3 citation_network/combine_citation_dataframe.py

## Parse remaining patent level data (value, dates, assignee data), combine dataframe

python3 data_frame/kogan_to_pandas.py
python3 data_frame/parse_dates_multithread.py
#python3 data_frame/parse_dates.py
python3 data_frame/assigneedataparser.py 

# Join everything
python3 data_frame/join_to_combined_dataframe.py

## Create citation pattern plots
python3 citation_network/citation_curves.py -s -f -l
python3 citation_network/citation_quantile_heatmap.py```
