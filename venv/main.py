import pyodbc
import pandas as pd
import random
import matplotlib.pyplot as plt
import numpy as np
from werkzeug.security import generate_password_hash
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
from bokeh.palettes import Category20
from bokeh.transform import cumsum
from math import pi
#flask import
from flask_login import login_required, current_user
from flask import Flask, render_template,url_for,request,redirect,Blueprint,render_template,flash

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
con1 = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")


def index():   
   flash('testing')
   return redirect(url_for('main.profile'))
@main.route('/addVendor')
@role('Admin')
def addVendor():
   return render_template("addVendor.html")

@main.route('/addVendor',methods=['POST'])
@role('Admin')
def addVendorData():
   user_ID=request.form.get('userid')
   username=request.form.get('username')  
   password=request.form['password']
   
   location=request.form.get('location')
   cname=request.form.get('cname')
   telno=request.form.get('telno')
   aienable=request.form.get('new_aienable')

   password=generate_password_hash(password, method='sha256')
   try:
      cur=con.cursor()
      cur.execute("set nocount on exec prc_addVendor @id =?,@name = ?,@password = ?,@location = ?,@cname = ?,@telno = ?,@aicontrol =?",user_ID,username,password,location,cname,telno,aienable) 
      cur.commit()
      cur.close()
   except Exception as ex:
      return str(ex)
      cur.close()
   flash("Vendor Sucessful Added")
   
   return redirect(url_for('main.manageVendor'))

   

@main.route('/profile')
@role('Admin')
def profile():
   cur=con.cursor()
   cur.execute("select count(*) from request where status='P'")
   pending=cur.fetchone()
   cur.execute("select sum(sell_price) from request where month(order_date)=month(getdate()) and year(order_date)=year(getdate())")
   revenue=cur.fetchone()
   cur.execute("select count(sell_price) from request where month(order_date)=month(getdate()) and year(order_date)=year(getdate())")
   sales=cur.fetchone()
   #cur.execute("select TOP 1 logDate from autoLog where logType='F'order by LogDate desc")
   #data2=cur.fetchone()
   cur.execute("select cast(order_date as date),sum(sell_price) from request where month(order_date)=month(getdate()) and year(order_date)=year(getdate()) group by cast(order_date as date)")
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

   SQL_Query = pd.read_sql_query("select prod_name,sum(sell_price) from request r,product p where month(order_date)=month(getdate()) and year(order_date)=year(getdate()) and p.prod_id=r.prod_id group by prod_name", con)   
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
   cur.execute("select TOP 10  vendor_id,count(*) from vendor_order where month(Send_date)=11 group by vendor_id")
   data=cur.fetchall()
   X=[]
   y=[]
   for i in data:
      X.append(i[0])
      y.append(i[1])

   hover1 = HoverTool(tooltips=[("Quantity", "@Sales")])
   barchart = figure(x_range=X, plot_height=250,
               toolbar_location=None, tools=[hover1], sizing_mode='stretch_both')
   source = ColumnDataSource(data=dict(Vendor=X, Sales=y, color=Spectral6))
   barchart.vbar(x='Vendor', top='Sales', width=0.5,color='color',source=source)

   barchart.xgrid.grid_line_color = None
   barchart.y_range.start = 0
   script2, div2 = components(barchart)
   return render_template('profile.html', name=current_user.name,requestPending=pending[0],revenue=revenue[0],sales=sales[0],the_div=div, the_script=script,the_div1=div1, the_script1=script1,the_div2=div2, the_script2=script2)
