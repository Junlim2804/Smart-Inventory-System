import pyodbc
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np
from pmdarima.arima import auto_arima
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid,Range1d,DatetimeTickFormatter
from bokeh.models.widgets import Panel,Tabs
from bokeh.models.glyphs import VBar
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.io import show

server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
cur = con.cursor()
cur.execute("select distinct(prod_id) from show_sales")
data=cur.fetchall()
for prod_id in data:
    SQL_Query = pd.read_sql_query("select * from show_sales where prod_id='"+prod_id[0]+"'", con)
    df=pd.DataFrame(SQL_Query)
    df['date'] = pd.to_datetime(df['date'])
    df=df.drop(['prod_id'], axis=1)
    df=df.set_index('date')

    y=df
    y = df['Quantity'].resample('MS').sum()
    model = auto_arima(y, trace=True, start_p=3, start_q=3, start_P=1, start_Q=5,
                        max_p=7, max_q=7, max_P=7, max_order=20,max_Q=6,D=1,d=1, m=1,seasonal=True,
                        stepwise=True, error_action='ignore', suppress_warnings=True)
    model.fit(y)
    forecast = model.predict(n_periods=4)
    date_index=y[-1:].index
    x_index=[]
    date_index=date_index+1
    for i in range(4):
        x_index.append(str((date_index+i).date[0]))
    forecast=forecast.round()
    forecast=forecast.astype(int)
    d = {'Date': x_index, 'Prediction': forecast}
    result = pd.DataFrame(data=d)
    result.insert(loc=0, column='prod_id', value=prod_id[0])

    for index,row in result.iterrows():
        cur.execute("SET NOCOUNT ON exec prc_insertForecast @prod_id=?,@fdate=?,@no=?",row['prod_id'],row['Date'],row["Prediction"])
cur.commit()
cur.close()