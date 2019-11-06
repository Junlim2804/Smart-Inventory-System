import pyodbc
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np
#bokeh import
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid,Range1d,DatetimeTickFormatter
from bokeh.models.widgets import Panel,Tabs
from bokeh.models.glyphs import VBar
from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
#flask import
from flask_login import login_required, current_user
from flask import Flask, render_template,url_for,request,redirect,Blueprint,render_template

from pmdarima.arima import auto_arima
from . import db
from .models import User
from . import role



main = Blueprint('main', __name__)

server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")




@main.route('/')
def index():
   return render_template('index.html')

@main.route('/profile')
@role('Admin')
def profile():
   return render_template('profile.html', name=current_user.name)

@main.route('/showGraph',methods = ['GET'])
@login_required
def showGraph():
   
   cur = con.cursor()
   cur.execute("select * from product")
   product = cur.fetchall()
   cur.execute("select DISTINCT year(send_date) from vendor_order order by year(send_date)")
   year=cur.fetchall()
   try:
      Product_ID=request.args.get('pid')
      syear=request.args.get('year')
   except Exception as e:
      return render_template("showGraph.html",product=product,year=year,data=e)
   
   if(Product_ID==None and syear==None):
      return render_template("showGraph.html",product=product,year=year)

   SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth] @year="+syear, con)
   
   df = pd.DataFrame(SQL_Query)
   
   X = df.columns[1:13].values
   y = df.loc[df['product_id'] == Product_ID].iloc[0,1:13].values
   #y = df.loc[0,1:13].values
   hover1 = HoverTool(tooltips=[("Quantity", "@top")])
   barchart = figure(x_range=X, plot_height=250, title="Stock Counts",
            toolbar_location=None, tools=[hover1])
   barchart.vbar(x=X, top=y, width=0.5)

   barchart.xgrid.grid_line_color = 'red'
   barchart.y_range.start = 0
   
   hover2 = HoverTool(tooltips=[("Quantity", "@y")])
   p = figure(plot_width=400, plot_height=400,x_range=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep',
       'oct', 'nov', 'dec'],tools=[hover2])
  
   # add a line renderer

   p.line(y=y,x=X,line_width=2)
   tab1 = Panel(child=barchart, title="Bar")
   tab2 = Panel(child=p, title="Line")
   tabs = Tabs(tabs=[tab1, tab2])
   script, div = components(tabs)

   #script2, div2 = components(p)
   return render_template("showGraph.html", bars_count=1,
                           the_div=div, the_script=script,product=product,year=year)

@main.route('/showStock')
@login_required
def showStock():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from v_warehouse_stock order by date_received asc")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)



@main.route('/showVendorRequest')
@login_required
def showVendorRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from request")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)

@main.route('/addstock')
@login_required
def addStock():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
   cur = con.cursor()
   cur.execute("select * from product")
   data = cur.fetchall()
   cur.execute("SELECT CAST(current_value as int) FROM sys.sequences WHERE name = 'seq_warehouse' ;")
   seq=cur.fetchval()
   seq='sk'+str(seq+1)
   cur.close()
   con.close()
   return render_template('addStock.html',data=data,seq=seq)
@main.route('/addingstock',methods = ['POST'])
@login_required
def addingStock():
   #Stock_ID=request.form['sid']
   Supplier_ID=request.form['sup_id']
   Prod_ID=request.form['pid']
   Receive_Date=request.form['drec']
   Condition=request.form['condition']   
   price=request.form['price']
   quantity=request.form['qty']
   
   
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur=con.cursor()
   
   try:
      cur.execute("insert into warehouse values(CONCAT('sk', Next value for seq_warehouse),?,?,?,?,?,?,?)",(Prod_ID,Receive_Date,Condition,price,quantity,quantity,Supplier_ID))
      con.commit()
      if(cur.rowcount):
         return ("Order sucessful placed")
      else:
         return "error"
   except Exception as e:
      return str(e)
      

@main.route('/addOrder',methods=['POST'])
@login_required
def addOrder():
   
   rid=request.form['rid']
   sid=request.form['sid']
   vid=request.form['vid']
   qty=request.form['qty']
   price=request.form['price']
   data=[rid,sid,vid,qty,price]
   return render_template('addOrder.html',data=data) 
   
@main.route('/PlaceOrder',methods=['POST'])
@login_required
def placeOrder():
   a=request.form['sdate']
   return a

@main.route('/home')
@login_required
def home():
   return render_template('index.html')

@main.route('/forecast')
@login_required
def forecast():   
   SQL_Query = pd.read_sql_query("select * from show_sales where prod_id='pr1'", con)
   df=pd.DataFrame(SQL_Query)
   df['date'] = pd.to_datetime(df['date'])
   df=df.drop(['prod_id'], axis=1)
   df=df.set_index('date')
   y=df
   y = df['Quantity'].resample('MS').sum()
   train=y[0:-2]
   valid=y[-12:]


   model = auto_arima(y[:-1], trace=True, start_p=3, start_q=3, start_P=1, start_Q=5,
                        max_p=7, max_q=7, max_P=7, max_order=20,max_Q=6,D=1,d=1, m=1,seasonal=True,
                        stepwise=True, error_action='ignore', suppress_warnings=True)
   model.fit(y[:-1])

   forecast = model.predict(n_periods=4)
   #HERE IS HARDCODE
   forecast = pd.DataFrame(forecast,index = ['2018-12-01','2019-01-01','2019-2-01','2019-3-01'],columns=['Prediction'])
   forecast.to_csv('forecast.csv')
   hover1 = HoverTool(tooltips=[("Sales", "@y")])
   X = ['December','January','February','March']

   Y = y.iloc[-1:].values
   Y= np.concatenate((Y, forecast['Prediction'].iloc[-3:].values))

   p = figure(x_range=X, plot_height=400,x_axis_label='Month',x_minor_ticks=1,
            title="Forecast Sales",toolbar_location=None, tools=[hover1])
   #barchart.vbar(x=X, top=Y, width=0.2)
   p.line(y=Y,x=X,line_width=2)
   
   p.y_range.start =0
   script, div = components(p)
   return render_template('showForecast.html',the_div=div, the_script=script)
@main.route('/confirmRequest')
@login_required
def confirmRequest():
   request_id=request.args.get('rid')
   if(request_id==None):
      return showRequest()
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from view_pending where request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select * from v_warehouse_stock where prod_id=? and cur_quantity>0 ",data[0][3])
   data2=cur.fetchall()
   cur.close()

   return render_template('confirmRequest.html',data=data,data2=data2)
   
@main.route('/showRequest')
@login_required
def showRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from view_pending")
   data = cur.fetchall()   

   con.close()
   return render_template('showRequest.html',data=data)

@main.route('/autoResponse')
@role('Admin')
def autoResponses():
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
   return showRequest()