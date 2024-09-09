import tkinter as tk
from tkinter import ttk
from tkinter import BooleanVar, filedialog, messagebox
from tkinter import BooleanVar
import json
from pathlib import Path
from dotenv import load_dotenv, set_key
import os
import cv2
import numpy as np
import pyautogui
from tkinter import Toplevel
from PIL import ImageGrab

import subprocess # AUTOSTART DISCORD CMD / MERCHANT CMD
import threading
import sys
import pathlib

print(pathlib.Path(__file__).parent.resolve())
print(str(pathlib.Path(__file__).parent.resolve()) + "/data/Autostart Feature/Autostart.py")