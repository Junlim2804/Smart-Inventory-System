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
cur=con.cursor()
cur.execute("select format([date], 'MMMMyyyy'),Prediction from forecast where prod_id='pr1' and [date]>getdate()")
data=cur.fetchall()
hover1 = HoverTool(tooltips=[("Sales", "@y")])
X=[]
Y=[]
for i in data:
    X.append(i[0])
    Y.append(i[1])

#Y = y.iloc[-1:].values
p = figure(x_range=X, plot_height=400,x_axis_label='Month',x_minor_ticks=1,
         title="Forecast Sales",toolbar_location=None, tools=[hover1])

p.line(y=Y,x=X,line_width=2)

#p.y_range.start =0
show(p)



