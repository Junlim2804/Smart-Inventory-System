from tkinter import *
global username
global password
class GUI:


    userdaten = {
        "zxmod51" : "wou"}

    def anmelden(self):

        self.benutzer = username.get()
        self.passwort = password.get()

        if passwort == userdaten[benutzer] :
            print("Login erfolgreich")
        else :  print("FEHLER")

    def register(self):
        root1 = Tk()
        global username
        global password
        canvas1 = Canvas(root1, height=300, width=200)
        canvas1.pack()

        framereg = Frame(root1, bg="lightskyblue", height=300, width=200)
        framereg.place(relx=0, rely=0, relheight=1, relwidth=1)

        labelreg = Label(framereg, text="Registrierung")
        labelreg.place(anchor="center",relx=0.5, rely=0.1)

        labelben = Label(framereg, text="Benutzername:")
        labelben.place(anchor="center",relx=0.5, rely=0.2)

        entryben = Entry(framereg)
        entryben.place(anchor="center",relx=0.5, rely=0.28)

        labelpw = Label(framereg, text="Passwort")
        labelpw.place(anchor="center",relx=0.5, rely=0.38)

        entrypw = Entry(framereg)
        entrypw.place(anchor="center",relx=0.5, rely=0.45)

        buttonreg = Button(framereg, text="Registieren")
        buttonreg.place(anchor="center",relx=0.5, rely=0.6)


    def interface(self):
            root = Tk()
            username = StringVar()
            password = StringVar()

            canvas = Canvas(root, height=750, width=500)
            canvas.pack()


            frame0 = Frame(root, bg="lightskyblue", height=750, width=500)
            frame0.place(relx=0.0,rely=0.0,relheight=1,relwidth=1)

            #foto = PhotoImage(file="foto1.png")
            #labelbild = Label(frame0, image=foto)
            #labelbild.image = foto
            #labelbild.place(relx=0,rely=0)

            label = Label(frame0, text="Benutzername")
            label.place(anchor="center",relx=0.5, rely=0.3)

            entry = Entry(frame0,textvariable=username)
            entry.place(anchor="center",relx=0.5, rely=0.36)

            label1 = Label(frame0, text="Passwort")
            label1.place(anchor="center",relx=0.5, rely=0.42)

            entry1 = Entry(frame0,textvariable=password)
            entry1.place(anchor="center",relx=0.5, rely=0.48)
            
            button = Button(frame0, text="Anmelden", command=self.anmelden)
            button.place(anchor="center",relx=0.5, rely=0.56)
            
            button1 = Button(frame0, text="Registrieren",  command=self.register)
            button1.place(anchor="sw",relx=0.01, rely=0.99)

            root.mainloop()  



if __name__ == "__main__" :

    inst = GUI()
    inst.interface()