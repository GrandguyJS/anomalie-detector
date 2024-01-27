import pandas as pd
import os

# Set the file path
file = "Sheet/pastdata.xlsx"
directory = "Sheet/"

anomalies = pd.DataFrame(["Segment","FiscalMonth","DeliveryOrg","ServiceType","DeliveryAreaName","hours","New","Z_Score","Outlier_Flag"])

def init_df(file):
    df_old = pd.read_excel(file, sheet_name='old').dropna()
    df_old["New"] = False

    df_new = pd.read_excel(file, sheet_name='new').dropna()
    df_new["New"] = True
    new_rows = df_new.shape[0]

    df = pd.concat([df_old, df_new])

    return df, new_rows

def getOutlier(group, z_score_threshold):

    new = group["New"].tail(1).iloc[0]
    if not new:
        return
    if group.shape[0] == 2:
        return
    
    median = group['hours'].median()
    std = group['hours'].head(group.shape[0]-1).std(ddof=0)
    hours = group.tail(1)["hours"]

    z_index = abs((hours.iloc[0]-median) / std)

    df.at[hours.index[0], "Outlier_Flag"] = z_index >= z_score_threshold
    df.at[hours.index[0], "Z_Score"] = z_index

    if z_index >= z_score_threshold:
       anomalies = pd.concat([anomalies, group])

    return

def createFile(excel_file_directory, name):
    out_file = f'{excel_file_directory}{name}'
    df.to_excel(out_file, index=False)
    return
    
def get_percentage_outliers(df):
    return (df["Outlier_Flag"].sum() / size) * 100

# Get all groups
df, size = init_df(file)



df_sorted = df.groupby(by=["Segment","DeliveryOrg","ServiceType","DeliveryAreaName"])

df_keys = df_sorted.groups.keys()


for group_name in df_keys:
    getOutlier(df_sorted.get_group(group_name), 2.5)
   
print(get_percentage_outliers(df))

createFile(directory, "anomalies.xlsx")

