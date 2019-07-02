import pyodbc
import pandas as pd


server = 'tcp:fypscm.database.windows.net,1433'
database = 'SCMdb'
username = 'jl2804'
password = 'TauJun2804'
driver= '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
cursor = cnxn.cursor()
sqlstring="EXEC [dbo].[prc_getsalesbymonth] @proc = N'sk1'"
'''

#sqlstring="select * from vendor_order"
cursor.execute(sqlstring)

row = cursor.fetchall()

for idx in range(len(row)): #[0, 1, ..., 9,] 
    print(row[idx]) # to get the first 10
'''
SQL_Query = pd.read_sql_query("select * from warehouse", cnxn)
df = pd.DataFrame(SQL_Query)
print(df)