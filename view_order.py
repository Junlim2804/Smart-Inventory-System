from tkinter import *
import pyodbc

root = Tk()
root.geometry('800x800')
root.title("View Order")


height = 30
width = 6
for i in range(height): #Rows
    for j in range(width): #Columns
        b = Entry(root, text="")
        b.grid(row=i, column=j)

l1=Label(root,text="Stock_ID")
l1.grid(row=0,column=0)

l2=Label(root,text="Vendor_ID")
l2.grid(row=0,column=1)

l3=Label(root,text="Quantity")
l3.grid(row=0,column=2)

l4=Label(root,text="Send_Date")
l4.grid(row=0,column=3)

l5=Label(root,text="Receive_Date")
l5.grid(row=0,column=4)

l6=Label(root,text="Sell_price")
l6.grid(row=0,column=5)


server = '(localdb)\MSSQLLocalDB'
database = 'SCMdb'
username = 'Guest'
password = 'Guest'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect("Driver="+driver+";Server="+server+";Database="+database+";Uid="+username+";Pwd="+password+";TrustServerCertificate=no;Connection Timeout=30;")
cursor = cnxn.cursor()
cursor.execute("select * from vendor_order")

i=1

e=[range(100)]
for x in cursor.fetchall():
    for j in range(len(x)):
        entry=Label(root,text=x[j],bg="#FFFFFF")
        entry.grid(row=i,column=j)
        j=j+1

    i=i+1










mainloop()