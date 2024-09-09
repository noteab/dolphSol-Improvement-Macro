from sys import argv # UNTIL NATIVE AURA DETECTION
from time import sleep

import pyautogui
def record_aura_hotkey():
    pyautogui.hotkey("winleft", "alt", "g")

def record_aura():
    # If roll minimum is less than 10000 all auras will be recorded
    if argv[2] < 10000:
        argv[2] = 0
    
    if argv[1] == 1:
        if argv[2] <= argv[3]:
            sleep(8) # wait for whole cutscene
            record_aura_hotkey()



def check_for_argv():
    # argv[1] record enabled
    # argv[2] record minimum
    # argv[3] aura rarity
    if not len(argv) == 4:
        exit(1)
    argv[1] = int(argv[1])
    argv[2] = int(argv[2])
    argv[3] = int(argv[3])

check_for_argv()
record_aura()