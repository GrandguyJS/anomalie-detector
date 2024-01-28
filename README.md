# How to run the script
### Excel:
If you want to get the data from an csv/slsx file, change the file variable to the sheet and the directory to its directory. Then set the plot_directory and the different sheet names of old and new data. You can specify the month to search anomalies in, and a month to exclude. 

### SQL:
If you want to do an SQL_Query then change the variables below the other ones and instead of init_df() you have to use connect_sql(). Now in the code I did, I join old and new data together and put it into a DataFrame. 

### Grouping:
I then group the dataframe by ["Segment","DeliveryOrg","ServiceType","DeliveryAreaName"]. Then I get all group names and iterate trough the names. When iterating trough the names the code withh call the outlier function with the DataFrame, the group with the name in the iteration, the group name, the z_score_threshhold, the min_group_value, the month to search, a boolean if you want to plot the anomalies. I used tqdm to create a progress bar. 

### GetOutlier() function:
In the getOutlier() function, the original DataFrame gets edited. If a group hasn't got the month you are looking for, it gets deleted from the DataFrame and if a group is smaller than the min_group_var it also gets removed from the DataFrame. The Z_Scores get assigned directly to the DataFrame aswell as the OutlierFlag. Note that we only check if the month specified is an Outlier and not every. But you can simply change this by uncommenting line 91 in main.py and commenting line 92. Then if the month is an anomaly it gets ploted with the createPlot() function.

### Creating the file:
After the whole iteration we have a DataFrame that has just the relevant groups and show us the outliers. We reset the indexes, as we have deleted a few groups. Then we call the createFile() function where we specify the DataFrame and the filename that usually is "anomalies.xlsx". In the function the DataFrame gets sorted by ["Segment", "DeliveryOrg", "ServiceType", "DeliveryAreaName", "FiscalMonth"] to ensure a group-like structure in the sheet. At last we create the file and return True. 

That's all!

# Code structure
# 1. Initialize the DataFrame from Sheet or SQL_Server
-   ### 1.1 Load new and old data into a DataFrame
-   ### 1.2 get the size of the new data
-   ### 1.3 Concatenate both DataFrames --> Newer dataframe on the bottom
-   ### 1.4 Remove the month to be excluded
-   ### 1.5 Return the DataFrame and its size
# 2. Convert DataFrame into groups
-   ### 2.1 Group the DataFrame by selected groups
-   ### 2.2 Get all group names
-   ### 2.3 Iterate trough all names
-   ### 2.4 Use tqdm to create a progress bar
-   ### 2.5 Call the Outlierfunction on each group
# 3. Get the outlier of a group
-   ### 3.1 Get all months from the group
-   ### 3.2 Check if the month to be checked is included in the group
-   ### 3.3 Remove the group from the DataFrame if no month corresponds
-   ### 3.4 Check if the group size is bigger or equal to min_group_size
-   ### 3.5 Remove it from the original DataFrame if it is smaller
-   ### 3.6 Get the rownumber of the object we want to check
-   ### 3.7 Calculate the median of the group without the object 
-   ### 3.8 Calculate the standard deviation without the object
-   ### 3.9 Calculate the z-scores for all rows in the group
-   ### 3.10 Set the Z_Scores of all items of the group in the DataFrame
-   ### 3.11 Get the Z_Score of the object to be checked
-   ### 3.12 Check if the Z_Score is greater than the threshhold
-   ### 3.13 Set the Outlier_Flag of the object in the DataFrame
-   ### 3.14 Check if we want to plot and if it is an anomaly
-   ### 3.15 Sort the group by months
-   ### 3.16 Get the plot name
-   ### 3.17 Call create_plot() function
-   ### 3.18 return the updated DataFrame (with Z_Scores and Outlier_Flags)
# 4. Creating the plot
-   ### 4.1 Get the x-Axis of the plot
-   ### 4.2 Create a second x-Axis to be the same as the first one
-   ### 4.3 Plot the hours to months
-   ### 4.4 Plot the Z_Scores to months
-   ### 4.5 Set X_Label
-   ### 4.6 Set Y_Label 1
-   ### 4.7 Set Y_Label 2
-   ### 4.8 Rotate the X_Labels by 90 degrees to prevent overlapping
-   ### 4.9 Title the plot
-   ### 4.10 Set to tight_layout to make the image contain the entire plot
-   ### 4.11 Save the plot to path with groupname as filename
-   ### 4.12 Close the plot
-   ### 4.13 return True
# 5. Anomaly Percentage and mapping the DataFrame to a file
-   ### 5.1 Check if we want to reset rows and do accordingly
-   ### 5.2 Call get_percentage_outliers(DataFrame, Size)
-   ### 5.2.1 This will divide the sum of the Outliers by the Size of Newdata
-   ### 5.3 Print the percentage
-   ### 5.4 Call createFile(DataFrame, file_directory, file_name)
-   ### 5.4.1 Set the file_path + file_name
-   ### 5.4.2 Sort the entire DataFrame to group_like structure
-   ### 5.4.3 Create the file
-   ### 5.4.4 Return True
#
Created by [GrandguyJS](https://github.com/GrandguyJS)
#
Readers Notes:
The algorithm used to calculate the anomaly worked as follows. You subtract the median of the group from the hours_amount of the object you want to check. Then you divide with the standard deviation of the group and take the absolute value. This will get you the Z_Score of the object. We want to check if this Z_Score is greater than a threshhold you can assign. A useful threshhold is from 2.5 to 3.0.

