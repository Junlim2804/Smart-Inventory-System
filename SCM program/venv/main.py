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
from pmdarima.arima import auto_arima
import matplotlib.pyplot as plt
import numpy as np
from bokeh.models import HoverTool


app = Flask(__name__)
server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

from bokeh.models import DatetimeTickFormatter
from bokeh.models.widgets import Panel,Tabs
from bokeh.layouts import column
@app.route('/showGraph',methods = ['GET'])
def index():

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

@app.route('/showStock')
def showStock():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from v_warehouse_stock order by date_received asc")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)

@app.route('/showVendorRequest')
def showVendorRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from request")
   data = cur.fetchall()
   cur.close()
   con.close()
   return render_template('showStock.html',data=data)

@app.route('/addstock')
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
@app.route('/addingstock',methods = ['POST'])
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

@app.route('/vendorRequest')
def vendorRequest():
   cur = con.cursor()
   cur.execute("select * from product")
   data = cur.fetchall()
   return render_template('addRequest.html',data=data)



@app.route('/forecast')
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
@app.route('/confirmRequest')
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
   con.close()
   return render_template('confirmRequest.html',data=data,data2=data2)
@app.route('/showRequest')
def showRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from view_pending")
   data = cur.fetchall()
   
   cur.close()
   con.close()
   return render_template('showRequest.html',data=data)
if __name__ == '__main__':
   app.run(debug = True)