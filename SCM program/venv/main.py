from flask import Flask, render_template,url_for,request
import pyodbc
from bokeh.plotting import figure
from bokeh.embed import components
import pandas as pd
import random
from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure

from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource


app = Flask(__name__)
server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
#SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth]", con)
#df = pd.DataFrame(SQL_Query)
#iris_df = df.copy()
#feature_names = iris_df.columns[0:-1].values.tolist()


@app.route('/test')
def index():
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
   bars_count=1
   return render_template("test.html", bars_count=bars_count,
                           the_div=div, the_script=script)
#
#SQL_Query=pd.read_sql_query("set nocount on exec [prc_getsalesbymonth] ",con)
#df=pd.DataFrame(SQL_Query)
#df=pd.DataFram(SQL_Query)
#iris_df=df.copy()
#feature_names=iris_df.column[0:-1].values.tolist()
## Determine the selected feature
#current_feature_name = "Jan"
#
## Create the plot
#plot = create_figure(current_feature_name, 10)
#	
## Embed plot into HTML via Flask Render
#script, div = components(plot)
#return render_template("iris_index1.html", script=script, div=div, feature_names=feature_names,  current_feature_name=current_feature_name)


@app.route('/showStock')
def showStock():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("SELECT * FROM warehouse")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)
@app.route('/addstock',methods = ['POST'])
def addStock():
   Stock_ID=request.form['sid']
   Prod_ID=request.form['pid']
   Receive_Date=request.form['drec']
   Condition=request.form['condition']   
   price=request.form['price']
   quantity=request.form['qty']
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur=con.cursor()
   try:
      cur.execute("insert into warehouse values(?,?,?,?,?,?)",(Stock_ID,Prod_ID,Receive_Date,Condition,price,quantity))
      con.commit()
      if(cur.rowcount):
         return ("Order sucessful placed")
      else:
         return "error"
   except:
      return "error in sql"

@app.route('/addRequest',methods=['POST'])
def addRequest():
   
   vid=request.form['vid']
   pid=request.form['pid']
   qty=request.form['qty']
   price=request.form['price']
   
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur=con.cursor()
   try:
      cur.execute("insert into request values(CONCAT('R',next value for seq_request),?,?,?,?,getdate(),'P')",(vid,pid,price,qty))
      #insert into request values(next value for seq_request,'v1',100,10,getdate())
      con.commit()
      if(cur.rowcount):
         return ("Request sucessful placed")
      else:
         return "error"
   except Exception as e:
      return str(e)

@app.route('/addOrder',methods=['POST'])
def addOrder():
   
   rid=request.form['rid']
   sid=request.form['sid']
   vid=request.form['vid']
   qty=request.form['qty']
   price=request.form['price']
   data=[rid,sid,vid,qty,price]
   return render_template('addOrder.html',data=data) 
   
@app.route('/PlaceOrder',methods=['POST'])
def placeOrder():
   a=request.form['sdate']
   return a

@app.route('/home')
def home():
   return render_template('index.html')

@app.route('/confirmRequest')
def confirmRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from view_pending")
   data = cur.fetchall()
   cur.execute("select * from v_warehouse_stock where prod_id=?",data[0][3])
   data2=cur.fetchall()
   cur.close()
   con.close()
   return render_template('confirmRequest.html',data=data,data2=data2)

if __name__ == '__main__':
   app.run(debug = True)