FOR THE VERSION2 FOLDER DATA
<br>direction_data.zip and ranking_data.zip= RAW txt results<br>
<br>json_output.zip = results as json<br>
filtered_json.zip = filtered results after attention check

ROAD TO GINI PLOT
1) txt_to_json.py= converts txt to json files (creates json_output folder)
1) to_filter.py: filter the data based on attention checks via json_output, this script creates filtered_json
2) after obtained the filtered_json, use csv_maker.py to create ranking and direction csv documents to see all participants results includes trial_id, values, buttons etc
     <br>this py script creates a folder called csv_output which supposed to have ranking.csv and direction.csv<br>
3) go to csv_output/Processed_data
     <br>ginicoeff_analyses.py = script for creating one avg coeff value<br>
     plot_gini.py = creating boxplot with gini values of ranking and direction conditions. (the original fine we used earlier)
     <br>gini_barplot.py = creating bar plot with average Ginis per condition<br>
