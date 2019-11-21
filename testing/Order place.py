from tkinter import *
import pyodbc
from tkinter.messagebox import showinfo

root = Tk()
root.geometry('500x500')
root.title("Order Detail")


ProductID=StringVar()
VendorID=StringVar()
Quantity = IntVar()
Send=StringVar()
price=IntVar()



def database():
   Prod_ID=ProductID.get()
   Ven_ID=VendorID.get()
   Qty=Quantity.get()
   Send_Date=Send.get()
   Price=price.get()
  

   #with conn:
   #   cursor=conn.cursor()
   #cursor.execute('CREATE TABLE IF NOT EXISTS Student (Fullname TEXT,Email TEXT,Gender TEXT,country TEXT,Programming TEXT)')
   #cursor.execute('INSERT INTO Student (FullName,Email,Gender,country,Programming) VALUES(?,?,?,?,?)',(name1,email,gender,country,prog,))
   #conn.commit()
   server = 'tcp:fypscm.database.windows.net,1433'
   database = 'SCMdb'
   username = 'jl2804'
   password = 'TauJun2804'
   driver= '{ODBC Driver 17 for SQL Server}'
   cnxn = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
   cursor = cnxn.cursor()
   #cursor.execute("insert into vendor_order(stock_id,vendor_id,quantity,send_date) values(?,?,?,?)",(Prod_ID,Ven_ID,Qty,Send_Date))
   sql="EXEC	[dbo].[prc_createOrder] @stock = ?,@venid =?,@qty = ?,@sdate = ?,@price = ?"
   values=(Prod_ID,Ven_ID,Qty,Send_Date,Price)
   cursor.execute(sql,values)
   cnxn.commit()
   if(cursor.rowcount):
      showinfo("Sucessful", "Order sucessful placed")
   
             
label_0 = Label(root, text="Order form",width=20,font=("bold", 20))
label_0.place(x=90,y=53)


label_1 = Label(root, text="Product ID",width=20,font=("bold", 10))
label_1.place(x=80,y=130)

entry_1 = Entry(root,textvar=ProductID)
entry_1.place(x=240,y=130)

label_2 = Label(root, text="Vendor ID",width=20,font=("bold", 10))
label_2.place(x=68,y=180)

entry_2 = Entry(root,textvar=VendorID)
entry_2.place(x=240,y=180)

label_3 = Label(root, text="Quantity",width=20,font=("bold", 10))
label_3.place(x=70,y=230)

entry_3 = Entry(root,textvar=Quantity)
entry_3.place(x=240,y=230)



label_4 = Label(root, text="Send_date",width=20,font=("bold", 10))
label_4.place(x=70,y=280)

entry_4 = Entry(root,textvar=Send)
entry_4.place(x=240,y=280)

label_5 = Label(root, text="Sell Price",width=20,font=("bold", 10))
label_5.place(x=70,y=320)

entry_5 = Entry(root,textvar=price)
entry_5.place(x=240,y=320)



Button(root, text='Submit',width=20,bg='brown',fg='white',command=database).place(x=180,y=380)

root.mainloop()























