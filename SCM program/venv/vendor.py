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
from flask_login import current_user,login_required
from flask import Flask, render_template,url_for,request,redirect,Blueprint,render_template,flash,session,current_app
from pmdarima.arima import auto_arima
from . import db
from .models import User

from . import role
vendor = Blueprint('vendor', __name__)
server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

@vendor.route('/vendor')
def vendorindex():
   return "vendor"

@vendor.route('/vendor/index')
@role("Vendor")
def index():
   return render_template('vendor/profile.html',data=current_user.vendorID)

@vendor.route('/vendorRequest')
@role("Vendor")
def vendorRequest():   
   cur = con.cursor()
   cur.execute("select * from product")
   data = cur.fetchall()
   uid=current_user.vendorID
   return render_template('/vendor/addRequest.html',data=data,uid=uid)


@vendor.route('/addRequest',methods=['POST'])
@role("Vendor")
def addRequest():
   #flash("Error")
   #return redirect(url_for('vendor.vendorRequest'))
   vid=request.form['vid']
   pid=request.form['pid']
   qty=request.form['qty']
   price=request.form['price']
   
   #con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur=con.cursor()
   try:
      cur.execute("insert into request values(CONCAT('R',next value for seq_request),?,?,?,?,getdate(),'P')",(vid,pid,price,qty))
      #insert into request values(next value for seq_request,'v1',100,10,getdate())
      con.commit()
      if(cur.rowcount):
         return redirect(url_for('vendor.showComplete'))
      else:
         return redirect(url_for('vendor.errorMessage'))
   except Exception as e: 
       session['errmsg'] = str(e)  
       return redirect(url_for('vendor.errorMessage'))

@vendor.route('/completeRequest')
@role("Vendor")
def showComplete():
    return "complete"

@vendor.route('/vendor/showStock')
@role("Vendor")
def showStock():
   if(current_user.vendorID is None):
      return redirect(url_for('auth.error'))

   
   
   #con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vendor_id='"+current_user.vendorID+"' order by receive_date asc")
   data = cur.fetchall()
   
   return render_template('vendor/showStock.html',data=data)

@vendor.route('/errorMsg')
@role("Vendor")
def errorMessage():
    messages = session['errmsg'] 
    flash(messages)
    return render_template("errorMessage.html")

@vendor.route('/vendor/adjustStock',methods=['GET'])
@role("Vendor")
def adjustStock():   
   vs_id=request.args.get('vs_id')
   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vs_id='"+vs_id+"'")
   data = cur.fetchall()
   return render_template('vendor/adjustStock.html',data=data)   

@vendor.route('/vendor/adjustStock',methods=['POST'])
@role("Vendor")
def adjustStocking():   
   #vs_id=request.form['vs_id']
   qty=request.form['qty']
   return qty  

@vendor.route('/vendor/dailyClosing')
@role('Vendor')
def dailyClosing():    
   cur = con.cursor()
   cur.execute("select * from vendor_sales where date=cast(getDATE() as date)")
   data=cur.fetchall()

   if(len(data)>0):
      return "<h1>CLOSING DONE TODAY</h1>"
   cur.execute("select * from v_vendor_stock where cur_quantity>0 and vendor_id='"+current_user.vendorID+"' order by vs_id asc")
   data = cur.fetchall()   
   return render_template('vendor/dailyClosing.html',data=data)

@vendor.route('/vendor/dailyClosing',methods=['POST'])
@role('Vendor')
def submitClosing():
   vs_id_list=request.form.getlist('vs_id[]')
   price_list= request.form.getlist('today_price[]')   
   qty_sales_list=request.form.getlist('qty_sales[]')
   qty_disposal_list=request.form.getlist('qty_disposal[]')
   qty_cur_list=request.form.getlist('qty_cur[]')
   a=''
   sql=""
   cur = con.cursor()
   try:
      for i in range(len(vs_id_list)) :
         a=a+str(vs_id_list[i])+str(price_list[i])+str(qty_sales_list[i])+str(qty_disposal_list[i])+str(qty_cur_list[i])
         sql="exec [prc_insertClosing] @vs_id='"+vs_id_list[i]+"',@qty_sales="+qty_sales_list[i]+",@unit_price="+price_list[i]+",@qty_disposal="+qty_disposal_list[i]
         print(sql)
         cur.execute(sql)
   except Exception as e:
      return str(e)
   cur.commit()
   cur.close()

   return dailyClosing()

@vendor.route('/testing')
def justTesting():
   df=pd.read_csv('forecast.csv',skiprows=1)
   return df.to_string()

   
@vendor.route('/showGraph',methods = ['GET'])
@role('Vendor')
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
