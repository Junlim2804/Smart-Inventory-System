import pyodbc
import pandas as pd
import random
server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth] @year=2018", con)
df = pd.DataFrame(SQL_Query)


X = df.columns[1:13].values

# Activity: We experimented with the Hover Tool and the
# Box Select tool in the previous example, try to
# include those tools in this graph
# Number of world cups that the team has won
#y = df.iloc[1,1:13].values
y = df.loc[df['product_id'] == 'pr1'].iloc[0,1:13].values

print(y)



#show(column(tabs,button))
#script, div = components(barchart)




