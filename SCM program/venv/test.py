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
iris_df = df.copy()
feature_names = iris_df.columns[0:-1].values.tolist()
def create_figure(current_feature_name, bins):
   p = figure(x_range=current_feature_name,legend='top_right',width=600,height=400)
   # Set the x axis label
   p.xaxis.axis_label = current_feature_name
   # Set the y axis label
   p.yaxis.axis_label = 'Count'
   return p

teams = ['Argentina', 'Brazil', 'Spain', 'Portugal']
# Activity: We experimented with the Hover Tool and the
# Box Select tool in the previous example, try to
# include those tools in this graph
# Number of world cups that the team has won
wc_won = [5, 3, 4, 2]
# Setting toolbar_location=None and tools="" essentially
# hides the toolbar from the graph
barchart = figure(x_range=teams, plot_height=250, title="WC Counts",
         toolbar_location=None, tools="")
barchart.vbar(x=teams, top=wc_won, width=0.5)
# Acitivity: Play with the width variable and see what
# happens. In particular, try to set a value above 1 for
# it 
barchart.xgrid.grid_line_color = 'red'
barchart.y_range.start = 0
script, div = components(barchart)
show(barchart)