from bokeh.palettes import Spectral6
@main.route('/showGraph',methods = ['GET'])
@role('Admin')
def showGraph():   
   cur = con.cursor()
   cur.execute("select * from product")
   product = cur.fetchall()
   cur.execute("select DISTINCT year(send_date) from vendor_order order by year(send_date) desc")
   year=cur.fetchall()
   try:
      Product_ID=request.args.get('pid')
      syear=request.args.get('year')
   except Exception as e:
      Product_ID=product[0][0]
      syear=year[0][0]
      print(Product_ID)
      print(syear)
   
   if(Product_ID==None and syear==None):
      Product_ID=product[0][0]
      syear=year[0][0]
      syear=str(syear)
      print(Product_ID)
      print(syear)
      

   SQL_Query = pd.read_sql_query("set nocount on exec [prc_getsalesbymonth] @year="+syear, con)
   
   df = pd.DataFrame(SQL_Query)
   
   X = df.columns[1:13].values
   y = df.loc[df['product_id'] == Product_ID].iloc[0,1:13].values
   #y = df.loc[0,1:13].values
   hover1 = HoverTool(tooltips=[("Quantity", "@Sales")])
   barchart = figure(x_range=X, plot_height=250, title="Stock Counts",
            toolbar_location=None, tools=[hover1], sizing_mode='stretch_both')
   source = ColumnDataSource(data=dict(product=X, Sales=y, color=Spectral6))
   barchart.vbar(x='product', top='Sales', width=0.5,color='color',source=source)

   barchart.xgrid.grid_line_color = None
   barchart.y_range.start = 0
   
   hover2 = HoverTool(tooltips=[("Quantity", "@y")])
   p = figure(plot_width=400, plot_height=400,x_range=['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep',
       'oct', 'nov', 'dec'],tools=[hover2], sizing_mode='stretch_both')
   
  
   # add a line renderer

   p.line(y=y,x=X,line_width=2)
   tab1 = Panel(child=barchart, title="Bar")
   tab2 = Panel(child=p, title="Line")
   tabs = Tabs(tabs=[tab1, tab2])
   script, div = components(tabs)

   #script2, div2 = components(p)
   return render_template("showGraph.html", bars_count=1,
                           the_div=div, the_script=script,product=product,year=year)
                           
@main.route('/showSales',methods = ['GET'])
@role('Admin')
def showSales():
   Product_ID=request.args.get('pid')
   sdate=request.args.get('sdate')  
   edate=request.args.get('edate')    
   cur = con.cursor()
   cur.execute("select * from product")
   product = cur.fetchall()
   if(sdate==None and edate==None):
      cur.execute("select TOP 7 prod_id,prod_name,send_date,sum(quantity) from showProductSales where prod_id=? group by prod_id,prod_name,send_date order by send_date desc",product[0][0])
   else: 
      cur.execute("select prod_id,prod_name,send_date,sum(quantity) from showProductSales where prod_id=? and send_date>=? and send_date<=? group by prod_id,prod_name,send_date order by send_date",Product_ID,sdate,edate)

   
   data=cur.fetchall()
   X=[]
   y1=[]
   for i in data:
      X.append(i[2])
      y1.append(i[3])
   hover1 = HoverTool(tooltips=[("Quantity", "@top")])
   barchart = figure(x_axis_type='datetime',plot_height=450, title="Sales for "+data[0][1],
            toolbar_location=None, tools=[hover1], sizing_mode='stretch_both')
   barchart.vbar(x=X, top=y1, width=70400000)

   barchart.y_range.start = 0
   barchart.xaxis.formatter=DatetimeTickFormatter(
           days=["%d %b "],
           months=["%d %b "],
           years=["%d %b "],
       )
   #hover2 = HoverTool(tooltips=[("Quantity", "@y")])
   #p = figure(plot_width=400, plot_height=400,tools=[hover2], sizing_mode='stretch_both')
   #p.xaxis.formatter=DatetimeTickFormatter(
   #     days=["%d %b"],
   #     months=["%d %b"],
   #     years=["%d %b"],
   # )
   # add a line renderer

   #p.line(y=y1,x=X,line_width=2)
   
   

   #tab1 = Panel(child=barchart, title="Bar")
   #tab2 = Panel(child=p, title="Line")
   #tabs = Tabs(tabs=[tab1, tab2])
   script, div = components(barchart)

   #script2, div2 = components(p)
   return render_template("showSales.html", bars_count=1,
                           the_div=div, the_script=script,product=product)

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

@main.route('/showStockTable')
@role('Admin')
def showStockTable():
   cur = con.cursor()
   cur.execute("select * from v_warehouse_stock order by prod_id,date_received asc")
   data = cur.fetchall()
   cur.execute("select prod_id,prod_name,sum(cur_quantity) as 'Total Quantity' from v_warehouse_stock group by prod_id,prod_name order by prod_id" )
   product=cur.fetchall()
   cur.close()

   return render_template('showStockTable.html',data=data,data1=product)

@main.route('/showVendorRequest')
@role('Admin')
def showVendorRequest():
   con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from request")
   data = cur.fetchall()
   cur.close()
   
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
      
      if(cur.rowcount):
         cur.commit()
         flash("Stock Added Sucessful")
         return redirect(url_for('main.showStock'))
         
      else:
         cur.close()
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
   price=request.form['price']
   
   
   return render_template('addOrder.html',data=rid,data1=vid,data2=price) 


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
         cur.execute("insert into vendor_order(Stock_id,Vendor_id,send_date,quantity,request_id) values (?,?,?,?,?)",
         sid_list[i],vid,sdate,qty_list[i],rid)
         cur.execute("update request set sell_price=?,status='A' where request_id=?",price,rid)
          
   except Exception as e:
      cur.close() 
      return str(e)
   cur.commit()
   flash('Responses sent')
   return redirect(url_for('main.showPending'))
