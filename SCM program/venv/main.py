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
@role('Admin')
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
@role('Admin')
def showStock():
   cur = con.cursor()
   cur.execute("select * from v_warehouse_stock order by prod_id,date_received asc")
   data = cur.fetchall()
   cur.execute("select prod_id,prod_name,sum(cur_quantity) as 'Total Quantity' from v_warehouse_stock group by prod_id,prod_name order by prod_id" )
   product=cur.fetchall()
   cur.close()

   return render_template('showStock.html',data=data,data1=product)



@main.route('/showVendorRequest')
@role('Admin')
def showVendorRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from request")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)

@main.route('/addstock')
@role('Admin')
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
@role('Admin')
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
@role('Admin')
def addOrder():  
   rid=request.form['rid']
   #sid=request.form['sid']
   vid=request.form['vid']
   #qty=request.form['qty']
   #price=request.form['price']
   
   
   return render_template('addOrder.html',data=rid,data1=vid) 

@main.route('/addOrder')
@role('Admin')
def testingonly():  
   rid='R52'
   #sid=request.form['sid']
   vid='V180101001'
   #qty=request.form['qty']
   #price=request.form['price']
   
   
   return render_template('addOrder.html',data=rid,data1=vid)   
@main.route('/PlaceOrder',methods=['POST'])
@role('Admin')
def placeOrder():
   from datetime import datetime
   rid=request.form['rid']
   vid=request.form['vid']
   sdate=request.form['sdate']
   price=request.form['price']
   sid_list=request.form.getlist('sid[]')
   qty_list=request.form.getlist('qty[]')
   cur=con.cursor()
   sdate=sdate.replace("T"," ")

   try:
      for i in range(len(sid_list)):
         cur.execute("insert into vendor_order(Stock_id,Vendor_id,send_date,quantity,sell_price,request_id) values (?,?,?,?,?,?)",
         sid_list[i],vid,sdate,qty_list[i],price,rid)
   except Exception as e:
      cur.close()
      return str(e)
   cur.commit()
   return "<script>sessionStorage.setItem('stock_list', JSON.stringify([]));</script><h1>sucess</h1>"
@main.route('/home')
@role('Admin')
def home():
   return render_template('index.html')

@main.route('/forecast')
@role('Admin')
def forecast():   

   #con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
   pid = request.args.get("pid")
   if pid ==None:
      pid='pr1'
   
   cur=con.cursor()
   cur.execute("select * from product")
   product=cur.fetchall()
   cur.execute("select format([date], 'MMMMyyyy'),Prediction from forecast where prod_id='"+pid+"' and [date]>getdate()")
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
 
   
   p.y_range.start =2000
   script, div = components(p)
   return render_template('showForecast.html',the_div=div, the_script=script,data=product)
@main.route('/confirmRequest')
@role('Admin')
def confirmRequest():
   request_id=request.args.get('rid')
   if(request_id==None):
      return showRequest()

   cur = con.cursor()
   cur.execute("select * from view_pending where request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select * from v_warehouse_stock where prod_id=? and cur_quantity>0 ",data[0][3])
   data2=cur.fetchall()
   cur.close()

   return render_template('confirmRequest.html',data=data,data2=data2)

@main.route('/reject',methods=['POST'])
@role('Admin')
def reject():
   rid=request.form['rid']
   return rid
@main.route('/showRequest')
@role('Admin')
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

import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler


def monthlyforecast():
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


scheduler = BackgroundScheduler()
scheduler.add_job(func=monthlyforecast, trigger="cron", day=8)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())