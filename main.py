import pandas as pd
import os
import matplotlib.pyplot as plt

from tqdm import tqdm # Progress Bar

### Vars
file = "Sheet/pastdata.xlsx"
directory = "Sheet/"
plot_dir = "Plots/"

sheetnew_name = "new"
sheetold_name = "old"

month = "FY2024-P01"
exclude_month = "FY2024-P04"

#SQL Vars
sql_query = None

server = ""
database = ""
username = ""
auth = ""
driver = ""
query_url = "query.sql"

reset_rows = True
###

# Initialize the DataFrane from an SQL-Server
def connect_sql(server, database, username, auth, driver, query_url):
    # This function loads the DataFrame from the SQL Server as one entire dataframe
    with open("query.sql", "r") as q:
        query = q.read()
    conn_str = {
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'PORT=1433;'
        f'DATABASE={database};'
        f'UID={username};'
        f'AUTHENTICATION={Authentication}'
    }

    conn = pyodbc.connect(conn_str)

    df = pd.read_sql_query(query, conn)
    size = df.shape[0]

    return df, shape


# Initialize the DataFrame from a file
def init_df(file): # Use if you have 2 sheets with old and new data, else use connect_sql()
    # Set the old data to a DataFranme and drop all None Values
    df_old = pd.read_excel(file, sheet_name=sheetold_name).dropna()
    # Set the new data to a DataFrame and drop all None Values
    df_new = pd.read_excel(file, sheet_name=sheetnew_name).dropna()

    # Get the amount of rows from the new data. (Used to calculate the percentage of outliers in the end)
    size = df_new.shape[0]

    # Connect both dataframes. This will have the new DataFrame be in the bottom
    df = pd.concat([df_old, df_new]).reset_index(drop=True)
    # Remove a month you want to exclude
    df = df[df['FiscalMonth'] != exclude_month]
    
    # Return the vcreated Dataframd
    return df, size

def getOutlier(df, group, name, z_score_threshold, min_group_size, month, plot = False):
    # Currmonth is the last row of the group, or the latest month. We want to check if it corresponds with the month we want to check.
    months = group["FiscalMonth"].tolist()

    if month not in months:  # If it isn't the month we want to check, remove the whole group from df and return df

        df = df.drop(group.index)

        return df
    elif group.shape[0] < min_group_size:   # If the group has less rows than min_group_size, remove it from df and return df
        df = df.drop(group.index)

        return df
    month_index = group[group["FiscalMonth"] == month].index[0]

    median = group['hours'].drop(month_index).median() # Calculate the group median
    std = group['hours'].drop(month_index).std(ddof=0) # Calculate the group standard deviation
    z_score = abs((group["hours"]-median) / std)    # Calculate all z_scores from the entire group and save it to a var

    df.loc[group.index, "Z_Score"] = z_score    # Got to the original DataFrame and set the rows from the group to have the calculated Z_Score

    z_index = df.loc[month_index,"Z_Score"] # Get the index of the last month which will be the month you specified in the beginning

    if z_index >= z_score_threshold:    # Check if the z_index is greater than the threshhold you specified in the function call
        df.loc[month_index, 'Outlier_Flag'] = True  # If yes, then got to the original DataFrame and set the Outlier_Flag to True
    else:
        df.loc[month_index, 'Outlier_Flag'] = False # Else set the Outlier_Flag in the original Data_Frame to Flase

    if plot and z_index >= z_score_threshold:   # If you want to plot and the last month is an outlier:
        group = df.loc[group.index].sort_values("FiscalMonth")  # Get all rows from the group from the modified dataframe that has the z_indexes and outlier flags
        new_name = "".join("_".join(name).split(" "))   # Set the name of the group
        create_plot(group, new_name)  # Call the create_plot function with the group, the name and the plot directory
    return df   # Return the modified dataframe

def createFile(df, excel_file_directory): # Create the file with all anomalies in the end
    name = plot_dir
    out_file = f'{excel_file_directory}{name}'  # Path to file
    df = df.sort_values(by=["Segment", "DeliveryOrg", "ServiceType", "DeliveryAreaName", "FiscalMonth"])    # Sort the DataFrame so the file is all groups after each other
    df.to_excel(out_file, index=False)  # Create the file
    return True
    
def get_percentage_outliers(df, size):
    return (df["Outlier_Flag"].sum() / size) * 100 # Return the sum of all Outliers (False = 0; True = 1) and divide it by the total amount of the rows in the 'new' datasheet --> You will get the percentage of outliers in the Dataframe

def create_plot(group, name, plot_dir): # Create the plot

    fig, ax1 = plt.subplots()   # Get the X-Axis of the plot

    ax2 = ax1.twinx()   # Set the second X-Axis to be the same as the first one

    ax1.plot(group["FiscalMonth"].tolist(), group["hours"].tolist(), label="Hours", color="g")  # Plot the hours with the x of month
    ax2.plot(group["FiscalMonth"].tolist(), group["Z_Score"].tolist(), label="z_score", color="r")  # Plot the z_score to the x of month

    # We have to y-Axes as the Z_Index is much smaller than hours, so we can compare them both, as now the z_index gets scaled to graph size

    # Set the labels
    ax1.set_xlabel("Months")
    ax1.set_ylabel("Hours", color="g")
    ax2.set_ylabel("Z_Score", color="r")

    # Rotate x-axis labels to prevent z-fighting
    ax1.set_xticklabels(group["FiscalMonth"].tolist(), rotation=90)

    # Title the plot with the group name
    plt.title(name)
    # Set it to tight layout, so everything is in the image of the plot
    plt.tight_layout()
    # Save it to the directory with the group name
    plt.savefig(f"{plot_dir}{name}.png")
    # Close the plot
    plt.close()
    return True

# Get the DataFrame with the size of the new DataSheet
df, size = init_df(file)

# Group them
df_sorted = df.groupby(by=["Segment","DeliveryOrg","ServiceType","DeliveryAreaName"])
# Get all group names, to allow iterating
df_keys = df_sorted.groups.keys()
# Iterate trough all groups

for group_name in tqdm(list(df_keys), desc="Processing groups", unit="group"):
    # Syntax : getOutlier(Dataframe, group, name of the group, z-index-threshhold, month that is searched, do you want to plot all ouliers, plot directory)
    df = getOutlier(df, df_sorted.get_group(group_name), group_name, 2.5, 4, month, False, plot_dir)
# The final DataFrame will have many missing and skipping rows, so we could reset the indexes. 
# But if you want to compare to the original DataFrame then specify reset_rows to False on top.
if reset_rows:
    df = df.reset_index(drop=True)
   
# Print the percentage of outliers
print("Anomaly Percentage: ","%.2f" % get_percentage_outliers(df, size) + "%")

# Create the DataFrame in an excel file
createFile(df, directory, "anomalies.xlsx")

