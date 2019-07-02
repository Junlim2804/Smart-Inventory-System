import pyodbc
try:
    import Tkinter
    import tkFont
except ImportError: # py3k
    import tkinter as Tkinter
    import tkinter.font as tkFont

import tkinter.ttk as ttk 
from calendar import *
import calendar
import sys
root = Tkinter.Tk()
root.title('Ttk Calendar')
ttkcal = Calendar(firstweekday=calendar.SUNDAY)
ttkcal.pack(expand=1, fill='both')

if 'win' not in sys.platform:
    style = ttk.Style()
    style.theme_use('clam')

root.mainloop()

