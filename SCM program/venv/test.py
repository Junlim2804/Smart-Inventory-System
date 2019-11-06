import pyodbc
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np



server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

cur = con.cursor()
cur.execute("select sum(cur_quantity) from warehouse where prod_id='pr1' group by prod_id ")
qtyitem=cur.fetchall()
qty_stock=qtyitem[0][0]
cur.execute("select * from view_pending where s")
data = cur.fetchall()
df=pd.read_csv('../forecast.csv',skiprows=1,index_col=False)
qty_forecast=int(df.iloc[-1,1])

qty_request=data[0][5]

if((qty_stock-qty_forecast)>qty_request):
    cur.execute("insert into vendor_order values('sk1','"+str(data[0][1])+"',GETDATE(),"+str(data[0][5])+",null,20,'A')")
    cur.execute("update request set status='A' where request_id='"+data[0][0]+"'")
cur.commit()