import customtkinter
from ctypes import windll, byref, sizeof, c_int

root = customtkinter.CTk()
root.update()

HWND = windll.user32.GetParent(root.winfo_id()) # the window we want to change

"""
DWMWA_ATTRIBUTES (for windows 11 title bar) 
CAPTION COLOR (HEADER) = 35
BORDER COLOR = 34
TITLE COLOR = 36
"""

DWMWA_ATTRIBUTE = 35

COLOR = 0x00FF0000 # color should be in hex order: 0x00bbggrr

windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_ATTRIBUTE, byref(c_int(COLOR)), sizeof(c_int))

root.mainloop()