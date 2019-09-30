import pyodbc
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import random
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure,show

from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource


server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth]", con)
df = pd.DataFrame(SQL_Query)


X = df.columns[1:13].values
# Activity: We experimented with the Hover Tool and the
# Box Select tool in the previous example, try to
# include those tools in this graph
# Number of world cups that the team has won
y = df.iloc[1,1:13].values
# Setting toolbar_location=None and tools="" essentially
# hides the toolbar from the graph
barchart = figure(x_range=X, plot_height=250, title="Stock Counts",
         toolbar_location=None, tools="")
barchart.vbar(x=X, top=y, width=0.5)
# Acitivity: Play with the width variable and see what
# happens. In particular, try to set a value above 1 for
# it 
barchart.xgrid.grid_line_color = 'red'
barchart.y_range.start = 0
script, div = components(barchart)
show(barchart)


