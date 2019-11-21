import pyodbc
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components


server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
cursor = cnxn.cursor()
sqlstring="EXEC [dbo].[prc_getsalesbymonth] "
'''

#sqlstring="select * from vendor_order"
cursor.execute(sqlstring)

row = cursor.fetchall()

for idx in range(len(row)): #[0, 1, ..., 9,] 
    print(row[idx]) # to get the first 10
'''
SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth]", cnxn)
df = pd.DataFrame(SQL_Query)
iris_df = df.copy()
feature_names = iris_df.columns[0:-1].values.tolist()
print(feature_names)

current_feature_name = "Jan"
plot = create_figure(current_feature_name, 10)
script, div = components(plot)
def create_figure(current_feature_name, bins):
   p = figure(x_range=current_feature_name,legend='top_right',width=600,height=400)
   # Set the x axis label
   p.xaxis.axis_label = current_feature_name
   # Set the y axis label
   p.yaxis.axis_label = 'Count'
   return p