@main.route('/home')
@role('Admin')
def home():
   return render_template('index.html')

@main.route('/forecast')
@role('Admin')
def forecast(): 
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
  
   p = figure(x_range=X, plot_height=400,x_axis_label='Month',x_minor_ticks=1,
            title="Forecast Sales",toolbar_location=None, tools=[hover1])

   p.line(y=Y,x=X,line_width=2)
 
   
   script, div = components(p)
   return render_template('showForecast.html',the_div=div, the_script=script,data=product)
@main.route('/confirmRequest')
@role('Admin')
def confirmRequest():
   request_id=request.args.get('rid')
   if(request_id==None):
      return redirect(url_for('main.showPending'))

   cur = con.cursor()
   cur.execute("select * from v_showRequest where status='P' and request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select * from v_warehouse_stock where prod_id=? and cur_quantity>0 ",data[0][3])
   data2=cur.fetchall()
   cur.execute("exec prc_showSafetyStock @pid=?",data[0][3])
   safetystock=cur.fetchone()
   
   if(safetystock[0]==None):
      safetystock[0]=0
   cur.close()

   return render_template('confirmRequest.html',data=data,data2=data2,safetystock=safetystock)


@main.route('/showRequestHistory')
@role('Admin')
def showRequestHistory():
   request_id=request.args.get('rid')
   if(request_id==None):
      return redirect(url_for('main.showRequest'))
   
   cur = con.cursor()
   cur.execute("select * from v_showRequest where request_id='"+request_id+"'")
   data = cur.fetchall()
   cur.execute("select Stock_id,Send_date,Quantity from vendor_order where request_id=?",request_id)
   data2=cur.fetchall()

   return render_template('completedRequest.html',data=data,data2=data2)



@main.route('/reject',methods=['POST'])
@role('Admin')
def reject():
   rid=request.form['rid']
   cur=con.cursor()
   try:      
      cur.execute("Update request set status='R' where request_id=?",rid)
   except Exception as e:
      cur.close()
      return str(e)
   cur.commit()         
   cur.close()
   flash('Sucessful Rejected')
   return redirect(url_for('main.showPending'))
    
@main.route('/showRequest')
@role('Admin')
def showAllRequest():   
   cur = con.cursor()
   cur.execute("select * from v_requesthistory where status!='P'")
   data = cur.fetchall()   

   cur.close()
   return render_template('requestHistory.html',data=data)

@main.route('/showPending')
@role('Admin')
def showPending():   
   cur = con.cursor()
   cur.execute("select * from v_requesthistory where status='P'")
   data = cur.fetchall()   

   cur.close()
   return render_template('showRequest.html',data=data)

@role('Admin')
def showRequest():
   cur = con.cursor()
   cur.execute("select * from v_showRequest")
   data = cur.fetchall()   

   cur.close()
   return render_template('showRequest.html',data=data)

@main.route('/callForecast')
@role('Admin')
def callForecast():
   if(monthlyforecast()!=False):
      flash('Re-Calculate Completed')
   else:
      flash('Error Please see the log')
   return redirect(url_for('main.forecast'))
@main.route("/showForecastLog")
@role('Admin')
def showForecastLog():
   cur=con.cursor()
   cur.execute("select * from autolog where prod_id is not null order by logdate desc")
   data=cur.fetchall()
   cur.close()
   return render_template('showForecastLog.html',data=data)
@main.route("/Productsetting")
def prod_setting():
   cur=con.cursor()
   cur.execute('select * from product')
   data=cur.fetchall()
   cur.execute("set nocount on SELECT cast(current_value as int)+1 FROM sys.sequences WHERE name = 'seq_productID'")
   newprod=cur.fetchall()
   newprod="pr"+str(newprod[0][0])
   cur.close()
   return render_template('showProductSetting.html',data=data,data1=newprod)

@main.route("/ManageVendor")
@role('Admin')
def manageVendor():
   cur=con.cursor()
   cur.execute('select [user_id],u.[name],u.vendorID,v.name,v.telno,AIEnable,v.location from [user] u,vendor v where v.vendorID=u.vendorID')
   data=cur.fetchall()
   cur.close()
   return render_template('ManageVendor.html',data=data)

