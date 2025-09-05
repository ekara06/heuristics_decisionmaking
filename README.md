jatos_results_data_20250901104501.zip = RAW result txt files
<br>input_jsons.zip = results as json<br>
filtered_json = filtered results after attention check

ROAD TO GINI PLOT
1) process.py: filter the data based on attention checks via input_json, this script creates filtered_json
2) after obtained the filtered_json, use csv_maker.py to create ranking and direction csv documents to see all participants results includes trial_id, values, buttons etc
     this py script creates a folder called csv_output which supposed to have ranking.csv and direction.csv
3) go to csv_output/Processed_data
     ginicoeff_analyses.py = script for creating one avg coeff value
     plot_gini.py = creating boxplot with gini values of ranking and direction conditions. (the original fine we used earlier)
     gini_barplot.py = creating bar plot with average Ginis per condition
