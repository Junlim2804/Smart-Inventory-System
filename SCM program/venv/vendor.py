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
from flask import Flask, render_template,url_for,request,redirect,Blueprint,render_template,flash,session
from pmdarima.arima import auto_arima
from . import db
from .models import User

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
@login_required
def index():
   return render_template('vendor/profile.html',data=current_user.vendorID)

@vendor.route('/vendorRequest')
@login_required
def vendorRequest():
   
   cur = con.cursor()
   cur.execute("select * from product")
   data = cur.fetchall()
   uid=current_user.vendorID
   return render_template('/vendor/addRequest.html',data=data,uid=uid)


@vendor.route('/addRequest',methods=['POST'])
@login_required
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
@login_required
def showComplete():
    return "complete"

@vendor.route('/vendor/showStock')
@login_required
def showStock():
   #con = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")

   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vendor_id='"+current_user.vendorID+"' order by receive_date asc")
   data = cur.fetchall()
   
   return render_template('vendor/showStock.html',data=data)

@vendor.route('/errorMsg')
@login_required
def errorMessage():
    messages = session['errmsg'] 
    flash(messages)
    return render_template("errorMessage.html")

@vendor.route('/vendor/adjustStock',methods=['GET'])
@login_required
def adjustStock():   
   vs_id=request.args.get('vs_id')
   cur = con.cursor()
   cur.execute("select * from v_vendor_stock where vs_id='"+vs_id+"'")
   data = cur.fetchall()
   return render_template('vendor/adjustStock.html',data=data)   

@vendor.route('/vendor/adjustStock',methods=['POST'])
@login_required
def adjustStocking():   
   #vs_id=request.form['vs_id']
   qty=request.form['qty']
   return qty  
