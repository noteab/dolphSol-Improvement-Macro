# dolphSol Improvement Macro (dSIM)
join [DISCORD SERVER](https://discord.gg/FyrVp3Vhe9) for help and releases cause I ain't gonna post announcements when 6 people are asking for help in the thread\
\
 A macro for the Roblox game "Sol's RNG", including features such as obby completion and item collection. A work in progress - BuilderDolphin
 This Improved version of this macro includes many community request features. A work in progress - noteab

## Installation
  - First of all, you need to download **[AutoHotKey v1.1](https://www.autohotkey.com/)** (Not 2.0), and run the installer
  - Once complete, download the most recent version of dSIM through the most recent [GitHub Release](https://github.com/noteab/dolphSol-Improvement-Macro/releases/latest) (Download source code ZIP)
  - After downloading, extract the ZIP file to your desired directory
  - You can now run dolphSol through the Main.ahk file in the folder
### TO ACCESS PYTHON FEATURES SUCH AS DISCORD BOT, AUTO MERCHANT AND MORE

1. Download Python (latest version) (If you don't have it installed): https://www.python.org/downloads/ --> Also enable "add PATH to python" option
2. RUN Installer_v2.py  IN INSTALLATION FOLDER IN THE PYTHON SUPPORT FOLDER
3.  Download Tesseract (OCR used for biome detection, item check): (https://github.com/UB-Mannheim/tesseract/wiki)
--> Just find the keyword: "The latest installers can be downloaded here: tesseract-ocr-w64-setup-5.4.0.20240606.exe (64 bit)", at the front page so it easy to see
4. To use macro, run main.ahk, to use python features (such as merchant teleporter item crafter etc.) open Python_Settings_GUI.pyw

## Features
dolphSol has a couple of different features it is capable of. These include:
 - Automatic Obby Completion, with an option to check if it is completed in case it has to be redone
 - Automatic Item Collection, with options to set which spots to collect from if sharing a server
 - Automatic Aura Equipping, so you can always have an aura equipped without an animation to ensure the macro performs well
 - Discord Webhook support
 - Reconnecting upon disconnect
 - Setting for the VIP gamepass to compensate for the increased WalkSpeed
 - Settings importing, useful for updates
### This Improvement Macro also includes
 - Automatic Merchant Crafting
 - Discord remote bot commands
 - Aura Recordings
 - Automatic Potion Crafting
 - Automatic Item Crafting
 - Setting Importing
 - Automatic Collection Calibration

Discord Server (to official dolphSol server): https://discord.gg/DYUqwJchuV

## FAQ (Will add more questions soon)
-- Congratulate to everyone who patiently complete my installation & instruction guide, so this is how you use the command correctly --

(1) If you open the discord_cmd.py but the slash command in your discord wont show up? What should you do? --> Use "/sync" command and refresh the discord page, it should be update all the existing command list for you. Or uncomment await bot.tree.sync() in async def on_ready() and refresh your discord browser then comment that bot.tree.sync() (prevent from being ratelimited)

(2) For the reconnection, I have reverted back to deeplink method, auto detection sol rng server shutdown message and roblox disconnect popup, after reconnect it will reset the camera angle to let the AHK macro do its job properly.

(?) Soon...

### Current Development Team
noteab
steveonly1
curiouspengu
