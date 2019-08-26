# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import tkinter as tk
from tkinter import *
import pyodbc
from tkinter.messagebox import showinfo
#from calander import *

LARGE_FONT= ("Verdana", 12)


class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self, width=500, height=500)
        container.grid_propagate(False)
        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):

            frame = F(container, self)

            self.frames[F] = frame
            
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #ttkcal = Calendar(firstweekday=calendar.SUNDAY)
        #ttkcal.place(x=240,y=380)
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
        
                    
        label_0 = Label(self, text="Add Stock",width=20,font=("bold", 20))
        label_0.place(x=90,y=53)


        label_1 = Label(self, text="Stock ID",width=20,font=("bold", 10))
        label_1.place(x=80,y=130)

        entry_1 = Entry(self,textvar=StockID)
        entry_1.place(x=240,y=130)

        label_2 = Label(self, text="Product ID",width=20,font=("bold", 10))
        label_2.place(x=68,y=180)

        #entry_2 = Entry(root,textvar=ProductID)
        #entry_2.place(x=240,y=180)

        label_3 = Label(self, text="Date Receive",width=20,font=("bold", 10))
        label_3.place(x=70,y=230)

        entry_3 = Entry(self,textvar=dateReceive)
        entry_3.place(x=240,y=230)

        label_4 = Label(self, text="Condtion",width=20,font=("bold", 10))
        label_4.place(x=70,y=280)

        entry_4 = Entry(self,textvar=condition)
        entry_4.place(x=240,y=280)

        label_5 = Label(self, text="Retail price",width=20,font=("bold", 10))
        label_5.place(x=70,y=320)

        entry_5 = Entry(self,textvar=Retail_price)
        entry_5.place(x=240,y=320)

        label_7 = Label(self, text="Buy price",width=20,font=("bold", 10))
        label_7.place(x=70,y=320)

        entry_6 = Entry(self,textvar=Retail_price)
        entry_6.place(x=240,y=320)

        label_6 = Label(self, text="Quantity",width=20,font=("bold", 10))
        label_6.place(x=70,y=370)

        entry_6 = Entry(self,textvar=Quantity)
        entry_6.place(x=240,y=370)

        label_8 = Label(self, text="Type",width=20,font=("bold", 10))
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
        w = OptionMenu(self, variable,*(x))
        w.place(x=240,y=180)






        Button(self, text='Submit',width=20,bg='brown',fg='white',command=database).place(x=180,y=480)


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = tk.Button(self, text="Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()
        


app = SeaofBTCapp()
app.mainloop()