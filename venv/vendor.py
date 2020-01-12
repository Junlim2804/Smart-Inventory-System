import pyodbc
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np
from math import pi
#bokeh import
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid,Range1d,DatetimeTickFormatter,DaysTicker, FuncTickFormatter
from bokeh.palettes import Category20
from bokeh.transform import cumsum
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
   return index()

@vendor.route('/vendor/index')
@role("Vendor")
def index():   
   cur = con.cursor()
   cur.execute("select sum(quantity*unit_price) from vendor_sales where month(date)=month(getdate()) and year(date)=year(getdate())")
   sales=cur.fetchone()
   cur.execute("select sum(quantity) from vendor_disposal where month(date)=month(getdate()) and year(date)=year(getdate())")
   disposal=cur.fetchone()
   cur.execute("select count(*) from request where status='P' and vendor_id=?",current_user.vendorID)
   pending=cur.fetchone()
   cur.execute("select count(*) from request where status='A' and vendor_id=?",current_user.vendorID)
   shipped=cur.fetchone() 
   cur.execute("select date,sum(unit_price*quantity) from vendor_sales where month(date)=month(getdate()) and year(date)=year(getdate()) group by date")
   data=cur.fetchall()
   X=[]
   y1=[]
   for i in data:
      X.append(i[0])
      y1.append(i[1])
   cum = np.cumsum(y1)
   hover2 = HoverTool(tooltips=[("Sales", "@y")])
   p = figure(plot_width=400, plot_height=400,tools=[hover2], sizing_mode='stretch_both')
   p.xaxis.formatter=DatetimeTickFormatter(
         days=["%d %b"],
         months=["%d %b"],
         years=["%d %b"],
      )
      # add a line renderer
   p.toolbar_location = None
   p.line(y=cum,x=X,line_width=2)
   script, div = components(p)


   SQL_Query = pd.read_sql_query("select p.prod_name,sum(quantity*unit_price) from vendor_sales vs,vendor_store va,warehouse w,Product p where month(date)=month(getdate()) and year(date)=year(getdate()) and vs.vs_id=va.vs_id and va.Stock_id=w.stock_id and p.prod_id=w.prod_id group by p.prod_name", con)   
   df = pd.DataFrame(SQL_Query)
   df.columns = ['item','Sales']
   df['angle'] = df['Sales']/df['Sales'].sum() * 2*pi
   df['color'] = Category20[len(df)]
   pie = figure(plot_height=350, toolbar_location=None,
           tools="hover", tooltips="@item: RM@Sales", x_range=(-0.5, 1.0), sizing_mode='stretch_both')

   pie.wedge(x=0, y=1, radius=0.4,
         start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
         line_color="white", fill_color='color', source=df,legend='item')

   pie.axis.axis_label=None
   pie.axis.visible=False
   pie.grid.grid_line_color = None
   script1, div1 = components(pie)
   return render_template('vendor/profile.html',data=current_user.vendorID,sales=sales,disposal=disposal,pending=pending,shipped=shipped,the_div=div, the_script=script,revenue=data,the_div1=div1, the_script1=script1)

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
   

   cur=con.cursor()
   try:
      cur.execute("insert into request values(CONCAT('R',next value for seq_request),?,?,?,?,getdate(),'P',null)",(vid,pid,price,qty))
      #insert into request values(next value for seq_request,'v1',100,10,getdate())
     
      if(cur.rowcount):
         con.commit()
         flash("Request Sent")         
         return redirect(url_for('vendor.vendorRequest'))
      else:
         cur.close()
         return redirect(url_for('vendor.errorMessage'))
   except Exception as e: 
       session['errmsg'] = str(e)  
       cur.close()
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
 

   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vendor_id='"+current_user.vendorID+"' and receive_date is not NULL order by receive_date asc")
   data = cur.fetchall()
   cur.execute("select prod_id,prod_name,sum(cur_quantity) as 'Total Quantity' from v_vendor_stock where vendor_id='"+current_user.vendorID+"'  group by prod_id,prod_name" )
   product=cur.fetchall()
   cur.close()
   
   return render_template('vendor/showStock.html',data=data,data1=product)

@vendor.route('/vendor/showStockTable')
@role("Vendor")
def showStockTable():
   if(current_user.vendorID is None):
      return redirect(url_for('auth.error')) 
 

   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vendor_id='"+current_user.vendorID+"' and receive_date is not NULL order by receive_date asc")
   data = cur.fetchall()
   cur.close()
   
   return render_template('vendor/showStockTable.html',data=data)

@vendor.route('/errorMsg')
@role("Vendor")
def errorMessage():
    messages = session['errmsg'] 
    flash(messages)
    return render_template("errorMessage.html")


@vendor.route('/vendor/dailyClosing')
@role('Vendor')
def dailyClosing():     
   cur = con.cursor()
   cur.execute("select * from vendor_sales where date=cast(getDATE() as date)")
   data=cur.fetchall()

   if(len(data)>0):
     flash('Closing Done Today')
     return redirect(url_for('vendor.index'))
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
   flash("Closing")
   return render_template('vendor/dailyClosing.html',data=data)

@vendor.route('/testing')
def justTesting():
   df=pd.read_csv('forecast.csv',skiprows=1)
   return df.to_string()

   
