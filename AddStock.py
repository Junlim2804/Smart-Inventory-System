from tkinter import *
import pyodbc
from tkinter.messagebox import showinfo

root = Tk()
root.geometry('500x500')
root.title("Add stock to warehouse")

StockID=StringVar()
ProductID=StringVar()
dateReceive=StringVar()
condition=StringVar()
Retail_price = DoubleVar()
Quantity=IntVar()

server = 'tcp:fypscm.database.windows.net,1433'
db = 'SCMdb'
username = 'jl2804'
password = 'TauJun2804'
driver= '{ODBC Driver 17 for SQL Server}'



def database():
    Stock_ID=StockID.get()
    Prod_ID=variable.get()   
    #Prod_ID=Prod_ID[2:5]
    #print(Prod_ID)
    Receive_Date=dateReceive.get()
    Con=condition.get()
    Re_price=Retail_price.get()
    Qty=Quantity.get()


    cnxn = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+db+";Uid="+username+";Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    cursor = cnxn.cursor()
    cursor.execute("insert into warehouse values(?,?,?,?,?,?)",(Stock_ID,Prod_ID,Receive_Date,Con,Re_price,Qty))
    cnxn.commit()
    if(cursor.rowcount):
        showinfo("Sucessful", "Order sucessful placed")
   
             
label_0 = Label(root, text="Add Stock",width=20,font=("bold", 20))
label_0.place(x=90,y=53)


label_1 = Label(root, text="Stock ID",width=20,font=("bold", 10))
label_1.place(x=80,y=130)

entry_1 = Entry(root,textvar=StockID)
entry_1.place(x=240,y=130)

label_2 = Label(root, text="Product ID",width=20,font=("bold", 10))
label_2.place(x=68,y=180)

#entry_2 = Entry(root,textvar=ProductID)
#entry_2.place(x=240,y=180)

label_3 = Label(root, text="Date Receive",width=20,font=("bold", 10))
label_3.place(x=70,y=230)

entry_3 = Entry(root,textvar=dateReceive)
entry_3.place(x=240,y=230)

label_4 = Label(root, text="Condtion",width=20,font=("bold", 10))
label_4.place(x=70,y=280)

entry_4 = Entry(root,textvar=condition)
entry_4.place(x=240,y=280)

label_5 = Label(root, text="Retail price",width=20,font=("bold", 10))
label_5.place(x=70,y=320)

entry_5 = Entry(root,textvar=Retail_price)
entry_5.place(x=240,y=320)

label_7 = Label(root, text="Buy price",width=20,font=("bold", 10))
label_7.place(x=70,y=320)

entry_6 = Entry(root,textvar=Retail_price)
entry_6.place(x=240,y=320)

label_6 = Label(root, text="Quantity",width=20,font=("bold", 10))
label_6.place(x=70,y=370)

entry_6 = Entry(root,textvar=Quantity)
entry_6.place(x=240,y=370)

label_8 = Label(root, text="Type",width=20,font=("bold", 10))
label_8.place(x=70,y=420)

cnxn = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+db+";Uid="+username+";Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
cursor = cnxn.cursor()
cursor.execute("Select prod_id from Product")
x=cursor.fetchall()
i=0
for pr in x:
        x[i]=str(pr)[2:5]
        i+=1
variable=StringVar()
variable.set(x[0])
w = OptionMenu(root, variable,*(x))
w.place(x=240,y=180)






Button(root, text='Submit',width=20,bg='brown',fg='white',command=database).place(x=180,y=480)

root.mainloop()























