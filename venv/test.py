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
cur.execute("select vs.vs_id,vs.date,vs.quantity as 'sales', vd.quantity as 'Disposal',unit_price from vendor_disposal vd,vendor_sales vs where vs.vs_id=vd.vs_id and vs.date=vd.date")
data=cur.fetchall()
for i in data:
    print(i)