@vendor.route('/vendor/showGraph',methods = ['GET'])
@role('Vendor')
def showGraph():
   Product_ID=request.args.get('pid')
   sdate=request.args.get('sdate')  
   edate=request.args.get('edate') 
   cur = con.cursor()
   cur.execute("select * from product")
   product = cur.fetchall()

   if(sdate==None and edate==None):
      cur.execute("select TOP 7 * from v_vendor_closing where prod_id=?",product[0][0])
   else: 
      cur.execute("select * from v_vendor_closing where prod_id=? and date>=? and date<=?",Product_ID,sdate,edate)
  
   
   data=cur.fetchall()  


   X=[]
   y1=[]
   y2=[]
   for i in data:      
      X.append(i[1])
      y1.append(i[2])
      y2.append(i[3])

   hover1 = HoverTool(tooltips=[("Quantity", "@top")])
   barchart = figure(x_axis_type='datetime',plot_height=450, title="Stock Counts",
         toolbar_location=None, tools=[hover1], sizing_mode='stretch_both')
   barchart.vbar(x=X, top=y1, width=70400000)

   barchart.y_range.start = 0
   barchart.xaxis.ticker = DaysTicker(days=np.arange(1,32))
   barchart.xaxis.major_label_orientation = 1.5
   barchart.xaxis.formatter=DatetimeTickFormatter(
        days=["%d %B"],
        months=["%d %B"]
        
    )
   
   hover2 = HoverTool(tooltips=[("Quantity", "@y")])
   p = figure(x_axis_type='datetime',plot_height=450, title="Stock Counts",
            toolbar_location=None, tools=[hover1], sizing_mode='stretch_both')
   p.vbar(x=X, top=y2, width=70400000)
   p.xaxis.ticker = DaysTicker(days=np.arange(1,32))
   p.xaxis.major_label_orientation = 1.5
   p.y_range.start = 0
   p.xaxis.formatter=DatetimeTickFormatter(
         days=["%d %B %Y"],
         months=["%d %B %Y"]
        
      )

   tab1 = Panel(child=barchart, title="Sales")
   tab2 = Panel(child=p, title="Dispose")
   tabs = Tabs(tabs=[tab1, tab2])   
   script, div = components(tabs)

   #script2, div2 = components(p)
   return render_template("vendor/showGraph.html", bars_count=1,
                           the_div=div, the_script=script,product=product)


   
@vendor.route('/vendor/showAllRequest')
@role('Vendor')
def showRequestHistory():
   cur = con.cursor()
   if(current_user.vendorID is None):
      return redirect(url_for('auth.error'))
   cur.execute("select * from v_requesthistory where vendor_id=?",current_user.vendorID)
   data = cur.fetchall()   

   cur.close()
   return render_template('vendor/showPurchaseOrder.html',data=data)

@vendor.route('/vendor/showPending')
@role('Vendor')
def showPending():
   cur = con.cursor()
   if(current_user.vendorID is None):
      return redirect(url_for('auth.error'))
   cur.execute("select * from v_requesthistory where status='A' and vendor_id=?",current_user.vendorID)
   data = cur.fetchall()   

   cur.close()
   return render_template('vendor/showPending.html',data=data)

@vendor.route('/vendor/deliveryOrder')
@role('Vendor')
def deliveryOrder():
   
   cur = con.cursor()
   cur.execute("select * from view_pending")
   data = cur.fetchall()   

   cur.close()
   return render_template('vendor/showPurchaseOrder.html',data=data,data2=data)

@vendor.route('/vendor/confirmDO')
@role('Vendor')
def confirmDO():
   request_id=request.args.get('rid')   
   cur = con.cursor()
   cur.execute("select * from v_deliveryOrder where request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select Stock_id,Send_date,Quantity from vendor_order where request_id=?",request_id)
   data2=cur.fetchall()

   cur.close()

   
   return render_template('vendor/confirmDelivery.html',data=data,data2=data2)
import datetime
@vendor.route('/vendor/addStore',methods=['POST'])
@role('Vendor')
def addStore():
   rid=request.form['rid']
   vid=request.form['vid']
   sdate=request.form['sdate']   
   price=request.form['uprice']
   sid_list=request.form.getlist('sid[]')
   qty_list=request.form.getlist('qty[]')
   #next value for seq_request
   sdate=sdate[:-3]
   now = datetime.datetime.now()
   cur=con.cursor()

   try:
      for i in range(len(sid_list)):                      
         
         cur.execute("insert into vendor_store(vs_id,vendor_id,stock_id,send_date,init_quantity,cur_quantity,cost_price) values (concat('v',next value for seq_vendorstore),?,?,?,?,?,?)"
         ,vid,sid_list[i],sdate,qty_list[i],qty_list[i],price)
      cur.execute("update request set status='C' where request_id=?",rid)  

      
      
   except Exception as e:    
        
      cur.close() 
      return str(e)
   cur.commit()
   cur.close()
   flash("Stock Added")
   return redirect(url_for('vendor.showPending'))

   
@vendor.route('/showCompletedRequest')
@role('Vendor')
def showRequestCompleteHistory():
   request_id=request.args.get('rid')  
   cur = con.cursor()
   cur.execute("select * from v_showRequest where request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select Stock_id,Send_date,Quantity from vendor_order where request_id=?",request_id)
   data2=cur.fetchall()

   return render_template('vendor/showAcceptedOrder.html',data=data,data2=data2)

@vendor.route('/vendor/notification')
@role('Vendor')
def notification():
   cur = con.cursor()
   cur.execute("select count(*) from request where status='A' and vendor_id=?",current_user.vendorID)
   result=cur.fetchone()
   return str(result[0])