@main.route("/updateVendor",methods=['POST'])
@role('Admin')
def update_Vendor(): 
   cur=con.cursor()                            
   uid=request.form['uid']
   uname=request.form['uname']
   vid=request.form['vid']
   cname=request.form['cname']
   telno=request.form['telno']
   aienable=request.form['aienable']
   location=request.form['location']
   try:            
      cur.execute("update vendor set location=?,name=?,telno=?,aienable=? where vendorId=?",location,cname,telno,aienable,vid)
      cur.execute("update [user] set name=? where user_id=?",uname,uid)
      
   except Exception as ex:
      cur.close()
      return str(ex)
   
   cur.close()    
   return "Suceesful Update"

@main.route("/updateProduct",methods=['POST'])
@role('Admin')
def update_productSetting():
   pid=request.form['pid']
   pname=request.form['pname']
   aienable=request.form['aienable']
   price=request.form['price']

   cur=con.cursor()
 
   try:            
      cur.execute("update product set prod_name=?,prod_aiEnable=?,price=? where prod_id=?",pname,aienable,price,pid)    
   except Exception as ex:
      cur.close()
      return str(ex)
   cur.commit()
   cur.close()    
   return "Suceesful Update"

@main.route("/addProduct",methods=['POST'])
@role('Admin')
def add_product():
   
   pname=request.form['pname']
   price=request.form['pprice']
   aienable=request.form['aienable']
   cur=con.cursor()  
   try:  
     
      sql="insert into product(prod_id,prod_name,prod_aiEnable,price) values(CONCAT('pr', Next value for seq_productID),'"+pname+"',"+aienable+",'"+price+"')"   
      print(sql)
      cur.execute(sql)
      cur.commit()
   except Exception as ex:
      cur.close()
      return str(ex)
   cur.close()    
   return redirect(url_for('main.prod_setting'))

@main.route("/showResponseLog")
@role('Admin')
def showResponseLog():
   cur=con.cursor()
   cur.execute("select * from autolog where request_id is not null order by logdate desc")
   data=cur.fetchall()
   cur.close()
   return render_template('showResponseLog.html',data=data)

@main.route('/autoResponse')
@role('Admin')
def autoResponses():
   a=""
   sucess=1
   cur = con.cursor()
   cur.execute("select * from v_autoResponse")
   result=cur.fetchall()
   for data in result :
      qty_request=data[3]
      cur.execute("set nocount on exec prc_showSafetyStock @pid=?",data[2])
      qty_safe=cur.fetchone()
      cur.execute("select Min(sell_price/quantity) from request where prod_id=? and sell_price is NOT NULL and DATEDIFF(MM, order_date, GETDATE()) < 6 ",data[2])
      min_price=cur.fetchone()  
      print(data[0])   
      print(data[1])  
      print(data[2])  
      print(data[3])  
      print(data[4])  
      if(data[4]>min_price[0]):
      
         if(qty_request<qty_safe[0]):
            cur.execute('exec prc_sendOrder @pid=?,@vid=?,@quantity=?,@rid=?,@price=?',data[2],data[1],data[3],data[0],data[4])
            cur.execute("insert into autoLog(logdate,request_id,details,logtype) values(getdate(),?,?,'R')",data[0],'Accepted')
         else:
            detail='Stock level too low. Safety Stock Quantity:'+str(data[4])
            cur.execute("insert into autoLog(logdate,request_id,details,logtype) values(getdate(),?,?,'RE')",data[0],detail)  
      else:
         detail='Sell price too low'
         cur.execute("insert into autoLog(logdate,request_id,details,logtype) values(getdate(),?,?,'RE')",data[0],detail) 
   cur.commit()
   cur.close()
   return redirect(url_for('main.showPending'))
@main.route('/notification')
@role('Admin')
def notification():
   cur = con1.cursor()
   cur.execute("select count(*) from request where status='P'")
   result=cur.fetchone()
   return str(result[0])

import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler


def monthlyforecast():
   cur = con.cursor()
   cur.execute("select distinct(prod_id) from show_sales")
   data=cur.fetchall()
   sucess=0
   failed=0
   try:
      for prod_id in data:
         try:
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
               sucess=sucess+1
         except Exception as e:
               cur.execute("insert into autolog(logdate,prod_id,date,details,logtype) values (getdate(),?,?,?,'FE')",row['prod_id'],row['Date'],str(e))
               failed=failed+1
               continue
   except Exception as e:
         cur.close()         
         return False
   flash(str(sucess)+" forecast completed,"+str(failed)+" FAILED")
   cur.commit()
   cur.close()


scheduler = BackgroundScheduler()
scheduler.add_job(func=monthlyforecast, trigger="cron", day=8)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())