; dolpSol Macro
;   A macro for Sol's RNG on Roblox
;   GNU General Public License
;   Free for anyone to use
;   Modifications are welcome, however stealing credit is not
;   Hope you enjoy - BuilderDolphin
;   A "small" project started on 03/07/2024
;   
;   https://github.com/BuilderDolphin/dolphSol-Macro
;   
;   Feel free to provide any suggestions (through discord preferably, @builderdolphin). 

#Requires AutoHotkey v1.1+ 64-bit
#SingleInstance, force
#NoEnv
#Persistent
SetBatchLines, -1

OnError("LogError")
; OnMessage(0x500, "ReceiveData")

SetWorkingDir, % A_ScriptDir "\lib"
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

#Include *i %A_ScriptDir%\lib
#Include *i ocr.ahk
#Include *i Gdip_All.ahk
#Include *i Gdip_ImageSearch.ahk
#Include *i jxon.ahk


global currentVersion := "v1.5.0"
global currentPatch := "08/08"
global version := "v1.4.0" . " (Python Experimental - Noteab 07/9) " ; fake v1.4.0 version so it wont popup the update anymore

if (RegExMatch(A_ScriptDir,"\.zip") || IsFunc("ocr") = 0) {
    ; File is not extracted or not saved with other necessary files
    MsgBox, 16, % "dolphSol Macro " version, % "Unable to access all necessary files to run correctly.`n"
            . "Please make sure the macro folder is extracted by right clicking the downloaded file and choosing 'Extract All'.`n`n"
            . "Note that Amraki's Patch only contains modified files. They will need to be copied into the official macro folder."
    ExitApp
}

Gdip_Startup()

; Run macro as admin to avoid issues with Roblox input
full_command_line := DllCall("GetCommandLine", "str")
if not (A_IsAdmin or RegExMatch(full_command_line, " /restart(?!\S)")) {
    try {
        RunWait, *RunAs "%A_AhkPath%" /restart "%A_ScriptFullPath%"
    }
}

; TODO: change some of these to static variables
global loggingEnabled := true ; Debug logging to file
global disableAlignment := false ; Toggle with F5
global lastLoggedMessage := ""
global delayMultiplier := 3 ; Delay multiplier for slower computers - Mainly for camera mode changes
global auraNames := [] ; List of aura names for webhook pings
global biomes := ["Windy", "Rainy", "Snowy", "Hell", "Starfall", "Corruption", "Null", "Glitched"]
global ItemSchedulerEntries := []  ; Initialize the array for item usage entries
global StellaPortalDelay := 0 ; Extra wait time (ms) after entering portal before moving to cauldron - 1000ms = 1s

global robloxId := 0

global canStart := 0
global macroStarted := 0
global reconnecting := 0

global isSpawnCentered := 0
global atSpawn := 0

global pathsRunning := []

obbyCooldown := 120 ; 120 seconds
lastObby := A_TickCount - obbyCooldown*1000
hasObbyBuff := 0

obbyStatusEffectColor := 0x9CFFAC
craftingCompleteColor := 0x1C821A

statusEffectSpace := 5

global mainDir := A_ScriptDir "\"

logMessage("") ; empty line for separation
logMessage("Macro opened")

configPath := mainDir . "settings\config.ini"
global ssPath := "ss.jpg"
global pathDir := mainDir . "paths\"
global imgDir := mainDir . "images\"

global camFollowMode := 0

configHeader := "; dolphSol Settings`n;   Do not put spaces between equals`n;   Additions may break this file and the macro overall, please be cautious`n;   If you mess up this file, clear it entirely and restart the macro`n`n[Options]`r`n"

global importantStatuses := {"Starting Macro":1
    ,"Roblox Disconnected":1
    ,"Reconnecting":1
    ,"Reconnecting, Roblox Opened":0
    ,"Reconnecting, Game Loaded":0
    ,"Reconnect Complete":1
    ,"Initializing":0
    ,"Macro Stopped":1}

global potionIndex := {0:"None"
    ,1:"Fortune Potion I"
    ,2:"Fortune Potion II"
    ,3:"Fortune Potion III"
    ,4:"Haste Potion I"
    ,5:"Haste Potion II"
    ,6:"Haste Potion III"
    ,7:"Heavenly Potion I"
    ,8:"Heavenly Potion II"}

global craftingInfo := {"Fortune Potion I":{slot:1,subSlot:1,addSlots:4,maxes:[5,1,5,1],attempts:2}
    ,"Fortune Potion II":{slot:1,subSlot:2,addSlots:5,maxes:[1,10,5,10,2],attempts:2}
    ,"Fortune Potion III":{slot:1,subSlot:3,addSlots:5,maxes:[1,15,10,15,5],attempts:2}
    ,"Haste Potion I":{slot:2,subSlot:1,addSlots:4,maxes:[10,5,10,1],attempts:2}
    ,"Haste Potion II":{slot:2,subSlot:2,addSlots:5,maxes:[1,10,10,15,2],attempts:2}
    ,"Haste Potion III":{slot:2,subSlot:3,addSlots:5,maxes:[1,20,15,25,4],attempts:2}
    ,"Heavenly Potion I":{slot:3,subSlot:1,addSlots:4,maxes:[100,50,20,1],attempts:2}
    ,"Heavenly Potion II":{slot:3,subSlot:2,addSlots:5,maxes:[2,125,75,50,1],attempts:2}}

global rarityIndex := {0:"None"
    ,1:"1/1k+"
    ,2:"1/10k+"
    ,3:"1/100k+"}

reverseIndices(t){
    newT := {}
    for i,v in t {
        newT[v] := i
    }
    return newT
}

global reversePotionIndex := reverseIndices(potionIndex)
global reverseRarityIndex := reverseIndices(rarityIndex)

; defaults
global sData := {}
global options := {"DoingObby":1
    ,"AzertyLayout":0
    ,"ArcanePath":0
    ,"CheckObbyBuff":1
    ,"CollectItems":1
    ,"ItemSpot1":1
    ,"ItemSpot2":1
    ,"ItemSpot3":1
    ,"ItemSpot4":1
    ,"ItemSpot5":1
    ,"ItemSpot6":1
    ,"ItemSpot7":1
    ,"Screenshotinterval":60
    ,"WindowX":100
    ,"WindowY":100
    ,"VIP":0
    ,"BackOffset":0
    ,"ReconnectEnabled":1
    ,"AutoEquipEnabled":0
    ,"AutoEquipX":-0.415
    ,"AutoEquipY":-0.438
    ,"PrivateServerId":""
    ,"InOwnPrivateServer":1 ; Determines side button positions
    ,"ScanLoopInterval":1 ; How many attempts/tries to scan and count left side buttons (If 7 buttons then you're on friend/public server, 8 is you are on your PS instead) - Noteab
    ,"StorageButtonYPosScanVALUE":318 ; Storage Y Pos value in main option - Noteab
    ,"StorageYOffsetIntervalVALUE":70 ; Storage Y Pos highlight box for easier look while adjusting - Noteab
    ,"AutoClaimQuestEnabled":0 ; Toggle for Auto Claim Quest from Amraki (why he doesnt add this, what a silly guy :at:)
    ,"LastAnnouncement":0
    ,"WebhookEnabled":0
    ,"WebhookLink":""
    ,"WebhookImportantOnly":0
    ,"DiscordUserID":""
    ,"DiscordGlitchID":""       ; Amraki ; Used in status.ahk for biome ping in Discord - Defaults to DiscordUserID if not set
    ,"WebhookRollSendMinimum":10000
    ,"WebhookRollPingMinimum":100000
    ,"WebhookAuraRollImages":0
    ,"StatusBarEnabled":0
    ,"WasRunning":0
    ,"FirstTime":0
    ,"InvScreenshotsEnabled":1
    ,"LastInvScreenshot":0
    ,"OCREnabled":0             ; Amraki
    ,"RestartRobloxEnabled":0   ; Amraki
    ,"RestartRobloxInterval":1  ; Amraki
    ,"LastRobloxRestart":0      ; Amraki
    ,"RobloxUpdatedUI":2 ; Default to "New"

    ; Crafting
    ,"ItemCraftingEnabled":0
    ,"CraftingInterval":10
    ,"LastCraftSession":0
    ,"PotionCraftingEnabled":0
    ,"PotionCraftingSlot1":0
    ,"PotionCraftingSlot2":0
    ,"PotionCraftingSlot3":0
    ,"PotionAutoAddEnabled":0   ; Amraki
    ,"PotionAutoAddInterval":10 ; Amraki
    ,"LastPotionAutoAdd":0      ; Amraki

    ,"ExtraRoblox":0 ; mainly for me (builderdolphin) to run my 3rd acc on 2nd monitor, not used for anything else, not intended for public use unless yk what you're doing i guess

; not really options but stats i guess
    ,"RunTime":0
    ,"Disconnects":0
    ,"ObbyCompletes":0
    ,"ObbyAttempts":0
    ,"CollectionLoops":0}

global privateServerPre := "https://www.roblox.com/games/15532962292/Sols-RNG?privateServerLinkCode="

; Must be called in correct order
updateStaticData() ; Get latest data for update check, aura names, etc.
loadData() ; Load config data

; Disable OCR mode if resolution isn't supported
; Now enabling the mode will notify of requirements
if (options.OCREnabled) {
    getRobloxPos(pX, pY, pW, pH)
    if not (pW = 1920 && pH = 1080 && A_ScreenDPI = 96) {
        options.OCREnabled := 0
    }
}

if (options.ItemCraftingEnabled) {
    if (options.ItemCraftingEnabled = 1) {
        options.ItemCraftingEnabled := 0
    }
}

global currentLanguage := getCurrentLanguage() ; Get the current language for OCR check
getCurrentLanguage() {
    try {
        hWnd := GetRobloxHWND() ? WinExist("ahk_id" . GetRobloxHWND()) : WinExist("A")
        currentLanguage := GetInputLangName(GetInputLangID(hWnd))
        logMessage("Current Language: " currentLanguage)
        return currentLanguage
    }
    return "Unknown"
}
getOCRLanguages() {
    ; Macro requires "en-US" to be installed for OCR library (as of 06/21/24)

    languages := ocr("ShowAvailableLanguages")
    if (!languages) {
        logMessage("An error occurred while checking for OCR languages")
        return 0
    }

    logMessage("OCR languages installed:")
    logMessage(languages)
    return languages

    ; Check if the script is running as admin
    if (!A_IsAdmin) {
        logMessage("Main.ahk not running as admin")

        MsgBox, 4, , % "You will need the 'English (United States)' language pack installed for enhanced functionality.`n`n"
            . "Would you like to run this file as an administrator to attempt to install it automatically?"

        IfMsgBox Yes
            logMessage("Restarting Main.ahk as admin")
            RunWait, *RunAs "%A_AhkPath%" /restart "%A_ScriptFullPath%"
            return
    } else {
        logMessage("Main.ahk running as admin")

        ; Give the option to auto install the language pack
        MsgBox, 4, , % "You will need the 'English (United States)' language pack installed for enhanced functionality.`n`n"
            . "Select 'No' to do it yourself through Settings > Time & Language > Language & Region > Add a language.`n"
            . "Select 'Yes' to attempt to install it automatically.`n`n"
            . "Both options will require you to log out and back in (or restart) to take effect."

        IfMsgBox Yes
            logMessage("Attempting to install the language pack")
            try {
                RunWait, *RunAs powershell.exe -ExecutionPolicy Bypass Install-Language en-US
                ExitApp
            } catch e {
                logMessage("An error occurred while attempting to install the language pack")
                logMessage(e, 1)
                MsgBox, 16, Error, % "An error occurred while attempting to install the language pack.`n`n"
                    . "Please install it manually through Settings > Time & Language > Language & Region > Add a language."
            }
    }
}

/*
    Begin Language Functions

    GetInputLangID(), GetInputLangName()
    Last submitted by teadrinker 20 Sep 2020 at https://www.autohotkey.com/boards/viewtopic.php?style=17&p=353708&sid=4498caf4025f947e56ee1f190c7f2227#p353708
*/
GetInputLangID(hWnd) {
   WinExist("ahk_id" . hWnd)
   WinGet, processName, ProcessName
   if (processName != "ApplicationFrameHost.exe") {
      ControlGetFocus, focused
      if !ErrorLevel
         ControlGet, hWnd, hwnd,, % focused
      threadId := DllCall("GetWindowThreadProcessId", "Ptr", hWnd, "Ptr", 0)
   }
   else {
      WinGet, PID, PID
      WinGet, controlList, ControlListHwnd
      Loop, parse, controlList, `n
         threadId := DllCall("GetWindowThreadProcessId", "Ptr", A_LoopField, "UIntP", childPID)
      until childPID != PID
   }
   lyt := DllCall("GetKeyboardLayout", "Ptr", threadId, "UInt")
   return langID := Format("{:#x}", lyt & 0x3FFF)
}
GetInputLangName(langId) {
   static LOCALE_SENGLANGUAGE := 0x1001
   charCount := DllCall("GetLocaleInfo", "UInt", langId, "UInt", LOCALE_SENGLANGUAGE, "UInt", 0, "UInt", 0)
   VarSetCapacity(localeSig, size := charCount << !!A_IsUnicode, 0)
   DllCall("GetLocaleInfo", "UInt", langId, "UInt", LOCALE_SENGLANGUAGE, "Str", localeSig, "UInt", size)
   return localeSig
}
/*
    End Language Functions
*/

getINIData(path){
    FileRead, retrieved, %path%
    
    if (!retrieved){
        logMessage("[getINIData] No data found in " path)
        MsgBox, An error occurred while reading %path% data, please review the file.
        return
    }

    retrievedData := {}
    readingPoint := 0

    ls := StrSplit(retrieved,"`n")
    for i,v in ls {
        ; Remove any carriage return characters
        v := Trim(v, "`r")

        isHeader := RegExMatch(v,"\[(.*)]")
        if (v && readingPoint && !isHeader){
            RegExMatch(v,"(.*)(?==)",index)
            RegExMatch(v,"(?<==)(.*)",value)
            if (index){
                retrievedData[index] := value
            }
        } else if (isHeader){
            readingPoint := 1
        }
    }
    return retrievedData
}

writeToINI(path,object,header){
    if (!FileExist(path)){
        MsgBox, You are missing the file: %path%, please ensure that it is in the correct location.
        return
    }

    formatted := header

    for i,v in object {
        formatted .= i . "=" . v . "`r`n"
    }

    FileDelete, %path%
    FileAppend, %formatted%, %path%
}

getURLContent(url) {
    try {
        WinHttp := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        WinHttp.Open("GET", url, false)
        WinHttp.SetRequestHeader("Cache-Control", "no-cache")
        WinHttp.SetRequestHeader("Pragma", "no-cache")
        WinHttp.Send()

        If (WinHttp.Status = 200) {
            return WinHttp.ResponseText
        }

        return ""
    } catch {
        return ""
    }
}


updateStaticData() {
    updateURL := "https://raw.githubusercontent.com/BuilderDolphin/dolphSol-Macro/main/lib/staticData.json"
    patchURL := "https://raw.githubusercontent.com/Amraki/dolphSol-Macro/Amraki-Patch/lib/staticData.json"

    patchContent := getURLContent(patchURL)
    if (patchContent != "") {
        FileDelete, staticData.json
        FileAppend, %patchContent%, staticData.json

        patchData := Jxon_Load(patchContent)[1]
        patchVersion := patchData.updateInfo.latestVersion
        OutputDebug, % "patchVersion: " patchVersion
    }

    content := getURLContent(updateURL)
    if (content != "") {
        officialData := Jxon_Load(content)[1]
        officialVersion := officialData.updateInfo.latestVersion
        OutputDebug, % "officialVersion: " officialVersion
    }

    if (patchContent == "" && content == "") {
        MsgBox, 16, Update Check, % "Unable to check for update. Error: " . e.Message . "`nContinuing with current StaticData.json data.`nCheck your network connection and restart to try again."
        return
    }

    ; Show Announcement once daily at most
    sData := patchData
    if (sData.announcement != "" && (getUnixTime() - options.LastAnnouncement >= 24*60*60*1000)) { ; 24hrs
        MsgBox, 0, Macro Announcement, % sData.announcement
        options.LastAnnouncement := getUnixTime()
    }

    if (patchVersion && patchVersion != currentPatch) {
        ; Patch update available
        updateMessage := "A new patch version is available!"
    } else if (officialVersion && officialVersion != currentVersion) {
        ; Official update available
        sData := officialData
        updateMessage := "An official update is available! Please note some features from the patch may be missing or modified so adjust accordingly."
    } else {
        return
    }

    uNotes := sData.updateInfo.updateNotes
    MsgBox, 36, New Update Available, % updateMessage . "`nWould you like to head to the GitHub page to update your macro?" . (uNotes ? ("`n`nUpdate Notes:`n" . uNotes) : "")
    IfMsgBox No
        return

    options.FirstTime := 0
    vLink := sData.updateInfo.versionLink
    Run % (vLink ? vLink : "https://github.com/BuilderDolphin/dolphSol-Macro/releases/latest")
    ExitApp
}

; data loading
loadData(){
    global
    logMessage("[loadData] Loading config data")

    savedRetrieve := getINIData(configPath)
    if (!savedRetrieve){
        logMessage("[loadData] Unable to retrieve config data, Resetting to defaults.")
        MsgBox, % "Unable to retrieve config data, your settings have been set to their defaults."
        savedRetrieve := {}
    } else { ; Commented out to avoid log spam
        ; logMessage("[loadData] Successfully retrieved config data:")
        ; for i,v in savedRetrieve {
            
        ;     ; Don't log Aura Webhook settings
        ;     if (InStr(i, "wh" , 1) = 1) {
        ;         continue
        ;     }

        ;     ; Don't log private data
        ;     if (i = "PrivateServerId" || i = "WebhookLink") {
        ;         logMessage(i ": *hidden*", 1)
        ;         continue ; don't log these
        ;     }
        ;     logMessage(i ": " v, 1)
        ; }
    }

    local newOptions := {}
    for i, v in options { ; Iterating through defined options does not load dynamic settings - currently aura, biomes
        if (savedRetrieve.HasKey(i)) {
            newOptions[i] := savedRetrieve[i]

            ; Temporary code to fix time error
            for _, key in ["LastCraftSession","LastInvScreenshot","LastPotionAutoAdd"] {
                if (i = key && savedRetrieve[i] > getUnixTime()) {
                    ; logMessage("Resetting " i)
                    ; Reset value so it's not too high to trigger
                    newOptions[i] := 0
                }
            }
        } else {
            logMessage("[loadData] Missing key: " i)
            newOptions[i] := v
        }
    }
    options := newOptions

    ; Load aura settings with prefix
    for index, auraName in auraNames {
        sAuraName := RegExReplace(auraName, "[^a-zA-Z0-9]+", "_") ; Replace all non-alphanumeric characters with underscore
        sAuraName := RegExReplace(sAuraName, "\_$", "") ; Remove any trailing underscore
        key := "wh" . sAuraName
        if (savedRetrieve.HasKey(key)) {
            options[key] := savedRetrieve[key]
        } else {
            options[key] := 1 ; default enabled
        }
        ; logMessage("[loadData] Aura: " auraName " - " sAuraName " - " options[key])
    }

    ; Load biome settings
    for i, biome in biomes {
        key := "Biome" . biome
        if (savedRetrieve.HasKey(key)) {
            options[key] := savedRetrieve[key]
        } else {
            options[key] := "Message" ; Set default
        }
        ; logMessage("[loadData] Biome: " biome " - " options[key])
    }

    LoadItemSchedulerOptions()
}

saveOptions(){
    global configPath,configHeader
    writeToINI(configPath,options,configHeader)
}
saveOptions()

updateYesClicked(){
    vLink := sData.updateInfo.versionLink
    Run % (vLink ? vLink : "https://github.com/BuilderDolphin/dolphSol-Macro/releases/latest")
    ExitApp
}

; CreateFormData() by tmplinshi, AHK Topic: https://autohotkey.com/boards/viewtopic.php?t=7647
; Thanks to Coco: https://autohotkey.com/boards/viewtopic.php?p=41731#p41731
; Modified version by SKAN, 09/May/2016
; Rewritten by iseahound in September 2022
CreateFormData(ByRef retData, ByRef retHeader, objParam) {
	New CreateFormData(retData, retHeader, objParam)
}

Class CreateFormData {

    __New(ByRef retData, ByRef retHeader, objParam) {

        Local CRLF := "`r`n", i, k, v, str, pvData
        ; Create a random Boundary
        Local Boundary := this.RandomBoundary()
        Local BoundaryLine := "------------------------------" . Boundary

        ; Create an IStream backed with movable memory.
        hData := DllCall("GlobalAlloc", "uint", 0x2, "uptr", 0, "ptr")
        DllCall("ole32\CreateStreamOnHGlobal", "ptr", hData, "int", False, "ptr*", pStream:=0, "uint")
        this.pStream := pStream

        ; Loop input paramters
        For k, v in objParam
        {
            If IsObject(v) {
                For i, FileName in v
                {
                    str := BoundaryLine . CRLF
                        . "Content-Disposition: form-data; name=""" . k . """; filename=""" . FileName . """" . CRLF
                        . "Content-Type: " . this.MimeType(FileName) . CRLF . CRLF

                    this.StrPutUTF8( str )
                    this.LoadFromFile( Filename )
                    this.StrPutUTF8( CRLF )

                }
            } Else {
                str := BoundaryLine . CRLF
                    . "Content-Disposition: form-data; name=""" . k """" . CRLF . CRLF
                    . v . CRLF
                this.StrPutUTF8( str )
            }
        }

        this.StrPutUTF8( BoundaryLine . "--" . CRLF )

        this.pStream := ObjRelease(pStream) ; Should be 0.
        pData := DllCall("GlobalLock", "ptr", hData, "ptr")
        size := DllCall("GlobalSize", "ptr", pData, "uptr")

        ; Create a bytearray and copy data in to it.
        retData := ComObjArray( 0x11, size ) ; Create SAFEARRAY = VT_ARRAY|VT_UI1
        pvData  := NumGet( ComObjValue( retData ), 8 + A_PtrSize , "ptr" )
        DllCall( "RtlMoveMemory", "Ptr", pvData, "Ptr", pData, "Ptr", size )

        DllCall("GlobalUnlock", "ptr", hData)
        DllCall("GlobalFree", "Ptr", hData, "Ptr")                   ; free global memory

        retHeader := "multipart/form-data; boundary=----------------------------" . Boundary
    }

    StrPutUTF8( str ) {
        length := StrPut(str, "UTF-8") - 1 ; remove null terminator
        VarSetCapacity(utf8, length)
        StrPut(str, &utf8, length, "UTF-8")
        DllCall("shlwapi\IStream_Write", "ptr", this.pStream, "ptr", &utf8, "uint", length, "uint")
    }

    LoadFromFile( filepath ) {
        DllCall("shlwapi\SHCreateStreamOnFileEx"
                    ,   "wstr", filepath
                    ,   "uint", 0x0             ; STGM_READ
                    ,   "uint", 0x80            ; FILE_ATTRIBUTE_NORMAL
                    ,    "int", False           ; fCreate is ignored when STGM_CREATE is set.
                    ,    "ptr", 0               ; pstmTemplate (reserved)
                    ,   "ptr*", pFileStream:=0
                    ,   "uint")
        DllCall("shlwapi\IStream_Size", "ptr", pFileStream, "uint64*", size:=0, "uint")
        DllCall("shlwapi\IStream_Copy", "ptr", pFileStream , "ptr", this.pStream, "uint", size, "uint")
        ObjRelease(pFileStream)
    }

    RandomBoundary() {
        str := "0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z"
        Sort, str, D| Random
        str := StrReplace(str, "|")
        Return SubStr(str, 1, 12)
    }

    MimeType(FileName) {
        n := FileOpen(FileName, "r").ReadUInt()
        Return (n        = 0x474E5089) ? "image/png"
            :  (n        = 0x38464947) ? "image/gif"
            :  (n&0xFFFF = 0x4D42    ) ? "image/bmp"
            :  (n&0xFFFF = 0xD8FF    ) ? "image/jpeg"
            :  (n&0xFFFF = 0x4949    ) ? "image/tiff"
            :  (n&0xFFFF = 0x4D4D    ) ? "image/tiff"
            :  "application/octet-stream"
    }
}

webhookPost(data := 0){
    data := data ? data : {}

    url := options.webhookLink

    if (data.pings){
        data.content := data.content ? data.content " <@" options.DiscordUserID ">" : "<@" options.DiscordUserID ">"
    }

    payload_json := "
		(LTrim Join
		{
			""content"": """ data.content """,
			""embeds"": [{
                " (data.embedAuthor ? """author"": {""name"": """ data.embedAuthor """" (data.embedAuthorImage ? ",""icon_url"": """ data.embedAuthorImage """" : "") "}," : "") "
                " (data.embedTitle ? """title"": """ data.embedTitle """," : "") "
				""description"": """ data.embedContent """,
                " (data.embedThumbnail ? """thumbnail"": {""url"": """ data.embedThumbnail """}," : "") "
                " (data.embedImage ? """image"": {""url"": """ data.embedImage """}," : "") "
                " (data.embedFooter ? """footer"": {""text"": """ data.embedFooter """}," : "") "
				""color"": """ (data.embedColor ? data.embedColor : 0) """
			}]
		}
		)"

    if ((!data.embedContent && !data.embedTitle) || data.noEmbed)
        payload_json := RegExReplace(payload_json, ",.*""embeds.*}]", "")
    

    objParam := {payload_json: payload_json}

    for i,v in (data.files ? data.files : []) {
        objParam["file" i] := [v]
    }

    try {
        CreateFormData(postdata, hdr_ContentType, objParam)

        WebRequest := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        WebRequest.Open("POST", url, true)
        WebRequest.SetRequestHeader("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        WebRequest.SetRequestHeader("Content-Type", hdr_ContentType)
        WebRequest.SetRequestHeader("Pragma", "no-cache")
        WebRequest.SetRequestHeader("Cache-Control", "no-cache, no-store")
        WebRequest.SetRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT")
        WebRequest.Send(postdata)
        WebRequest.WaitForResponse()
    } catch e {
        logMessage("[webhookPost] Error creating webhook data:")
        logMessage(e, 1)
        ; MsgBox, 0, Webhook Error, % "An error occurred while creating the webhook data: " e
        return
    }
}

HasVal(haystack, needle) {
    for index, value in haystack
        if (value = needle)
            return index
    if !(IsObject(haystack))
        throw Exception("Bad haystack!", -1, haystack)
    return 0
}

global possibleDowns := ["w","a","s","d","Space","Enter","Esc","r"]
liftKeys(){
    for i,v in possibleDowns {
        Send {%v% Up}
    }
}

stop(terminate := 0, restart := 0) {
    global
    if (running && !restart){
        running := 0
        updateStatus("Macro Stopped")
    }

    if (terminate){
        options.WasRunning := 0
    }

    DetectHiddenWindows, On
    for i,v in pathsRunning {
        logMessage("[stop] Exiting running path: " . v, 1)
        WinClose, % v
    }

    liftKeys()
    removeDim()

    if (!restart){
        WinClose, % mainDir . "lib\status.ahk"
    }

    if (camFollowMode){
        rotateCameraMode()
    }

    applyNewUIOptions()
    saveOptions()

    if (terminate){
        logMessage("[stop] Terminating application.")
        OutputDebug, Terminated
        ExitApp
    }
}

global pauseDowns := []
global paused := 0
handlePause(){
    paused := !paused
    if (A_IsPaused){
        ResumePaths()

        updateStatus("Macro Running")
        Gui, mainUI:+LastFoundExist
        WinSetTitle, % "dolphSol Macro " version " (Running)"

        applyNewUIOptions()
        saveOptions()
        updateUIOptions()

        Pause, Off ; Unpause the script
    } else {
        PausePaths()

        updateStatus("Macro Paused")
        Gui, mainUI:+LastFoundExist
        WinSetTitle, % "dolphSol Macro " version " (Paused)"
      
        updateUIOptions()
        Gui mainUI:Show

        Pause, On, 1 ; Pause the main thread
    }
}

StopPaths() {
    global pathsRunning, camFollowMode

    logMessage("Paths running: " pathsRunning.Length())

    ; Close external AHK files
    DetectHiddenWindows, On
    for _, v in pathsRunning {
        logMessage("[StopPaths] Stopping path: " . v, 1)
        WinClose, % v
        pathsRunning.Remove(HasVal(pathsRunning,v))
    }

    liftKeys()
    removeDim()

    if (camFollowMode){
        rotateCameraMode()
    }

    saveOptions()
}

PausePaths() {
    global pathsRunning

    logMessage("Paths running: " pathsRunning.Length())
    if (pathsRunning.Length() = 0) {
        return
    }

    ; Send Pause to external AHK files
    DetectHiddenWindows, On
    WM_COMMAND := 0x0111
    ID_FILE_PAUSE := 65403
    for _, v in pathsRunning {
        logMessage("[PausePaths] Pausing path: " . v, 1)
        PostMessage, WM_COMMAND, ID_FILE_PAUSE,,, % v ahk_class AutoHotkey

        hWnd := WinExist(v "ahk_class AutoHotkey")
        logMessage("Paused: " JEE_AhkWinIsPaused(hWnd), 2)
    }

    pauseDowns := []
    for i,v in possibleDowns {
        state := GetKeyState(v)
        if (state){
            pauseDowns.Push(v)
            Send {%v% Up}
        }
    }
}

ResumePaths() {
    logMessage("Paths running: " pathsRunning.Length())
    if (pathsRunning.Length() = 0) {
        return
    }

    ; Send Un-Pause to external AHK files
    DetectHiddenWindows, On
    WM_COMMAND := 0x0111
    ID_FILE_PAUSE := 65403
    for i, v in pathsRunning {
        logMessage("[ResumePaths] Resuming path: " . v, 1)
        PostMessage, WM_COMMAND, ID_FILE_PAUSE,,, % v ahk_class AutoHotkey

        hWnd := WinExist(v "ahk_class AutoHotkey")
        logMessage("Paused: " JEE_AhkWinIsPaused(hWnd), 2)
    }

    ; Restore any previously paused key states
    WinActivate, ahk_id %robloxId%
    for i, v in pauseDowns {
        Send {%v% Down}
    }
}

; JEE_ScriptIsPaused - Detects if an external script is paused
JEE_AhkWinIsPaused(hWnd) {
	vDHW := A_DetectHiddenWindows
	DetectHiddenWindows, On
	SendMessage, 0x211,,,, % "ahk_id " hWnd ;WM_ENTERMENULOOP := 0x211
	SendMessage, 0x212,,,, % "ahk_id " hWnd ;WM_EXITMENULOOP := 0x212
	hMenuBar := DllCall("GetMenu", Ptr,hWnd, Ptr)
	hMenuFile := DllCall("GetSubMenu", Ptr,hMenuBar, Int,0, Ptr)
	;ID_FILE_PAUSE := 65403
	vState := DllCall("GetMenuState", Ptr,hMenuFile, UInt,65403, UInt,0, UInt)
	vIsPaused := (vState >> 3) & 1
	DetectHiddenWindows, % vDHW
	return vIsPaused
}

global regWalkFactor := 1.25 ; since i made the paths all with vip, normalize

getWalkTime(d){
    return d*(1 + (regWalkFactor-1)*(1-options.VIP))
}

walkSleep(d){
    Sleep, % getWalkTime(d)
}

global azertyReplace := {"w":"z","a":"q"}

walkSend(k,t){
    if (options.AzertyLayout && azertyReplace[k]){
        k := azertyReplace[k]
    }
    Send, % "{" . k . (t ? " " . t : "") . "}"
}

press(k, duration := 50) {
    walkSend(k,"Down")
    walkSleep(duration)
    walkSend(k,"Up")
}
press2(k, k2, duration := 50) {
    walkSend(k,"Down")
    walkSend(k2,"Down")
    walkSleep(duration)
    walkSend(k,"Up")
    walkSend(k2,"Up")
}

reset() {
    global atSpawn

    ; if (atSpawn) {
    ;     return
    ; }

    press("Esc",150)
    Sleep, 50 * delayMultiplier
    press("r",150)
    Sleep, 50 * delayMultiplier
    press("Enter",150)
    Sleep, 50 * delayMultiplier

    atSpawn := 1
}
jump() {
    press("Space")
}

arcaneTeleport(){
    press("x",50)
}

; main stuff

global initialized := 0
global running := 0
global isFirstScan := 0
global Storage_YPos_Scan := 0
global Storage_YOffset_Scan := 0

initialize() {
    initialized := 1

    if (disableAlignment) {
        ; Re-enable for reconnects
        disableAlignment := false
    } else {
        alignCamera()
    }
}

resetZoom(){
    Loop 2 {
        if (checkInvOpen()){
            clickMenuButton(1)
        } else {
            break
        }
        Sleep, 400
    }

    ; press("i", 1000)
    ; Sleep, 200
    ; press("o", 200) ; TODO: Allow user to configure zoom distance
    ; Sleep, 200

    MouseMove, % A_ScreenWidth/2, % A_ScreenHeight/2
    Sleep, 200
    Loop 20 {
        Click, WheelUp
        Sleep, 50
    }
    Loop 10 {
        Click, WheelDown
        Sleep, 50
    }
}

resetCameraAngle(){
    resetZoom()

    ; Get window position and size
    getRobloxPos(pX,pY,width,height)

    ; Pan camera
    centerX := Floor(pX + width/2)
    centerY := Floor(pY + height/2)
    MouseClickDrag(centerX, centerY, centerX, centerY + 50)
}

MouseClickDrag(x1, y1, x2, y2) {
    ; Move to start position
    MoveMouseDll(x1, y1, false)
    Sleep, 50
    Send {RButton Down} ; Press the button
    Sleep, 50
    
    ; Drag to end position
    MoveMouseDll(x2 - x1, y2 - y1, true)
    Sleep, 50
    Send, {RButton Up} ; Release the button
}

MoveMouseDll(x, y, relative := true) {
    MOUSEEVENTF_MOVE := 0x0001
    MOUSEEVENTF_ABSOLUTE := 0x8000
    
    flags := MOUSEEVENTF_MOVE
    if (!relative) {
        flags := flags | MOUSEEVENTF_ABSOLUTE
    }
    
    DllCall("mouse_event", "UInt", flags, "Int", x, "Int", y, "UInt", 0, "UInt", 0)
}

; MouseClickDragDll(button, x1, y1, x2, y2) {
;     MOUSEEVENTF_LEFTDOWN := 0x0002
;     MOUSEEVENTF_LEFTUP := 0x0004
;     MOUSEEVENTF_RIGHTDOWN := 0x0008
;     MOUSEEVENTF_RIGHTUP := 0x0010
    
;     buttonDown := (button = "Right") ? MOUSEEVENTF_RIGHTDOWN : MOUSEEVENTF_LEFTDOWN
;     buttonUp := (button = "Right") ? MOUSEEVENTF_RIGHTUP : MOUSEEVENTF_LEFTUP

;     ; Move to start position
;     MoveMouse(x1, y1, false)
;     Sleep, 50
    
;     ; Press the button
;     ; DllCall("mouse_event", "UInt", buttonDown, "Int", 0, "Int", 0, "UInt", 0, "UInt", 0)
;     Send {RButton Down}
;     Sleep, 50
    
;     ; Drag to end position
;     MoveMouse(x2 - x1, y2 - y1, true)
;     Sleep, 50
    
;     ; Release the button
;     Send, {RButton Up}
;     ; DllCall("mouse_event", "UInt", buttonUp, "Int", 0, "Int", 0, "UInt", 0, "UInt", 0)
; }

; Paths

rotateCameraMode(){
    ; Initialize retry counter
    static retryCount := 0
    maxRetries := 5 ; Set the maximum number of retries

    ; Update to the new camera mode
    camFollowMode := !camFollowMode
    mode := camFollowMode ? "Follow" : "Default"

    press("Esc")
    Sleep, 500
    press("Tab")
    Sleep, 500
    press("Down")
    Sleep, 150 * delayMultiplier
    press("Right")
    Sleep, 150 * delayMultiplier
    press("Right")
    Sleep, 150 * delayMultiplier

    ; If enabled, use OCR to confirm the camera mode change
    while (options.OCREnabled && !containsText(1055, 305, 120, 30, mode)) {
        ; Avoid infinite loop
        if (retryCount >= maxRetries) {
            logMessage("[rotateCameraMode] Failed to change camera mode to " mode)
            camFollowMode := !camFollowMode ; Reset to previous state
            retryCount := 0 ; Reset retry counter for the next call
            return
        }

        press("Right")
        Sleep, 150 * delayMultiplier

        retryCount++
    }

    press("Esc")
    Sleep, 250

    ; Reset retry counter after successful execution
    retryCount := 0
}

alignCamera(){
    startDim(1,"Aligning Camera, Please wait...")

    WinActivate, % "ahk_id " GetRobloxHWND()
    Sleep, 500

    closeChat()
    Sleep, 200

    reset()
    Sleep, 100

    rotateCameraMode() ; Follow

    clickMenuButton(2)
    Sleep, 500
    
    getRobloxPos(rX,rY,rW,rH)
    MouseMove, % rX + rW*0.15, % rY + 44 + rH*0.05 + options.BackOffset
    Sleep, 200
    MouseClick
    Sleep, 200

    rotateCameraMode() ; Default(Classic)
    ;resetCameraAngle() ; Fix angle before aligning direction
    Sleep, 100

    walkSend("d","Down")
    walkSleep(200)
    jump()
    walkSleep(400)
    walkSend("d","Up")
    walkSend("w","Down")
    walkSleep(500)
    jump()
    walkSleep(900)
    walkSend("w","Up")

    rotateCameraMode() ; Follow
    Sleep, 1500
    rotateCameraMode() ; Default(Classic)
    ;resetCameraAngle()

    ; reset() ; Redundant, handleCrafting() will use align() if needed
    removeDim()
    Sleep, 2000
}

align(){ ; align v2
    if (isSpawnCentered && forCollection){
        isSpawnCentered := 0
        atSpawn := 0
        return
    }
    updateStatus("Aligning Character")
    if (atSpawn){
        atSpawn := 0
    } else {
        reset()
        Sleep, 2000
    }

    walkSend("d","Down")
    walkSend("w","Down")
    walkSleep(2500)
    walkSend("w","Up")
    walkSleep(750)
    walkSend("d","Up")
    Sleep, 50
    press("a",2500)
    Sleep, 50
}

collect(num){
    if (!options["ItemSpot" . num]){
        return
    }
    Loop, 6 
    {
        Send {f}
        Sleep, 75
    }
    Send {e}
    Sleep, 50
}

runPath(pathName,voidPoints,noCenter = 0){
    try {
        targetDir := pathDir . pathName . ".ahk"
        if (!FileExist(targetDir)){
            MsgBox, 0, % "Error",% "Path file: " . targetDir . " does not exist."
            return
        }
        if (HasVal(pathsRunning,targetDir)){
            return
        }
        pathsRunning.Push(targetDir)
        
        DetectHiddenWindows, On
        Run, % """" . A_AhkPath . """ """ . targetDir . """"
        pathRuntime := A_TickCount

        stopped := 0

        Loop 5 {
            if (WinExist(targetDir)){
                break
            }
            Sleep, 200
        }

        getRobloxPos(rX,rY,width,height)
        scanPoints := [[rX+1,rY+1],[rX+width-2,rY+1],[rX+1,rY+height-2],[rX+width-2,rY+height-2]]

        voidPoints := voidPoints ? voidPoints : []
        startTick := A_TickCount
        expectedVoids := 0
        voidCooldown := 0

        while (WinExist(targetDir)){
            if (!running){
                stopped := 1
                break
            }

            if (A_IsPaused){
                Sleep, 100
                continue
            }

            for i,v in voidPoints {
                if (v){
                    if (A_TickCount-startTick >= getWalkTime(v)){
                        expectedVoids += 1
                        voidPoints[i] := 0
                    }
                }
            }

            blackCorners := 0
            for i,point in scanPoints {
                PixelGetColor, pColor, % point[1], % point[2], RGB
                blackCorners += compareColors(pColor,0x000000) < 8
            }
            PixelGetColor, pColor, % rX+width*0.5, % rY+height*0.5, RGB
            centerBlack := compareColors(pColor,0x000000) < 8
            if (blackCorners = 3 && centerBlack){
                if (!voidCooldown){
                    voidCooldown := 5
                    expectedVoids -= 1
                    if (expectedVoids < 0){
                        stopped := 1
                        break
                    }
                }
            }
            Sleep, 225
            voidCooldown := Max(0,voidCooldown-1)
        }
        ; elapsedTime := (A_TickCount - pathRuntime)//1000
        ; logMessage("[runPath] " pathName " completed in " elapsedTime " seconds")

        if (stopped){
            WinClose, % targetDir
            isSpawnCentered := 0
            atSpawn := 1
        } else if (!noCenter) {
            isSpawnCentered := 1
        }
        liftKeys()
        pathsRunning.Remove(HasVal(pathsRunning,targetDir))
    } catch e {
        MsgBox, 0,Path Error,% "An error occurred when running path: " . pathDir . "`n:" . e
    }
}

searchForItems(){
    updateStatus("Searching for Items")    
    atSpawn := 0

    runPath("searchForItems",[8250,18000],1)

    options.CollectionLoops += 1

    ; logMessage("[searchForItems] Items collected")
}

doObby(){
    updateStatus("Doing Obby")
    
    runPath("doObby",[],1)

    options.ObbyAttempts += 1
}

obbyRun(){
    global lastObby
    Sleep, 250
    doObby()
    lastObby := A_TickCount
    Sleep, 100
}

walkToJakesShop(){
    press("w",800)
    press("a",1200)
}

walkToPotionCrafting(){
    sleep, 2000
    walkSend("w","Down")
    walkSend("a","Down")
    walkSleep(3800)
    walkSend("a","Up")
    walkSleep(675)
    walkSend("w","Up")
    walkSend("a","Down")
    walkSleep(777)
    jump()
    walkSend("w","Down")
    walkSleep(200)
    walkSend("w","Up")
    walkSend("a","Down")
    walkSleep(800)
    walkSend("s","Down")
    walkSleep(235)
    walkSend("s","Up")
    walkSleep(1225)
    jump()
    walkSleep(350)
    walkSend("a","Up")
    walkSend("a","Down")
    walkSleep(2500)
    press("s",500)
    walkSend("a","Up")
    walkSend("s","Down")
    walkSleep(100)
    jump()
    walkSleep(800)
    walkSend("a","Down")
    walkSleep(400)
    jump()
    walkSleep(200)
    walkSend("s","Up")
    walkSleep(500)
    jump()
    walkSleep(740)
    walkSend("a","up")
    walkSleep(200)
    walkSend("s","down")
    walkSleep(3050)
    walkSend("s","up")
    Sleep, 200
}

; End of paths


closeChat(){
    offsetX := 75
    offsetY := 25 ; Changed from 12
    if (options["RobloxUpdatedUI"] = 2) {
        offsetX := 144
        offsetY := 40
    }

    getRobloxPos(pX,pY,width,height)
    PixelGetColor, chatCheck, % pX + offsetX, % pY + offsetY, RGB
    isWhite := compareColors(chatCheck,0xffffff) < 16
    isGray := compareColors(chatCheck,0xc3c3c3) < 16
    if (isWhite || isGray){ ; is chat open??
        ClickMouse(pX + offsetX, pY + offsetY)
    }
}
*/


checkInvOpen(){
    checkPos := getPositionFromAspectRatioUV(0.861357, 0.494592,storageAspectRatio)
    PixelGetColor, checkC, % checkPos[1], % checkPos[2], RGB
    alreadyOpen := compareColors(checkC,0xffffff) < 8
    return alreadyOpen
}

mouseActions(){
    updateStatus("Performing Mouse Actions")

    ; close jake shop if popup
    openP := getPositionFromAspectRatioUV(0.718,0.689,599/1015)
    openP2 := getPositionFromAspectRatioUV(0.718,0.689,1135/1015)
    ClickMouse(openP[1], openP2[2])

    ; re equip
    if (options.AutoEquipEnabled){
        logMessage("Re-equipping user selected aura")
        closeChat()
        alreadyOpen := checkInvOpen()

        if (!alreadyOpen){
            clickMenuButton(1)
        }
        Sleep, 100
        sPos := getPositionFromAspectRatioUV(options.AutoEquipX,options.AutoEquipY,storageAspectRatio)
        MouseMove, % sPos[1], % sPos[2]
        Sleep, 300
        MouseClick
        Sleep, 100
        ePos := getPositionFromAspectRatioUV(storageEquipUV[1],storageEquipUV[2],storageAspectRatio)
        MouseMove, % ePos[1], % ePos[2]
        Sleep, 300
        MouseClick
        Sleep, 100
        clickMenuButton(1)
        Sleep, 250
    }

    if (options.ExtraRoblox){ ; for afking my 3rd alt lol
        MouseMove, 2150, 700
        Sleep, 300
        MouseClick
        Sleep, 250
        jump()
        Sleep, 500
        Loop 5 {
            Send {f}
            Sleep, 200
        }
        MouseMove, 2300,800
        Sleep, 300
        MouseClick
        Sleep, 250
    }
}

isFullscreen() {
	WinGetPos,,, w, h, Roblox
	return (w = A_ScreenWidth && h = A_ScreenHeight)
}

; used from natro
GetRobloxHWND(){
	if (hwnd := WinExist("Roblox ahk_exe RobloxPlayerBeta.exe")) {
		return hwnd
	} else if (WinExist("Roblox ahk_exe ApplicationFrameHost.exe")) {
		ControlGet, hwnd, Hwnd, , ApplicationFrameInputSinkWindow1
		return hwnd
	} else {
        logMessage("[GetRobloxHWND] Roblox Process: Unknown", 1)
        Sleep, 5000
		return 0
    }
}

getRobloxPos(ByRef x := "", ByRef y := "", ByRef width := "", ByRef height := "", hwnd := ""){
    if !hwnd
        hwnd := GetRobloxHWND()
    VarSetCapacity( buf, 16, 0 )
    DllCall( "GetClientRect" , "UPtr", hwnd, "ptr", &buf)
    DllCall( "ClientToScreen" , "UPtr", hwnd, "ptr", &buf)

    x := NumGet(&buf,0,"Int")
    y := NumGet(&buf,4,"Int")
    width := NumGet(&buf,8,"Int")
    height := NumGet(&buf,12,"Int")

    ; What to do if Roblox isn't open
    if (macroStarted && !width) {
        attemptReconnect()
        return
    }
}

; screen stuff

checkHasObbyBuff(BRCornerX, BRCornerY, statusEffectHeight){
    if (!options.CheckObbyBuff){
        return 1
    }
    global obbyStatusEffectColor,obbyStatusEffectColor2,hasObbyBuff,statusEffectSpace
    Loop, 5
    {
        targetX := BRCornerX - (statusEffectHeight/2) - (statusEffectHeight + statusEffectSpace)*(A_Index-1)
        targetY := BRCornerY - (statusEffectHeight/2)
        PixelGetColor, color, targetX, targetY, RGB
        if (compareColors(color, obbyStatusEffectColor) < 16){
            hasObbyBuff := 1
            options.ObbyCompletes += 1
            updateStatus("Completed Obby")
            return 1
        }
    }  
    hasObbyBuff := 0
    return 0
}

spawnCheck(){ ; not in use
    if (!options.ExtraAlignment) {
        return 1
    }
    getRobloxPos(rX, rY, width, height)
    startPos := getFromUV(-0.55,-0.9,rX,rY,width,height)
    targetPos := getFromUV(-0.45,-0.9,rX,rY,width,height)
    startX := startPos[1]
    startY := startPos[2]
    distance := targetPos[1]-startX
    bitMap := Gdip_BitmapFromScreen(startX "|" startY "|" distance "|1")
    vEffect := Gdip_CreateEffect(5,50,30)
    Gdip_BitmapApplyEffect(bitMap,vEffect)
    ;Gdip_SaveBitmapToFile(bitMap,"test1.png")
    prev := 0
    greatestDiff := 0
    cat := 0
    Loop, %distance%
    {
        c := Gdip_GetPixelColor(bitMap,A_Index-1,0,1)
        if (!prev){
            prev := c
        }
        comp := compareColors(prev,c)
        greatestDiff := Max(comp,greatestDiff)
        if (greatestDiff = comp){
            cat := A_Index
        }
        prev := c
    }
    Gdip_DisposeEffect(vEffect)
    Gdip_DisposeBitmap(bitMap)
    return greatestDiff >= 5
}

getColorComponents(color){
    return [color & 255, (color >> 8) & 255, (color >> 16) & 255]
}

compareColors(color1, color2) ; determines how far apart 2 colors are
{
    color1V := getColorComponents(color1)
    color2V := getColorComponents(color2)

    cV := [color1V[1] - color2V[1], color1V[2] - color2V[2], color1V[3] - color2V[3]]
    dist := Abs(cV[1]) + Abs(cV[2]) + Abs(cV[3])

    if (color2 not in 0x000000,0xffffff,0x393b3d){
        logMessage("[compareColors] " color1 " " color2 " " dist, 1)
    }
    return dist
}

clamp(x,mn,mx){
    nX := Min(x,mx)
    nX := Max(nX,mn)
    return nX
}

; menu ui stuff (ingame)

global menuBarOffset := 20 ;10 pixels from left edge

getMenuButtonPosition(num, ByRef posX := "", ByRef posY := ""){ ; num is 1-7, 1 being top, 7 only existing if you are the private server owner
    num := options["InOwnPrivateServer"] ? num : num + 1
    
    getRobloxPos(rX, rY, width, height)

    menuBarVSpacing := 10.5*(height/1080)
    menuBarButtonSize := 58*(width/1920)
    menuEdgeCenter := [rX + menuBarOffset, rY + (height/2)]
    startPos := [menuEdgeCenter[1]+(menuBarButtonSize/2),menuEdgeCenter[2]+(menuBarButtonSize/4)-(menuBarButtonSize+menuBarVSpacing-1)*3.5] ; final factor = 0.5x (x is number of menu buttons visible to all, so exclude private server button)
    
    posX := startPos[1]
    posY := startPos[2] + (menuBarButtonSize+menuBarVSpacing)*(num-0.5)

    MouseMove, % posX, % posY
}

clickMenuButton(num){
    getMenuButtonPosition(num, posX, posY)

    MouseMove, posX, posY
    Sleep, 200
    MouseClick
}

; storage ratio: w1649 : h952
global storageAspectRatio := 952/1649
global storageEquipUV := [-0.625,0.0423] ; equip button

getUV(x,y,oX,oY,width,height){
    return [((x-oX)*2 - width)/height,((y-oY)*2 - height)/height]
}

getFromUV(uX,uY,oX,oY,width,height){
    return [Floor((uX*height + width)/2)+oX,Floor((uY*height + height)/2)+oY]
}

getAspectRatioSize(ratio, width, height){
    fH := width*ratio
    fW := height*(1/ratio)

    if (height >= fH){
        fW := width
    } else {
        fH := height
    }

    return [Floor(fW+0.5), Floor(fH+0.5)]
}

getPositionFromAspectRatioUV(x,y,aspectRatio){
    getRobloxPos(rX, rY, width, height)
    
    ar := getAspectRatioSize(aspectRatio, width, height)

    oX := Floor((width-ar[1])/2) + rX
    oY := Floor((height-ar[2])/2) + rY

    p := getFromUV(x,y,oX,oY,ar[1],ar[2]) ; [Floor((x*ar[2] + ar[1])/2)+oX,Floor((y*ar[2] + ar[2])/2)+oY]

    return p
}

getAspectRatioUVFromPosition(x,y,aspectRatio){
    getRobloxPos(rX, rY, width, height)
    
    ar := getAspectRatioSize(aspectRatio, width, height)

    oX := Floor((width-ar[1])/2) + rX
    oY := Floor((height-ar[2])/2) + rY

    p := getUV(x,y,oX,oY,ar[1],ar[2])

    return p
}

; Convert 1920x1080 coordinates to UV coordinates and then to user's screen coordinates
convertScreenCoordinates(x, y, ByRef cX := "", ByRef cY := "") {
    ; aspectRatio := 1920/1080
    
    ; getRobloxPos(rX, rY, width, height)
    ; robloxAspectRatio := width/height

    ; Convert screen coordinates to UV coordinates
    ; uv := getAspectRatioUVFromPosition(x, y, aspectRatio)

    ; Convert UV coordinates back to screen coordinates for mouse clicks
    ; cPos := getPositionFromAspectRatioUV(uv[1], uv[2], robloxAspectRatio)
    ; cX := cPos[1]
    ; cY := cPos[2]
    
    ; Use original 1920x1080 coordinates to avoid conversion issues as of 6/24
    cX := x
    cY := y
}

getScreenCenter(){
    getRobloxPos(rX, rY, width, height)
    return [rX + width/2, rY + height/2]
}

ShowMousePos() {
    MouseGetPos, mx,my
    p := getAspectRatioUVFromPosition(mx,my,storageAspectRatio)
    c := convertScreenCoordinates(mx,my)
    Tooltip, % "Current: " mx ", " my "`n"
            . "UV Ratio: " p[1] ", " p[2] "`n"
            . "1920x1080: " c[1] ", " c[2]
    Sleep, 2500
    Tooltip
}

isCraftingMenuOpen() {
    ; if (options.OCREnabled) {
    if (containsText(250, 30, 200, 75, "Close")) {
        return 1
    }
        ; Don't return 0 so it uses backup non-ocr check
    ; }

    convertScreenCoordinates(290, 40, closeX, closeY)
    PixelSearch, blackX, blackY, closeX, closeY, closeX+100, closeY+40, 0x060A09, 16, Fast RGB
    PixelSearch, whiteX, whiteY, closeX, closeY, closeX+100, closeY+40, 0xFFFFFF, 16, Fast RGB
    if (blackX && whiteX) {
        logMessage("Close button found")
        return 1
    }

    return 0
}

clickCraftingSlot(num,isPotionSlot := 0){
    getRobloxPos(rX,rY,width,height)

    scrollCenter := 0.17*width + rX
    scrollerHeight := 0.78*height
    scrollStartY := 0.15*height + rY

    slotHeight := (width/1920)*129 ; Changed 138 to 129 - Fixed gilded coin in Era 7

    if (isPotionSlot){ ; potion select sub menu
        scrollCenter := 0.365*width + rX
        scrollerHeight := 0.38*height
        scrollStartY := 0.325*height + rY
        ; slotHeight is the same for both crafting menus as of Era 7. May change again in the future
    }

    MouseMove, % scrollCenter, % scrollStartY-2
    Sleep, 250
    Click, WheelDown ; in case res upd
    Sleep, 100
    Loop 10 {
        Click, WheelUp
        Sleep, 75
    }

    fittingSlots := Floor(scrollerHeight/slotHeight) + (Mod(scrollerHeight, slotHeight) > height*0.045)
    if (fittingSlots < num){
        rCount := num-fittingSlots
        if (num = 13 && !isPotionSlot){
            rCount += 5
        }
        Loop %rCount% {
            Click, WheelDown
            Sleep, 200
        }
        if (isPotionSlot || (num != 13)){
            MouseMove, % scrollCenter, % scrollStartY + slotHeight*(fittingSlots-1) + rCount
        } else {
            MouseMove, % scrollCenter, % scrollStartY + slotHeight*(fittingSlots-3) + rCount
        }
    } else {
        MouseMove, % scrollCenter, % scrollStartY + slotHeight*(num-1)
    }

    Sleep, 300
    MouseClick
    Sleep, 200
    MouseGetPos, mouseX,mouseY
    MouseMove, % mouseX + width/4, % mouseY
}

craftingClickAdd(totalSlots, maxes := 0, isGear := 0) {
    if (!maxes){
        maxes := []
    }

    getRobloxPos(rX,rY,width,height)

    startXAmt := 0.6*width + rX
    startX := 0.635*width + rX
    startY := 0.413*height + rY
    slotSize := 0.033*height

    if (isGear){
        startXAmt := 0.582*width + rX
        startX := 0.62*width + rX
        startY := 0.395*height + rY
        slotSize := 0.033*height
    }

    fractions := [1, 0.5, 0.1, 0]

    slotI := 1 ; Maybe use A_Index instead?
    Loop %totalSlots% {
        ; Skip crafting slot if already complete
        slotPosY := startY + slotSize*(A_Index-1)
        ; PixelSearch, pX, pY, startX-5, slotPosY-5, startX+5, slotPosY+5, 0x158210, 8, Fast RGB
        ; if (pX && pY) {
        ; }

        ; 6/23 - Incorrectly detecting gilded coin slot as completed
        ; 0x178111 seems to work better. More testing needed to determine if stella and jake completed are different
        ; Bypassing for now
        PixelGetColor, checkC, startX, slotPosY, RGB
        ; logMessage("Slot " slotI " Color: " checkC, 1)
        if (!isGear && compareColors(checkC, 0x178111) < 6) {
            logMessage("Skipping completed slot " slotI " - color: " checkC, 1)
            slotI += 1
            continue
        }

        for _, fraction in fractions {
            ; Calculate the input quantity based on the maximum amount
            inputQty := Max(1, Floor(maxes[slotI] * fraction))
            ; logMessage("Crafting Slot " slotI " - Input Quantity: " inputQty " - Fraction: " fraction, 1)

            MouseMove, % (slotI == 1) ? startX : startXAmt, % slotPosY
            Sleep, 200
            ; MouseClick, WheelUp ; Test if this is still needed
            ; Sleep, 200
            MouseClick
            Sleep, 200
            Send % inputQty
            Sleep, 200

            ; Click the "Add" button
            MouseMove, % startX, % slotPosY
            Sleep, 200
            Loop 3 {
                MouseClick
                Sleep, 200
            }

            ; Check if the crafting slot is complete
            PixelGetColor, checkC, startX, slotPosY, RGB
            if (compareColors(checkC, craftingCompleteColor) < 20) {
                break
            }

            ; Avoid the fraction loop if the quantity is 1
            if (inputQty = 1) {
                break
            }
        }

        slotI += 1
    }

    ; Click the "Craft" button
    if (isGear){
        MouseMove, % 0.43*width + rX, % 0.635*height + rY
    } else {
        MouseMove, % 0.46*width + rX, % 0.63*height + rY
    }
    Sleep, 250
    MouseClick
}

; craftLocation: 0 = none, 1 = Stella, 2 = Jake
; retryCount: limit retry attempts to prevent infinite loop
handleCrafting(craftLocation := 0, retryCount := 0){
    static potionAutoAdd := 0

    getRobloxPos(rX,rY,rW,rH)
    if (retryCount = 0) {
        updateStatus("Beginning Crafting Cycle")
        Sleep, 2000
    } else if (retryCount = 2) {
        updateStatus("Crafting Failed. Fixing Camera...")
        Sleep, 2000
        alignCamera()
        Sleep, 500
        handleCrafting(0,retryCount+1)
        return
    } else if (retryCount > 2) {
        updateStatus("Crafting Failed. Continuing...")
        Sleep, 2000
        return
    }

    if (options.PotionCraftingEnabled && craftLocation != 2){
        align()
        updateStatus("Walking to Stella's Cave (Crafting)")
        walkToPotionCrafting()
        Sleep, % (StellaPortalDelay && StellaPortalDelay > 0) ? StellaPortalDelay : 0
        resetCameraAngle()
        Sleep, 2000
        walkSend("a","Down")
        walkSleep(500)
        walkSend("a","Up")
        walkSleep(500)
        press("f")
        walkSleep(500)

        ; Continue moving away from cauldron to avoid exiting menu early
        walkSend("a","Down")
        walkSleep(1000)
        walkSend("a","Up")
        walkSleep(500)

        ; OCR - Check for "Close" button
        if (!isCraftingMenuOpen()) {
            updateStatus("Failed to open Potion menu")
            alignCamera()
            handleCrafting(1,retryCount+1)
            return
        }

        updateStatus("Crafting Potions")

        if (options.potionAutoAddEnabled) {
            if ((getUnixTime() - options.LastPotionAutoAdd) >= ((options.PotionAutoAddInterval-1) * 60)) { ; 1m buffer to avoid waiting another cycle
                options.LastPotionAutoAdd := getUnixTime()

                ; Determine which potion to Auto Add next
                Loop 3 {
                    v := options["PotionCraftingSlot" A_Index]
                    if (v) {
                        maxIndex := A_Index
                    }
                }
                potionAutoAdd := (potionAutoAdd >= maxIndex) ? 1 : potionAutoAdd + 1
                logMessage("Auto Add Potion: " potionIndex[potionAutoAdd], 1)
            }
        }

        Loop 3 {
            v := options["PotionCraftingSlot" A_Index]
            logMessage("  Crafting: " potionIndex[v])
            if (v && craftingInfo[potionIndex[v]]){
                info := craftingInfo[potionIndex[v]]
                loopCount := info.attempts
                clickCraftingSlot(info.slot)
                Sleep, 200
                clickCraftingSlot(info.subSlot,1)
                Sleep, 200

                ; Loop %loopCount% {
                craftingClickAdd(info.addSlots,info.maxes)
                Sleep, 200
                ; }

                if (A_Index = potionAutoAdd) { ; Need to make sure this doesn't toggle Auto Add off
                    logMessage("Auto Add potion: " potionIndex[v], 1)
                    enableAutoAdd()
                    Sleep, 200
                }
            }
        }

        ; Click the "Close" button
        MouseMove, % rX + rW*0.175, % rY + rH*0.05
        Sleep, 200
        MouseClick

        alignCamera()
    }
    if (options.ItemCraftingEnabled && craftLocation != 1){
        align()
        updateStatus("Walking to Jake's Shop (Crafting)")
        walkToJakesShop()
        Sleep, 100
        press("f")
        Sleep, 4500
        openP := getPositionFromAspectRatioUV(-0.718,0.689,599/1015)
        openP2 := getPositionFromAspectRatioUV(-0.718,0.689,1135/1015)
        MouseMove, % openP[1], % openP2[2]
        Sleep, 200
        MouseClick
        Sleep, 1000

        ; OCR - Check for "Close" button
        if (!isCraftingMenuOpen()) {
            updateStatus("Failed to open Jake's Shop")
            handleCrafting(2,retryCount+1)
            alignCamera()
            return
        }

        ; Click the "Close" button
        MouseMove, % rX + rW*0.175, % rY + rH*0.05
        Sleep, 200
        MouseClick

        alignCamera()
    }

    reset()
}

; Click Auto Add if not enabled
enableAutoAdd(){
    btnW := 60
    btnH := 25
    convertScreenCoordinates(1080, 670, autoX, autoY)
    PixelSearch,,, autoX, autoY, autoX+btnW, autoY+btnH, 0x30FF20, 20, Fast RGB

    if (ErrorLevel) {
        ClickMouse(autoX+btnW/2, autoY+btnH/2)
        logMessage("Enabled Auto Add", 1)
    } else { ; Skip if Auto Add is already enabled
        logMessage("Auto Add already enabled", 1)
    }
}

waitForInvVisible(){
    Loop 10 {
        alreadyOpen := checkInvOpen()
        if (alreadyOpen)
            break
        Sleep, 50
    }
}

screenshotInventories(){ ; from all closed
    updateStatus("Inventory screenshots")
    topLeft := getPositionFromAspectRatioUV(-1.3,-0.9,storageAspectRatio)
    bottomRight := getPositionFromAspectRatioUV(1.3,0.75,storageAspectRatio)
    totalSize := [bottomRight[1]-topLeft[1]+1,bottomRight[2]-topLeft[2]+1]

    closeChat()

    clickMenuButton(1)
    Sleep, 200

    waitForInvVisible()

    ssMap := Gdip_BitmapFromScreen(topLeft[1] "|" topLeft[2] "|" totalSize[1] "|" totalSize[2])
    Gdip_SaveBitmapToFile(ssMap,ssPath)
    Gdip_DisposeBitmap(ssMap)
    try webhookPost({files:[ssPath],embedImage:"attachment://ss.jpg",embedTitle: "Aura Storage"})

    Sleep, 200
    clickMenuButton(3)
    Sleep, 200

    waitForInvVisible()

    itemButton := getPositionFromAspectRatioUV(0.564405, -0.451327, storageAspectRatio)
    MouseMove, % itemButton[1], % itemButton[2]
    Sleep, 200
    MouseClick
    Sleep, 200

    ssMap := Gdip_BitmapFromScreen(topLeft[1] "|" topLeft[2] "|" totalSize[1] "|" totalSize[2])
    Gdip_SaveBitmapToFile(ssMap,ssPath)
    Gdip_DisposeBitmap(ssMap)
    try webhookPost({files:[ssPath],embedImage:"attachment://ss.jpg",embedTitle: "Item Inventory"})

    Sleep, 200
    clickMenuButton(5)
    Sleep, 200

    waitForInvVisible()

    dailyTab := getPositionFromAspectRatioUV(0.5185, -0.4389, storageAspectRatio)
    ClickMouse(dailyTab[1], dailyTab[2])

    ssMap := Gdip_BitmapFromScreen(topLeft[1] "|" topLeft[2] "|" totalSize[1] "|" totalSize[2])
    Gdip_SaveBitmapToFile(ssMap,ssPath)
    Gdip_DisposeBitmap(ssMap)
    try webhookPost({files:[ssPath],embedImage:"attachment://ss.jpg",embedTitle: "Quests"})

    Sleep, 200
    clickMenuButton(5)
    Sleep, 200
}

ClaimQuests() {
    updateStatus("Checking Quests")

    ; Open Quest Menu
    clickMenuButton(5)
    waitForInvVisible()

    dailyTab := getPositionFromAspectRatioUV(0.5185, -0.4389, storageAspectRatio)
    ClickMouse(dailyTab[1], dailyTab[2])

    btnX := 0.6393
    btnYList := [0.0382, 0.1927, 0.3416]

    for _, btnY in btnYList {
        claimButton := getPositionFromAspectRatioUV(btnX, btnY, storageAspectRatio)
        ClickMouse(claimButton[1], claimButton[2])
        Sleep, 250
    }

    ; Close Quest Menu
    clickMenuButton(5)
    Sleep, 200
}

; Simplify frequent code
ClickMouse(posX, posY) {
    MouseMove, % posX, % posY
    Sleep, 500
    MouseClick
    Sleep, 200

    ; Highlight(posX-5, posY-5, 10, 10, 5000) ; Highlight for 5 seconds
}

useItem(itemName, useAmount := 1) {
    updateStatus("Using items")
    logMessage("Using item: " itemName, 1)

    ; Open Inventory
    clickMenuButton(3)
    waitForInvVisible()

    ; Select Items tab
    itemTab := getPositionFromAspectRatioUV(0.564405, -0.451327, storageAspectRatio)
    ClickMouse(itemTab[1], itemTab[2])

    ; Search for item
    searchBar := getPositionFromAspectRatioUV(0.56, -0.39, storageAspectRatio)
    ClickMouse(searchBar[1], searchBar[2])
    Send, % itemName
    Sleep, 200

    ; Select item
    selectItem := getPositionFromAspectRatioUV(-0.18, -0.25, storageAspectRatio)
    ClickMouse(selectItem[1], selectItem[2])

    ; Update quantity
    updateQuantity := getPositionFromAspectRatioUV(-0.70, 0.12, storageAspectRatio)
    ClickMouse(updateQuantity[1], updateQuantity[2])
    Send, % useAmount
    Sleep, 200

    ; Click Use
    clickUse := getPositionFromAspectRatioUV(-0.46, 0.12, storageAspectRatio)
    ClickMouse(clickUse[1], clickUse[2])

    ; Clear search result
    ClickMouse(searchBar[1], searchBar[2])

    ; Close inventory
    clickMenuButton(3)
    Sleep, 200

    ; Special case for "Merchant Teleport"
    if (itemName = "Merchant Teleport") {
        logMessage("Pressing E for Merchant (if they spawned and wait for my python to do the job)", 1)
        Sleep, 500
        Send, {E 3} ; Press E to interact with the NPC
        Sleep, 2500
        
        ; Check for merchant name
        ; containsText(x,y,w,h "mari") and 4 value: x,y,w,h you have to get it yourself in order to work
        ; waitTime - Please adjust it for mari (32500 is mari's 32s wait time before reset and realign your character, same for jester, 
        ; -> if it reset too early, try to increase wait time for mari or jester :)
        Loop, 5 {
            if (containsText(755, 581, 210, 39, "mari") || containsText(755, 581, 210, 39, "jester")) {
                merchantName := containsText(755, 581, 210, 39, "mari") ? "Mari" : "Jester"
                logMessage("[Merchant]: " merchantName " name found!", 1)
                updateStatus("Merchant found! Pausing the macro...")
                
                ; Calculate the wait time for Mari and Jester
                waitTime := (merchantName = "Mari") ? 32500 : 56000
                logMessage("[Merchant]: Merchant timer set, waiting for unpause", 1)

                Sleep, waitTime
                alignCamera()
                Sleep, 2000
                reset()
                Sleep, 500
                break
            }
            Sleep, 350
        }
    }
}

global deviceLastUsed := A_TickCount
global currentBiome

changeBiome() {
    deviceIntervalMS := 20 * 60 * 1000
    sinceLastUsed := A_TickCount - deviceLastUsed
    
    cooldownRemainingSec := Floor(((deviceIntervalMS - sinceLastUsed) / 1000))
    logMessage("Device Cooldown: " cooldownRemainingSec " seconds", 1)

    ; Cooldown check
    if (sinceLastUsed < deviceIntervalMS) {
        return
    }

    ; Change biome
    logMessage("Current Biome: '" currentBiome "'")
    if !(currentBiome in ["Glitched", "Hell", "Null", "Starfall"]) {
        ;"Strange Controller" or "Biome Randomizer"
        logMessage("Changing biome using 'Strange Controller'", 1)

        PausePaths()
        useItem("Strange Controller")
        deviceLastUsed := A_TickCount
        ResumePaths()

        ; Update biome check schedule
        SetTimer, biomeLoop, Off
        biomeLoop()
    }
}

checkBottomLeft(){
    getRobloxPos(rX,rY,width,height)

    start := [rX, rY + height*0.86]
    finish := [rX + width*0.14, rY + height]
    totalSize := [finish[1]-start[1]+1, finish[2]-start[2]+1]
    readMap := Gdip_BitmapFromScreen(start[1] "|" start[2] "|" totalSize[1] "|" totalSize[2])
    ;Gdip_ResizeBitmap(readMap,500,500,1)
    readEffect1 := Gdip_CreateEffect(7,100,-100,50)
    readEffect2 := Gdip_CreateEffect(2,10,100)
    Gdip_BitmapApplyEffect(readMap,readEffect1)
    Gdip_BitmapApplyEffect(readMap,readEffect2)
    Gdip_SaveBitmapToFile(readMap,ssPath)
    OutputDebug, % ocrFromBitmap(readMap)
    Gdip_DisposeBitmap(readMap)
    Gdip_DisposeEffect(readEffect1)
}

getUnixTime() {
    now := A_NowUTC
    EnvSub, now, 1970, seconds
    return now
}

closeRoblox(){
    WinClose, Roblox
    WinClose, % "Roblox Crash"
}

isGameNameVisible() {
    getRobloxPos(pX,pY,width,height)

    ; Game Logo/Name
    x := pX + (width * 0.25)
    y := pY + (height * 0.05)
    w := width // 5
    h := height // 5

    colors := [0xD356FF, 0x8528FF, 0x140E46, 0x000000] ; Lavender, Purple, Dark Blue, Black
    variation := 10

    foundColors := 0

    ; Search for each color in the defined area
    for color in colors {
        PixelSearch, FoundX, FoundY, x, y, x + w, y + h, color, variation, Fast RGB
        if (ErrorLevel = 0) {
            foundColors++
            logMessage("[GameName] Color " color " found at " FoundX ", " FoundY)
            Highlight(FoundX-5, FoundY-5, 10, 10, 5000, "Yellow") ; Temporary for debug
        } else {
            return false
        }
    }
    if (foundColors = colors.Length()) {
        logMessage("[GameName] Colors found: " foundColors " out of " colors.Length())
        Highlight(x, y, w, h, 2500) ; Temporary for debug
        return true
    }
    return false
}

getPlayButtonColorRatio() {
    getRobloxPos(pX,pY,width,height)

    ; Play Button Text
    targetW := height * 0.15
    startX := width * 0.5 - targetW * 0.55
    x := pX + startX
    y := pY + height * 0.8
    w := targetW * 1.1
    h := height * 0.1
    ; OutputDebug, % x ", " y ", " w ", " h
    ; Highlight(x, y, w, h, 5000)

    retrievedMap := Gdip_BitmapFromScreen(x "|" y "|" w "|" h)
    ; Gdip_SaveBitmapToFile(retrievedMap, "retrievedMap.png")
    effect := Gdip_CreateEffect(5,-60,80)
    Gdip_BitmapApplyEffect(retrievedMap,effect)
    ; Gdip_SaveBitmapToFile(retrievedMap, "retrievedMap_effect.png")
    playMap := Gdip_ResizeBitmap(retrievedMap,32,32,0)
    ; Gdip_SaveBitmapToFile(playMap, "playMap.png")
    Gdip_GetImageDimensions(playMap, Width, Height)
    ; OutputDebug, % "playMap dimensions: " Width "w x " Height "h"

    blackPixels := 0
    whitePixels := 0

    Loop, %Width% {
        tX := A_Index-1
        Loop, %Height% {
            tY := A_Index-1
            pixelColor := Gdip_GetPixel(playMap, tX, tY)
            blackPixels += compareColors(pixelColor,0x000000) < 32
            whitePixels += compareColors(pixelColor,0xffffff) < 32
        }
    }
    ; OutputDebug, % "Black Pixels: " blackPixels
    ; OutputDebug, % "White Pixels: " whitePixels

    Gdip_DisposeEffect(effect)
    Gdip_DisposeBitmap(playMap)
    Gdip_DisposeBitmap(retrievedMap)
    
    if (whitePixels > 30 && blackPixels > 30){
        ratio := whitePixels/blackPixels
        OutputDebug, % "ratio: " ratio "`n"

        ; return (ratio > 0.35) && (ratio < 0.65)
        return ratio
    }
    return 0
}

isPlayButtonVisible(){ ; Era 8 Play button: 750,860,420,110 (covers movement area)
    getRobloxPos(pX,pY,width,height)

    ; Play Button Area
    targetW := height * 0.3833
    startX := width * 0.5 - targetW * 0.55
    x := pX + startX
    y := pY + height * 0.8
    w := targetW * 1.1
    h := height * 0.1

    if (containsText(x, y, w, h, "Play") || containsText(x, y, w, h, "Ploy")) { ; Add commonly detected misspelling
        logMessage("[isPlayButtonVisible] Play button detected with OCR")
        return true
    }

    ; Check again after delay to avoid false positives
    ; if (isGameNameVisible()) {
    ;     Sleep, 5000
    ;     return isGameNameVisible()
    ; }

    ; Compare after 5 checks to rule out false positives
    ratioSum := 0
    Loop, 5 {
        ratioSum += getPlayButtonColorRatio()
    }
    ratioAvg := ratioSum / 5
    if (ratioAvg >= 0.09 && ratioAvg <= 0.13) {
        logMessage("[isPlayButtonVisible] Color Ratio: " ratioAvg " (Average of 5 checks)")
        return true
    }
    return false
}

; Assumes button was previously detected using isPlayButtonVisible()
ClickPlay() {
    updateStatus("Game Loaded")

    StopPaths()
    getRobloxPos(pX,pY,width,height)

    rHwnd := GetRobloxHWND()
    if (rHwnd) {
        WinActivate, ahk_id %rHwnd%
    }
    
    ; Click Play
    ClickMouse(pX + (width*0.5), pY + (height*0.85))
    Sleep, 10000

    ; Skip existing aura prompt
    ClickMouse(pX + (width*0.6), pY + (height*0.85))
    Sleep, 2000
    
    ; Enable Auto Roll - Completely removed from Initialize() to avoid toggling when macro is restarted, but game is not
    ClickMouse(pX + (width*0.35), pY + (height*0.95))
}

; Clear RAM by restarting Roblox
; Used with Reconnect setting to relaunch game
ClearRAM() {
    ; Abort conditions
    if (!options.RestartRobloxEnabled || !options.ReconnectEnabled || !running) {
        return 0
    }

    updateStatus("Restarting Roblox to clear RAM")
    sleep, 2000
    rHwnd := GetRobloxHWND()
    if (rHwnd) {
        WinClose, ahk_id %rHwnd%
    }
    attemptReconnect()
    
    return 1 ; Notify calling function that Roblox was restarted
}

; Enable Auto Roll - OCR detect if Auto Roll is OFF and click to enable
enableAutoRoll() {
    getRobloxPos(pX,pY,width,height)

    btnX := pX + (width*0.35)
    btnY := pY + (height*0.95)
    if (containsText(btnX - 100, btnY - 25, 200, 50, "OFF")) {
        ClickMouse(btnX, btnY)
    }
}

/* WIP - Do not use
ReceiveData(wParam, lParam) {
    ; Lock the memory and get the string
    StringAddress := DllCall("GlobalLock", "Ptr", lParam, "Ptr")
    if (StringAddress) {
        currentBiome := StrGet(StringAddress, "UTF-8")  ; Ensure the correct encoding
        DllCall("GlobalUnlock", "Ptr", lParam)
        logMessage("[ReceiveData] Current Biome: " currentBiome)
        ToolTip, % "Current Biome: " currentBiome
        Sleep, 5000
        ToolTip
    }
}
*/

LogError(exc) {
    logMessage("[LogError] Error on line " exc.Line ": " exc.Message)
    try webhookPost({embedContent: "[Error - Main.ahk - Line " exc.Line "]: " exc.Message, embedColor: statusColors["Roblox Disconnected"]})
}

logMessage(message, indent := 0) {
    global loggingEnabled, mainDir, lastLoggedMessage
    maxLogSize := 1048576 ; 1 MB

    if (!loggingEnabled) {
        return
    }

    ; Sanitize message
    message := StrReplace(message, options.WebhookLink, "*WebhookLink*")


    ; Avoid logging the same message again
    if (message = lastLoggedMessage) {
        return
    }
    
    logFile := mainDir . "\macro_log.txt"
    try {
        ; Check the log file size and truncate if necessary
        if (FileExist(logFile) && FileGetSize(logFile) > maxLogSize) {
            FileDelete, %logFile%
        }

        if (indent) {
            message := "    " . message
        }
        FormatTime, fTime, , hh:mm:ss
        FileAppend, % fTime " " message "`n", %logFile%
        OutputDebug, % fTime " " message

        ; Update the last logged message
        lastLoggedMessage := message
    } catch e {
        ; TODO: handle gracefully
        ; ignore error popup for now
    }
}

; Function to get the size of a file
FileGetSize(filePath) {
    FileGetSize, fileSize, %filePath%
    return fileSize
}

; Check if area contains the specified text
containsText(x, y, width, height, text) {
    ; Potential improvement by ignoring non-alphanumeric characters

    ; Highlight(x-10, y-10, width+20, height+20, 2000)
    
    try {
        pbm := Gdip_BitmapFromScreen(x "|" y "|" width "|" height)
        pbm := Gdip_ResizeBitmap(pbm,500,500,true)
        ocrText := ocrFromBitmap(pbm)
        Gdip_DisposeBitmap(pbm)

        if (!ocrText) {
            return false
        }
        ocrText := RegExReplace(ocrText,"(\n|\r)+"," ")
        StringLower, ocrText, ocrText
        StringLower, text, text
        textFound := InStr(ocrText, text)
        if (!textFound) { ; Reduce logging by only saving when not found
            logMessage("[containsText] Searching: " text "  |  Found: " ocrText, 1)
        }

        return textFound > 0
    } catch e {
        logMessage("[containsText] Error searching '" text "': `n" e, 1)
        return -1
    }
}

global biomeData := {"Normal":{duration: 0}
                    ,"Windy":{duration: 120}
                    ,"Rainy":{duration: 120}
                    ,"Snowy":{duration: 120}
                    ,"Hell":{duration: 660}
                    ,"Starfall":{duration: 600}
                    ,"Corruption":{duration: 660}
                    ,"Null":{duration: 90}
                    ,"Glitched":{duration: 164}}

global similarCharacters := {"1":"l"
    ,"n":"m"
    ,"m":"n"
    ,"t":"f"
    ,"f":"t"
    ,"s":"S"
    ,"S":"s"
    ,"w":"W"
    ,"W":"w"}

identifyBiome(inputStr){
    if (!inputStr)
        return 0
    
    internalStr := RegExReplace(inputStr,"\s")
    internalStr := RegExReplace(internalStr,"^([\[\(\{\|IJ]+)")
    internalStr := RegExReplace(internalStr,"([\]\)\}\|IJ]+)$")

    highestRatio := 0
    matchingBiome := ""

    for v,_ in biomeData {
        if (v = "Glitched"){
            continue
        }
        scanIndex := 1
        accuracy := 0
        Loop % StrLen(v) {
            checkingChar := SubStr(v,A_Index,1)
            Loop % StrLen(internalStr) - scanIndex + 1 {
                index := scanIndex + A_Index - 1
                targetChar := SubStr(internalStr, index, 1)
                if (targetChar = checkingChar){
                    accuracy += 3 - A_Index
                    scanIndex := index+1
                    break
                } else if (similarCharacters[targetChar] = checkingChar){
                    accuracy += 2.5 - A_Index
                    scanIndex := index+1
                    break
                }
            }
        }
        ratio := accuracy/(StrLen(v)*2)
        if (ratio > highestRatio){
            matchingBiome := v
            highestRatio := ratio
        }
    }

    if (highestRatio < 0.70){
        matchingBiome := 0
        glitchedCheck := StrLen(internalStr)-StrLen(RegExReplace(internalStr,"\d")) + (RegExMatch(internalStr,"\.") ? 4 : 0)
        if (glitchedCheck >= 20){
            OutputDebug, % "glitched biome pro!"
            matchingBiome := "Glitched"
        }
    }

    return matchingBiome
}

determineBiome(){
    ; logMessage("[determineBiome] Determining biome...")
    if (!WinActive("ahk_id " GetRobloxHWND()) && !WinActive("Roblox")){
        logMessage("[determineBiome] Roblox window not active.")
        return
    }
    getRobloxPos(rX,rY,width,height)

    ; Capture screen area
    pBM := Gdip_BitmapFromScreen(rX "|" rY + height - height*0.102 + ((height/600) - 1)*10 "|" width*0.15 "|" height*0.03)

    effect := Gdip_CreateEffect(3,"2|0|0|0|0" . "|" . "0|1.5|0|0|0" . "|" . "0|0|1|0|0" . "|" . "0|0|0|1|0" . "|" . "0|0|0.2|0|1",0)
    effect2 := Gdip_CreateEffect(5,-100,250)
    effect3 := Gdip_CreateEffect(2,10,50)
    Gdip_BitmapApplyEffect(pBM,effect)
    Gdip_BitmapApplyEffect(pBM,effect2)
    Gdip_BitmapApplyEffect(pBM,effect3)

    identifiedBiome := 0
    resizeCounter := 0
    Loop 10 {
        newSizedPBM := Gdip_ResizeBitmap(pBM,300+(A_Index*38),70+(A_Index*7.5),1,2)
        ocrResult := ocrFromBitmap(newSizedPBM)
        identifiedBiome := identifyBiome(ocrResult)

        Gdip_DisposeBitmap(newSizedPBM)

        if (identifiedBiome){
            resizeCounter := A_Index ; Attempt to determine the optimal resize multiplier
            break
        }
    }
    
    ; Log only if identified
    if (identifiedBiome && identifiedBiome != "Normal") {
        logMessage("[determineBiome] OCR result: " RegExReplace(ocrResult,"(\n|\r)+",""))
        logMessage("[determineBiome] Identified biome: " identifiedBiome " (" resizeCounter " resizes)")
        ToolTip, % "Identified biome: " identifiedBiome " (" resizeCounter " resizes )"
        RemoveTooltip(5)
    }

    Gdip_DisposeEffect(effect)
    Gdip_DisposeEffect(effect2)
    Gdip_DisposeEffect(effect3)
    Gdip_DisposeBitmap(retrievedMap)
    Gdip_DisposeBitmap(pBM)

    DllCall("psapi.dll\EmptyWorkingSet", "ptr", -1)

    return identifiedBiome
}

; Noteab (Windy) Progress
YesConfirmBloxStrap() {
    Sleep, 6500

    WinGet, bloxstrapIDs, List, ahk_exe Bloxstrap.exe

    Loop, %bloxstrapIDs% {
        this_id := bloxstrapIDs%A_Index%
        WinActivate, ahk_id %this_id%
        WinWaitActive, ahk_id %this_id%

        ; Loop for a maximum of 5 seconds (5000 milliseconds) with 500ms intervals
        Loop, 5 { 
            WinGetPos, WinX, WinY, WinWidth, WinHeight, ahk_id %this_id%

            ; Check if dimensions match the warning popup (480x173)
            if (WinWidth = 480 && WinHeight = 173) {
                logMessage("[Bloxstrap] Warning popup found. Attempting to click Yes.")
                closeRoblox()

                yesButtonX := WinX + 300
                yesButtonY := WinY + 140

                MouseMove, %yesButtonX%, %yesButtonY%, 3
                Click

                logMessage("[Bloxstrap] Yes button clicked successfully.")
                Sleep, 4000
                bloxstrapFound := true
                break 2 ; Exit both loops if the button is clicked
            }

            Sleep, 500 ; Wait for 500ms before checking again
        }

        ; If the loop completes without finding the popup, log a message
        if (!bloxstrapFound) {
            logMessage("[Bloxstrap] Window found, but warning popup not detected within the timeout.")
        }
    }
}


; Noteab (Windy) Progress
FindSolsRNGButtons() {
    try {
        Gui, Default

        GuiControlGet, storage_Y_Offset_option, , StorageYOffsetInterval
        if (storage_Y_Offset_option = "")
        {
            storage_Y_Offset_option := Storage_YOffset_Scan 
            logMessage("[FindSolsRNGButton] GuiControlGet failed for StorageYOffsetInterval, using global Storage_YOffset_Scan")
        }

        GuiControlGet, storage_Y_Pos_option, , StorageYPosScanInterval
        if (storage_Y_Pos_option = "")
        {
            storage_Y_Pos_option := Storage_YPos_Scan
            logMessage("[FindSolsRNGButton] GuiControlGet failed for StorageYPosScanInterval, using global Storage_YPos_Scan")
        }

        GuiControlGet, scan_loops_attempt, , ScanLoopAttemptsUpDownInterval
        if (scan_loops_attempt = "")
        {
            scan_loops_attempt := 1
            logMessage("[FindSolsRNGButton] GuiControlGet failed for ScanLoopAttemptsUpDownInterval, using default value 1")
        }
    } catch e {
        logMessage("[FindSolsRNGButton] Error with GuiControlGet: " e.Message)
        storage_Y_Offset_option := Storage_YOffset_Scan
        storage_Y_Pos_option := Storage_YPos_Scan
        scan_loops_attempt := 2
    }

    updateStatus("Scanning button... (Tries: )")
    buttonCoords := []  ; Initialize an empty array to store button coordinates if needed
    global_Button_Found := 0

    ; Get current Roblox window size and client area size
    WinGetPos, , , currentWinWidth, currentWinHeight, ahk_exe RobloxPlayerBeta.exe

    ; Reference resolution (1920x1080)
    refWidth := 1920
    refHeight := 1080

    ; Calculate scaling factors
    scaleX := currentWinWidth / refWidth
    scaleY := currentWinHeight / refHeight

    ; Original dimensions
    origX := 15
    origY := storage_Y_Pos_option
    origW := 52
    origH := 55
    origYOffsetIncrement := storage_Y_Offset_option

    ; Scaled dimensions
    x := origX
    y := Floor(origY * scaleY)
    w := Floor(origW * scaleX)
    h := Floor(origH * scaleY)
    yOffsetIncrement := Floor(origYOffsetIncrement * scaleY)

    ; Pixel color for the button
    buttonPixelColor := 0xFFFFFF

    Loop, %scan_loops_attempt% {  ; Retry loop based on user input
        yOffset := 0   ; Initialize yOffset before each retry
        numButtonsFound := 0 ; Variable to count if found the button pixel and count it

        Loop, 8 { ; Loop through buttons
            buttonIndex := A_Index
            centerX := x + w / 2
            centerY := y + yOffset + h / 2
            MouseMove, %centerX%, %centerY%
            Sleep, 75  ; Delay before getting the pixel color

            ; Scan within the button area for the white pixel color
            ScanArea := { "left": x, "top": y + yOffset, "right": x + w - 1, "bottom": y + yOffset + h - 1 }
            PixelSearch, Px, Py, ScanArea.left, ScanArea.top, ScanArea.right, ScanArea.bottom, buttonPixelColor, 0, Fast

            if !ErrorLevel {
                MouseMove, %Px%, %Py%
                numButtonsFound++ ; Increment the counter
                global_Button_Found := numButtonsFound
            }

            yOffset += yOffsetIncrement  ; Offset y to move to the next button position
            ; Check if reached the bottom of the window
            if (y + yOffset + h > currentWinHeight) {
                break
            }
        }

        updateStatus("Scanning button... (Tries: " A_Index ")")
        logMessage("[FindSolsRNGButton] Attempt " A_Index " completed. Buttons found so far: " numButtonsFound)
        isFirstScan := 1
        Sleep, 1000
    }

    if (global_Button_Found > 0) {  ; If at least one button was found
        logMessage("[FindSolsRNGButton] Total buttons found: " global_Button_Found) ; Log the count 

        if (global_Button_Found == 7) {
            options["InOwnPrivateServer"] := 0
        } else if (global_Button_Found == 8) {
            options["InOwnPrivateServer"] := 1
        }

        return true  ; Exit the function and return true (success)
    }

    logMessage("[FindSolsRNGButton] Could not find Sol's RNG button after " scan_loops_attempt " attempts.")
    return false ; If no buttons are found after the specified number of attempts
}


; Noteab (Windy) Progress
ToggleStorageYPOS_Highlight() {
    GuiControlGet, newStorageYPosScan, , StorageYPosScanInterval
    GuiControlGet, newStorageYOffset, , StorageYOffsetInterval

    ; Get current Roblox window size and client area size
    WinGetPos, , , currentWinWidth, currentWinHeight, ahk_exe RobloxPlayerBeta.exe

    ; Reference resolution (1920x1080)
    refWidth := 1920
    refHeight := 1080

    ; Calculate scaling factors
    scaleX := currentWinWidth / refWidth
    scaleY := currentWinHeight / refHeight

    ; Original dimensions
    origX := 15
    origY := newStorageYPosScan
    origW := 52
    origH := 55
    origYOffsetIncrement := newStorageYOffset

    ; Scaled dimensions
    x := origX  ; X value is fine, no scaling needed for x
    y := Floor(origY * scaleY)
    w := Floor(origW * scaleX)
    h := Floor(origH * scaleY)
    yOffsetIncrement := Floor(origYOffsetIncrement * scaleY)

    ; Highlight the search area for all potential button positions
    Loop, 8 {
        yOffset := (A_Index - 1) * yOffsetIncrement
        if (y + yOffset + h > currentWinHeight) {
            break
        }
        Highlight(x, y + yOffset, w, h, 6000)
    }
}

attemptReconnect(failed := 0){
    ; Set default y position and offset of storage instead since guicontrolget dumped error when reconnecting, gg my macro :broken_heart:
    Storage_YPos_Scan := 318
    Storage_YOffset_Scan := 70 

    logMessage("[attemptReconnect] Reconnect check - Fail count: " failed)
    initialized := 0
    if (reconnecting && !failed){
        return
    }
    if (!options.ReconnectEnabled){
        logMessage("[attemptReconnect] Reconnect not enabled. Stopping...", 1)
        stop()
        return
    }
    reconnecting := 1
    macroStarted := 0
    success := 0

    ; stop(0, 1)
    StopPaths()
    closeRoblox()

    updateStatus("Reconnecting")
    Sleep, 5000
    Loop 5 {
        Sleep, % (A_Index-1)*10000
        try {
           if (options.PrivateServerId && A_Index < 4){
                privateServerURL := "https://www.roblox.com/games/15532962292/Sols-RNG?privateServerLinkCode=" options.PrivateServerId 
                Run, %ComSpec% /c start "" %privateServerURL%
            } 
        } catch e {
            logMessage("[attemptReconnect] Unable to open Private Server. Error: " e.message)
            continue
        }

        Loop 240 {
            rHwnd := GetRobloxHWND()
            if (rHwnd) {
                WinActivate, ahk_id %rHwnd%
                updateStatus("Roblox Opened")
                logMessage("[attemptReconnect] Detected Roblox opened at loop " A_Index, 1)
                break
            }
            if (A_Index == 240) { 
                logMessage("[attemptReconnect] Unable to get Roblox HWND.")
                Sleep, 10000
                continue 2
            }
            Sleep 1000
        }

        Loop 120 {
            getRobloxPos(pX,pY,width,height)

            valid := 0
            if (isPlayButtonVisible()){
                Sleep, 2000
                valid := isPlayButtonVisible()
            }
            
            if (valid){
                ClickPlay()
                break
            }

            if (A_Index == 120 || !GetRobloxHWND()) {
                logMessage("[attemptReconnect] Play button not found or Roblox closed.")
                continue 2
            }
            Sleep 1000
        }

        options.LastRobloxRestart := getUnixTime() ; Reset timer
        updateStatus("Reconnect Complete")
        success := 1
        break
    }

    if (success){
        reconnecting := 0
    } else {
        if (failed < 3) { ; Limit the number of attempts to prevent infinite recursion
            Sleep, 30000
            attemptReconnect(failed + 1)
        } else {
            updateStatus("Reconnect Failed")
            logMessage("[attemptReconnect] Failed to reconnect after multiple attempts.")
            reconnecting := 0
        }
    }
}



checkDisconnect(wasChecked := 0){
    logMessage("[checkDisconnect] Checking for disconnect")
    getRobloxPos(windowX, windowY, windowWidth, windowHeight)

    ; if (options.OCREnabled) {
    if (containsText(890, 425, 135, 25, "Disconnected")) { ; 1025, 450
        logMessage("[checkDisconnect] 'Disconnected' popup found with OCR")
        updateStatus("Roblox Disconnected")
        options.Disconnects += 1
        return 1
    }
        ; return 0 ; Commented out to allow secondary check below
    ; }

    if ((windowWidth > 0) && !WinExist("Roblox Crash")) {
		pBMScreen := Gdip_BitmapFromScreen(windowX+(windowWidth/4) "|" windowY+(windowHeight/2) "|" windowWidth/2 "|1")
        matches := 0
        hW := windowWidth/2
		Loop %hW% {
            matches += (compareColors(Gdip_GetPixelColor(pBMScreen,A_Index-1,0,1),0x393b3d) < 8)
            if (matches >= 128) {
                logMessage("[checkDisconnect] High probability of Disconnect screen found after " A_Index " loops", 1)
                break
            }
        }
        Gdip_DisposeBitmap(pBMScreen)
        if (matches < 128) {
            return 0
        }
	}
    if (wasChecked) {
        updateStatus("Roblox Disconnected")
        options.Disconnects += 1
        return 1
    } else {
        Sleep, 3000
        return checkDisconnect(1)
    }
}

RemoveTooltip(interval) {
    SetTimer, ClearToolTip, % -interval * 1000
}

; Closes all "instance already running" alerts
CloseBSAlerts() {
    WinGet, id, List, Bloxstrap ahk_exe Bloxstrap.exe
    Loop, %id% {
        this_id := id%A_Index%
        PostMessage, 0x0112, 0xF060,,, % "ahk_id" this_id ; 0x0112 = WM_SYSCOMMAND, 0xF060 = SC_CLOSE

        logMessage("[Bloxstrap Alert] Closed popup " this_id, 1)
    }
}

/*
testPath := mainDir "images\test.png"
OutputDebug, testPath
pbm := Gdip_LoadImageFromFile(testPath) ; Gdip_BitmapFromScreen("0|0|100|100")
pbm2 := Gdip_ResizeBitmap(pbm,1500,1500,true)
Gdip_SaveBitmapToFile(pbm2,"test2.png")

MsgBox, % ocrFromBitmap(pbm2)
ExitApp
*/

reconnectTimeout := 60000 ; 60 seconds
mainLoop(){
    Global
    if (reconnecting) { ; TODO: Avoid infinite loop from reconnect error
        Sleep, 1000
        return

        ; Track the start time
        ; startTime := A_TickCount

        ; ; Loop until reconnecting is false or timeout is exceeded
        ; while (!GetRobloxHWND()) {
        ;     Sleep, 15000
        ;     elapsedTime := A_TickCount - startTime
        ;     if (elapsedTime > reconnectTimeout) {
        ;         ; Log an error and take appropriate action
        ;         logMessage("[Error] Reconnect timeout exceeded. Please check the program status.", 1)
        ;         attemptReconnect(1)
        ;         return
        ;     }
        ; }
    }

    currentId := GetRobloxHWND()
    if (!currentId){
        logMessage("[mainLoop] Roblox not found. Attempting to reconnect.")
        attemptReconnect()
        return
    } else if (currentId != robloxId){
        logMessage("[mainLoop] New Roblox window found. Switching..")
        OutputDebug, "Window switched"
        robloxId := currentId
    }

    if (checkDisconnect()){
        logMessage("[mainLoop] Roblox disconnected. Attempting to reconnect.")
        attemptReconnect()
        return
    }

    ; Restart Roblox to clear RAM
    if (options.RestartRobloxEnabled && getUnixTime()-options.LastRobloxRestart >= (options.RestartRobloxInterval*60*60)) {
        if (ClearRAM()) {
            return
        }
    }

    WinActivate, ahk_id %robloxId%

    ; Checks to avoid idling
    ;CloseBSAlerts() ; Prevent infinite Bloxstrap error popups

    if (isPlayButtonVisible()) {
        ClickPlay()
    }

    enableAutoRoll() ; Check after ClickPlay to make sure not left off due to lag, etc

    if (!isFirstScan){
        FindSolsRNGButtons()
    }

    if (!initialized){
        updateStatus("Initializing")
        initialize()
    }

    mouseActions()

    Sleep, 250

    ; Reset to spawn before taking screenshots or using items
    ; reset()
    
    ; Attempt to claim quests every 30 minutes

    if (options.AutoClaimQuestEnabled && !lastClaim || A_TickCount - lastClaim > 1800000) {
        ClaimQuests()
        lastClaim := A_TickCount
    }
   
    ; Take Screenshots - Aura Storage, Item Inventory, Quests
    if (options.InvScreenshotsEnabled && getUnixTime()-options.LastInvScreenshot >= (options.ScreenshotInterval*60)) {
        options.LastInvScreenshot := getUnixTime()
        screenshotInventories()
    }

    Sleep, 250

    ; Run Item Scheduler entries
    currentUnixTime := getUnixTime()
    for each, entry in ItemSchedulerEntries {
        if (entry.Enabled && currentUnixTime >= entry.NextRunTime) {
            ; Use specified number of item
            UseItem(entry.ItemName, entry.Quantity)

            ; Update the NextRunTime for the next scheduled run
            frequencyInSeconds := entry.Frequency * (entry.TimeUnit = "Minutes" ? 60 : 3600)
            nextRunTime := currentUnixTime + frequencyInSeconds
            ; FormatTime, t, nextRunTime, "hh:mm:ss tt"
            ; logMessage("[Scheduler] " entry.ItemName " next run: " t " (" frequencyInSeconds " seconds)", 1)

            entry.NextRunTime := nextRunTime
        }
    }

    Sleep, 250

    if (options.PotionCraftingEnabled || options.ItemCraftingEnabled){
        if (getUnixTime()-options.LastCraftSession >= (options.CraftingInterval*60)) {
            options.LastCraftSession := getUnixTime()
            handleCrafting()
        }
    }
    
    if (options.DoingObby && (A_TickCount - lastObby) >= (obbyCooldown*1000)){
        align()
        obbyRun()

        ; MouseGetPos, mouseX, mouseY
        local TLCornerX, TLCornerY, width, height
        getRobloxPos(TLCornerX, TLCornerY, width, height)
        BRCornerX := TLCornerX + width
        BRCornerY := TLCornerY + height
        statusEffectHeight := Floor((height/1080)*54)

        hasBuff := checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
        Sleep, 1000
        hasBuff := hasBuff || checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
        if (!hasBuff){
            Sleep, 5000
            hasBuff := hasBuff || checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
        }
        if (!hasBuff)
        {
            align()
            updateStatus("Obby Failed, Retrying")
            lastObby := A_TickCount - obbyCooldown*1000
            obbyRun()
            hasBuff := checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
            Sleep, 1000
            hasBuff := hasBuff || checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
            if (!hasBuff){
                Sleep, 5000
                hasBuff := hasBuff || checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
            }
            if (!hasBuff){
                lastObby := A_TickCount - obbyCooldown*1000
            }
        }
    }

    if (options.CollectItems){
        reset()
        Sleep, 2000
        searchForItems()
    }

    /*
    ;MouseMove, targetX, targetY
    Gui test1:Color, %color%
    GuiControl,,TestT,% checkHasObbyBuff(BRCornerX,BRCornerY,statusEffectHeight)
    */
}

; Used to detect current biome - Copied from status.ahk 
biomeLoop(){ ; originally secondTick() - renamed due to conflict with existing function
    if (!options.OCREnabled) {
        return
    }

    detectedBiome := determineBiome()

    if (detectedBiome && biomeData[detectedBiome] && detectedBiome != "Normal"){
        ; If it's the same, we may be checking a little too early so don't wait the full duration again
        if (detectedBiome = currentBiome) {
            SetTimer, biomeLoop, -2000
            return
        }

        currentBiome := detectedBiome

        changeBiome()

        targetData := biomeData[currentBiome]
        SetTimer, biomeLoop, % -(targetData.duration+5) * 1000
    } else {
        SetTimer, biomeLoop, -2000
    }
}
; biomeLoop()

CreateMainUI() {
    global

; main ui
    try {
        Menu Tray, Icon, % mainDir "images\dSM.ico" ; Use icon if available
    } catch {
        Menu Tray, Icon, shell32.dll, 3
    }

    Gui mainUI: New, +hWndhGui
    Gui Color, 0xDADADA
    Gui Add, Button, gStartClick vStartButton x8 y224 w80 h23 -Tabstop, F1 - Start
    Gui Add, Button, gPauseClick vPauseButton x96 y224 w80 h23 -Tabstop, F2 - Pause
    Gui Add, Button, gStopClick vStopButton x184 y224 w80 h23 -Tabstop, F3 - Stop
    Gui Font, s11 Norm, Segoe UI
    Gui Add, Picture, gDiscordServerClick w26 h20 x462 y226, % mainDir "images\discordIcon.png"

    Gui Add, Tab3, vMainTabs x8 y8 w484 h210 +0x800000, Main|Crafting|Status|Settings|Credits|Extras

; main tab
    Gui Tab, 1

    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y40 w231 h70 vObbyOptionGroup -Theme +0x50000007, Obby
    Gui Font, s9 norm
    Gui Add, CheckBox, vObbyCheckBox x32 y59 w180 h26 +0x2, % " Do Obby (Every 2 Mins)"
    Gui Add, CheckBox, vObbyBuffCheckBox x32 y80 w200 h26 +0x2, % " Check for Obby Buff Effect"
    Gui Add, Button, gObbyHelpClick vObbyHelpButton x221 y50 w23 h23, ?

    Gui Font, s10 w600
    Gui Add, GroupBox, x252 y40 w231 h70 vAutoEquipGroup -Theme +0x50000007, Auto Equip
    Gui Font, s9 norm
    Gui Add, CheckBox, vAutoEquipCheckBox x268 y61 w190 h22 +0x2, % " Enable Auto Equip"
    Gui Add, Button, gAutoEquipSlotSelectClick vAutoEquipSlotSelectButton x268 y83 w115 h22, Select Storage Slot
    Gui Add, Button, gAutoEquipHelpClick vAutoEquipHelpButton x457 y50 w23 h23, ?

    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y110 w467 h100 vCollectOptionGroup -Theme +0x50000007, Item Collecting
    Gui Font, s9 norm
    Gui Add, CheckBox, vCollectCheckBox x32 y129 w261 h26 +0x2, % " Collect Items Around the Map"
    Gui Add, Button, gCollectHelpClick vCollectHelpButton x457 y120 w23 h23, ?

    Gui Add, GroupBox, x26 y155 w447 h48 vCollectSpotsHolder -Theme +0x50000007, Collect From Spots
    Gui Add, CheckBox, vCollectSpot1CheckBox x42 y174 w30 h26 +0x2 -Tabstop, % " 1"
    Gui Add, CheckBox, vCollectSpot2CheckBox x82 y174 w30 h26 +0x2 -Tabstop, % " 2"
    Gui Add, CheckBox, vCollectSpot3CheckBox x122 y174 w30 h26 +0x2 -Tabstop, % " 3"
    Gui Add, CheckBox, vCollectSpot4CheckBox x162 y174 w30 h26 +0x2 -Tabstop, % " 4"
    Gui Add, CheckBox, vCollectSpot5CheckBox x202 y174 w30 h26 +0x2 -Tabstop, % " 5"
    Gui Add, CheckBox, vCollectSpot6CheckBox x242 y174 w30 h26 +0x2 -Tabstop, % " 6"
    Gui Add, CheckBox, vCollectSpot7CheckBox x282 y174 w30 h26 +0x2 -Tabstop, % " 7"

; crafting tab
    Gui Tab, 2
    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y40 w231 h110 vItemCraftingGroup -Theme +0x50000007, Item Crafting
    Gui Font, s9 norm
    Gui Add, CheckBox, vItemCraftingCheckBox x32 y58 w190 h22 +Disabled, % " Automatic Item Crafting"
    Gui Font, s9 w600
    Gui Add, GroupBox, x21 y80 w221 h65 vItemCraftingOptionsGroup -Theme +0x50000007, Crafting Options

    ; Potion Crafting Settings
    potionSlotOptions := "None||Fortune Potion I|Fortune Potion II|Fortune Potion III|Haste Potion I|Haste Potion II|Haste Potion III|Heavenly Potion I|Heavenly Potion II"
    Gui Font, s10 w600
    Gui Add, GroupBox, x252 y40 w231 h170 vPotionCraftingGroup -Theme +0x50000007, Potion Crafting
    Gui Font, s9 norm
    Gui Add, CheckBox, vPotionCraftingCheckBox x268 y58 w200 h22 +0x2, % " Automatic Potion Crafting"
    Gui Add, CheckBox, vPotionAutoAddCheckBox x268 y78 w200 h22 +0x2, % " Use Auto Add (Cycles Slots)"
    
    ; Potion Crafting Slots
    Gui Font, s9 w600
    Gui Add, GroupBox, x257 y100 w221 h105 vPotionCraftingSlotsGroup -Theme +0x50000007, Crafting Slots
    Gui Font, s9 norm
    Gui Add, Text, x270 y122 w100 h16 vItemCraftingSlot1Header BackgroundTrans, Slot 1:
    Gui Add, DropDownList, x312 y118 w120 h10 vPotionCraftingSlot1DropDown R9, % potionSlotOptions
    Gui Add, Text, x270 y152 w100 h16 vItemCraftingSlot2Header BackgroundTrans, Slot 2:
    Gui Add, DropDownList, x312 y148 w120 h10 vPotionCraftingSlot2DropDown R9, % potionSlotOptions
    Gui Add, Text, x270 y182 w100 h16 vItemCraftingSlot3Header BackgroundTrans, Slot 3:
    Gui Add, DropDownList, x312 y178 w120 h10 vPotionCraftingSlot3DropDown R9, % potionSlotOptions

    ; Crafting Interval
    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y150 w231 h60 vCraftingIntervalGroup -Theme +0x50000007, Crafting Intervals
    Gui Font, s9 norm

    Gui Add, Text, x32 y170 h35 vCraftingIntervalText BackgroundTrans Section, Craft every
    Gui Add, Edit, ys wp w45 h18 vCraftingIntervalInput Number, 10
    Gui Add, UpDown, vCraftingIntervalUpDown Range1-300, 10
    Gui Add, Text, ys wp w60 h35 BackgroundTrans, minutes

    Gui Add, Text, x32 y190 h35 vPotionAutoAddIntervalText BackgroundTrans Section, Auto Add every
    Gui Add, Edit, ys wp w45 h18 vPotionAutoAddIntervalInput Number, 10
    Gui Add, UpDown, vPotionAutoAddIntervalUpDown Range1-300, 10
    Gui Add, Text, ys wp w60 h35 BackgroundTrans, minutes

; status tab
    Gui Tab, 3
    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y40 w130 h170 vStatsGroup -Theme +0x50000007, Stats
    Gui Font, s8 norm
    Gui Add, Text, vStatsDisplay x22 y58 w118 h146, runtime: 123`ndisconnects: 1000

    Gui Font, s10 w600
    Gui Add, GroupBox, x151 y40 w200 h170 vWebhookGroup -Theme +0x50000007, Discord Webhook
    Gui Font, s7.5 norm
    Gui Add, CheckBox, vWebhookCheckBox x166 y63 w120 h16 +0x2 gEnableWebhookToggle, % " Enable Webhook"
    Gui Add, Text, x161 y85 w100 h20 vWebhookInputHeader BackgroundTrans, Webhook URL:
    Gui Add, Edit, x166 y103 w169 h18 vWebhookInput,% ""
    Gui Add, Button, gWebhookHelpClick vWebhookHelpButton x325 y50 w23 h23, ?
    Gui Add, CheckBox, vWebhookImportantOnlyCheckBox x166 y126 w140 h16 +0x2, % " Important events only"
    Gui Add, Text, vWebhookUserIDHeader x161 y145 w150 h14 BackgroundTrans, % "Discord User ID (Pings):"
    Gui Add, Edit, x166 y162 w169 h16 vWebhookUserIDInput,% ""
    Gui Font, s7.4 norm
    Gui Add, CheckBox, vWebhookInventoryScreenshots x161 y182 w130 h26 +0x2, % "Inventory Screenshots (mins)"
    Gui Add, Edit, x294 y186 w50 h18
    Gui Add, UpDown, vInvScreenshotinterval Range1-1440

    Gui Font, s10 w600
    Gui Add, GroupBox, x356 y40 w127 h50 vStatusOtherGroup -Theme +0x50000007, Other
    Gui Font, s9 norm
    Gui Add, CheckBox, vStatusBarCheckBox x366 y63 w110 h20 +0x2, % " Enable Status Bar"

    Gui Font, s9 w600
    Gui Add, GroupBox, x356 y90 w127 h120 vRollDetectionGroup -Theme +0x50000007, Roll Detection
    Gui Font, s8 norm
    Gui Add, Button, gRollDetectionHelpClick vRollDetectionHelpButton x457 y99 w23 h23, ?
    Gui Add, Text, vWebhookRollSendHeader x365 y110 w110 h16 BackgroundTrans, % "Send Minimum:"
    Gui Add, Edit, vWebhookRollSendInput x370 y126 w102 h18, 10000
    Gui Add, Text, vWebhookRollPingHeader x365 y146 w110 h16 BackgroundTrans, % "Ping Minimum:"
    Gui Add, Edit, vWebhookRollPingInput x370 y162 w102 h18, 100000
    Gui Add, CheckBox, vWebhookRollImageCheckBox gWebhookRollImageCheckBoxClick x365 y183 w90 h18, Aura Images
    Gui Add, Picture, gShowAuraSettings vShowAuraSettingsIcon x458 y183 w20 h20, % mainDir "images\settingsIcon.png"

    ; Assign the g-label to the icon/button to show the Aura settings popup
    GuiControl, +gShowAuraSettings, vShowAuraSettingsIcon

; settings tab
    Gui Tab, 4
    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y40 w258 h170 vGeneralSettingsGroup -Theme +0x50000007, General
    Gui Font, s9 norm
    Gui Add, CheckBox, vVIPCheckBox x32 y58 w150 h22 +0x2, % " VIP Gamepass Owned"
    Gui Add, CheckBox, vAzertyCheckBox x32 y78 w200 h22 +0x2, % " AZERTY Keyboard Layout"
    Gui Add, Text, x32 y101 w200 h22, % "Collection Back Button Y Offset:"
    Gui Add, Edit, x206 y100 w50 h18
    Gui Add, UpDown, vBackOffsetUpDown Range-500-500, 0

    Gui Font, s10 w600
    Gui Add, GroupBox, x280 y40 w203 h138 vReconnectSettingsGroup -Theme +0x50000007, Reconnect
    Gui Font, s9 norm

    ; Enable Reconnect
    Gui Add, CheckBox, x296 y61 w150 h16 +0x2 vReconnectCheckBox Section, % "Enable Reconnect"

    ; Restart Roblox
    Gui Add, CheckBox, x296 y81 h16 +0x2 vRestartRobloxCheckBox Section, Restart Roblox every
    Gui Add, Edit, x296 y101 w45 h18 vRestartRobloxIntervalInput Number, 1
    Gui Add, UpDown, vRestartRobloxIntervalUpDown Range1-24, 1
    Gui Add, Text, x350 y102 w130 h16 BackgroundTrans, % "hour(s) (Clears RAM)"

    ; Private Server Link
    Gui Add, Text, x290 y131 w100 h20 vPrivateServerInputHeader BackgroundTrans, Private Server Link:
    Gui Add, Edit, x294 y148 w177 h20 vPrivateServerInput, % ""

    ; Import 
    Gui Add, Button, vImportSettingsButton gImportSettingsClick x317 y186 w130 h20, Import Settings

    ; Migrate from my last improvement macro UI section:
    ; Scan Button Loop

    ; Scan Loop Interval Input and Storage Y Pos Setting:
    Gui Add, Text, x32 y122 w120 h15, Scan Loops attempts:
    Gui Add, Edit, vScanLoopAttempts x150 y122 w45 h18 Number, 1 ; Default to 1 attempt
    Gui Add, UpDown, Range1-10 vScanLoopAttemptsUpDownInterval, 1  ; Allow 1 to 10 attempts

    Gui Add, Text, x32 y143 w120 h15, Storage Y Position:
    Gui Add, Edit, vStorageYPosScan x150 y143 w45 h18 Number, 1
    Gui Add, UpDown, Range100-1000 vStorageYPosScanInterval, 1 ; Storage Y Position number input

    ; Storage Y Offset UI
    Gui Add, Text, x32 y164 w120 h15, Storage Y Offset:
    Gui Add, Edit, vStorageYOffset x150 y164 w45 h18 Number, 1
    Gui Add, UpDown, Range1-400 vStorageYOffsetInterval, 1 ; Storage Y Offset number input

    ; Show Storage Aligning Pos and Offset:
    Gui Add, Button, gToggleStorageYPOS_Highlight vStorageYPosHighlightButton x197 y131 w65 h45 +0x2, Highlight

    ; ClaimQuest() toggle checkbox: - Noteab
    Gui Add, CheckBox, vAutoClaimQuestCheckBox x32 y183 w200 h22 +0x2, % " Auto Claim Daily Quest?"
; credits tab
    Gui Tab, 5
    Gui Font, s10 w600
    Gui Add, GroupBox, x16 y40 w231 h133 vCreditsGroup -Theme +0x50000007, The Creator
    Gui Add, Picture, w75 h75 x23 y62, % mainDir "images\pfp.png"
    Gui Font, s12 w600
    Gui Add, Text, x110 y57 w130 h22,BuilderDolphin
    Gui Font, s8 norm italic
    Gui Add, Text, x120 y78 w80 h18,(dolphin)
    Gui Font, s8 norm
    Gui Add, Text, x115 y95 w124 h40,"This was supposed to be a short project to learn AHK..."
    Gui Font, s8 norm
    Gui Add, Text, x28 y145 w200 h32 BackgroundTrans,% "More to come soon perhaps..."
    Gui Add, Button, x28 y177 w206 h32 gMoreCreditsClick,% "More Credits"

    Gui Font, s10 w600
    Gui Add, GroupBox, x252 y40 w231 h90 vCreditsGroup2 -Theme +0x50000007, The Inspiration
    Gui Add, Picture, w60 h60 x259 y62, % mainDir "images\auryn.ico"
    Gui Font, s8 norm
    Gui Add, Text, x326 y59 w150 h68,% "Natro Macro, a macro for Bee Swarm Simulator has greatly inspired this project and has helped me create this project overall."

    Gui Font, s10 w600
    Gui Add, GroupBox, x252 y130 w231 h80 vCreditsGroup3 -Theme +0x50000007, Other
    Gui Font, s9 norm
    Gui Add, Link, x268 y150 w200 h55, Join the <a href="https://discord.gg/DYUqwJchuV">Discord Server</a>! (Community)`n`nVisit the <a href="https://github.com/BuilderDolphin/dolphSol-Macro">GitHub</a>! (Updates + Versions)

; extras tab
    Gui Tab, 6
    Gui Font, s10 w600

    ; General
    Gui Add, GroupBox, x16 y40 w467 h50 vGeneralEnhancementsGroup -Theme +0x50000007, General
    Gui Font, s9 norm
    Gui Add, CheckBox, gOCREnabledCheckBoxClick vOCREnabledCheckBox x32 y60 w400 h22 +0x2 Section, % " Enable OCR for Self-Correction (Requires English-US PC Language)"
    Gui Add, Button, gOCRHelpClick vOCRHelpButton x457 y50 w23 h23, ?

    Gui Add, Button, gShowBiomeSettings vBiomeButton x16 y100 w128, Configure Biomes
    Gui Add, Button, gShowItemSchedulerSettings vSchedulerGUIButton x16 y+5 w128, Item Scheduler
    
    ; Roblox UI style to determine Chat button position
    Gui Font, s10 w600
    Gui Add, Text, x400 y130, Roblox UI
    Gui Font, s9 norm
    
    ; options["RobloxUpdatedUI"]
    Gui Add, Radio, AltSubmit gGetRobloxVersion vRobloxUpdatedUIRadio1 x420 y150, Old
    Gui Add, Radio, AltSubmit gGetRobloxVersion vRobloxUpdatedUIRadio2, New
    GuiControl,, RobloxUpdatedUIRadio1, % (options["RobloxUpdatedUI"] = 1) ? 1 : 0
    GuiControl,, RobloxUpdatedUIRadio2, % (options["RobloxUpdatedUI"] = 2) ? 1 : 0
    
    Gui Show, % "w500 h254 x" clamp(options.WindowX,10,A_ScreenWidth-100) " y" clamp(options.WindowY,10,A_ScreenHeight-100), % "dolphSol Macro " version

    ; status bar
    Gui statusBar:New, +AlwaysOnTop -Caption
    Gui Font, s10 norm
    Gui Add, Text, x5 y5 w210 h15 vStatusBarText, Status: Waiting...

    Gui mainUI:Default
}
CreateMainUI()

; Create the Aura settings popup
ShowAuraSettings() {
    global ; Needed for GUI variables
    Gui, AuraSettings:New, +AlwaysOnTop +LabelAuraGui
    Gui Font, s10 w600
    Gui Add, Text, x16 y10 w300 h30, Aura Webhook Toggles
    Gui Font, s9 norm
    Gui Add, Text, x16 y30 w300 h30, Uncheck to disable Discord notification

    ; Calculate the number of items per column
    itemsPerColumn := Ceil(auraNames.Length() / 2.0)

    ; Initialize position variables
    local startXPos := 16
    local startYPos := 50
    local xPos := startXPos
    local yPos := startYPos
    local columnCounter := 0
    local columnWidth := 240

    ; Create checkboxes for each aura
    for index, auraName in auraNames {
        ; Convert the aura name to a valid variable name
        sAuraName := RegExReplace(auraName, "[^a-zA-Z0-9]+", "_") ; Replace with underscore
        sAuraName := RegExReplace(sAuraName, "\_$", "") ; Remove any trailing underscore

        try {
            ; outputDebug, % "Adding checkbox for " auraName " (" sAuraName ") at x" xPos ", y" yPos
            Gui Add, CheckBox, % "v" sAuraName "CheckBox x" xPos " y" yPos " w220 h20 +0x2 Checked"options["wh" . sAuraName], % auraName
        } catch e {
            logMessage("[ShowAuraSettings] Error adding checkbox for " auraName "(" sAuraName ") : " e.Message)
        }
        yPos += 25
        columnCounter += 1

        ; Adjust if more than one column is needed
        if (columnCounter >= itemsPerColumn) {
            columnCounter := 0
            xPos += columnWidth  ; Move to the next column
            yPos := startYPos
        }
    }
    Gui Show, % "w500", Aura Settings
}

applyAuraSettings() {
    global auraNames, options

    Gui AuraSettings:Default  ; Ensure we are in the context of AuraSettings GUI

    ; Save aura settings with prefix
    for index, auraName in auraNames {
        sAuraName := RegExReplace(auraName, "[^a-zA-Z0-9]+", "_") ; Replace all non-alphanumeric characters with underscore
        sAuraName := RegExReplace(sAuraName, "\_$", "") ; Remove any trailing underscore
        
        GuiControlGet, rValue,, %sAuraName%CheckBox
        options["wh" . sAuraName] := rValue
        ; logMessage("[applyAuraSettings] Updating Aura Setting: " auraName " - " sAuraName " - " options["wh" . sAuraName])
    }
}

; Create the Biome settings popup
ShowBiomeSettings() {
    global ; Needed for GUI variables
    Gui, BiomeSettings:New, +AlwaysOnTop +LabelBiomeGui
    Gui Color, 0xDADADA
    Gui Font, s10 w600
    Gui Add, Text, x16 y10 w300 h30, Biome Alerts
    Gui Font, s9 norm
    Gui Add, Text, x16 y30 w300 h30, % "Message = Discord Message`n       Ping = Message + Ping User/Role"

    col := 1
    colW := 40 ; Spacing between name and dropdown (Biome in first column are mostly shorter)
    yPos := 75

    For i, biome in biomes {
        if (i = 5) {
            ; Start a new column
            col := 2
            colW := 60
            yPos := 75
        }

        xPos := (col = 1) ? 16 : 175

        Gui Add, Text, Section x%xPos% y%yPos% w%colW% h20, % biome ":"
        Gui Add, DropDownList, % "x+m ys-2 w80 h20 R3 v" biome "DropDown", None||Message|Ping
        GuiControl, ChooseString, %biome%DropDown, % options["Biome" . biome]

        yPos += 25
    }

    Gui Show, , Biome Settings
}

applyBiomeSettings() {
    global biomes, options

    Gui BiomeSettings:Default  ; Ensure we are in the context of the correct GUI

    ; Save settings with prefix
    for index, biome in biomes {
        GuiControlGet, rValue,, %biome%DropDown
        options["Biome" . biome] := rValue
        ; logMessage("[applyBiomeSettings] Updating Biome Setting: " biome " - " options["Biome" . biome])
    }
}

/*
    Start Item Scheduler Section
*/
; Create the Item Scheduler settings popup
ShowItemSchedulerSettings() {
    global

    Gui ItemSchedulerSettings:New, +AlwaysOnTop +LabelItemSchedulerGui
    ; Gui Font, s10 w600
    ; Gui Add, Text, x16 y10 w300 h30, Auto Item Scheduler
    Gui Font, s9 norm

    ; Initialize position variables
    startXPos := 16
    startYPos := 10
    xPos := startXPos
    yPos := startYPos

    ; Add button to add new entry and Highlight Coordinates
    Gui Add, Button, x%xPos% y%yPos% w100 h25 gAddNewItemEntry vAddNewItemEntryButton, New Entry
    Gui Add, Button, x+50 wp w150 h25 gHighlightItemCoordinates vHighlightItemCoordinatesButton, Show Inventory Clicks
    yPos += 30

    ; Create headers
    Gui Add, Text, x%xPos% y%yPos% Section w50 h20, Enable
    Gui Add, Text, x+30 yp w100 h20, Item
    Gui Add, Text, x+-25 yp w50 h20, Quantity
    Gui Add, Text, x+20 yp w50 h20, Frequency
    yPos += 20

    ; Create entries for each item usage configuration
    xPos := 20
    for index, entry in ItemSchedulerEntries {
        ; OutputDebug, % "# Entries: " ItemSchedulerEntries.Length()
        if (!entry) {
            ; OutputDebug, % "*Item " index ": " entry.ItemName
            break
        }
        ; OutputDebug, % "Item " index ": " entry.ItemName
        AddItemEntry(index, entry, xPos, yPos)
        yPos += 30
    }

    Gui Show, % "w430 h400", Auto Item Scheduler
}

; Function to add item entry to GUI
AddItemEntry(idx, entry, xPos, yPos) {
    global

    OutputDebug, % "Adding entry " idx " at yPos " yPos

    ; Concatenate item names for the dropdown list
    UsableItems := ["Merchant Teleport", "Strange Controller", "Biome Randomizer", "Lucky", "Speed", "Fortune Potion I", "Fortune Potion II", "Fortune Potion III", "Haste Potion I", "Haste Potion II", "Haste Potion III", "Heavenly Potion I", "Heavenly Potion II"]
    itemList := "|"
    for each, item in UsableItems {
        itemList .= item "|"
    }

    ; Add controls for the entry
    Gui Add, CheckBox, % "vEnable" idx "CheckBox Section x" xPos " y" yPos " w30 h20 Checked" entry.Enabled, % idx
    Gui Add, DropDownList, vItem%idx%DropDown x+ yp w115 h20 R10, % itemList
    GuiControl, ChooseString, Item%idx%DropDown, % entry.ItemName
    Gui Add, Edit, vQuantity%idx%Edit x+5 yp wp+10 w40 h20 Number, % entry.Quantity
    Gui Add, Edit, vFrequency%idx%Edit x+5 yp w30 h20 Number, % entry.Frequency
    Gui Add, DropDownList, vTimeUnit%idx%DropDown x+ yp w80 h20 R2, Minutes||Hours
    Gui Add, Button, gDeleteItemEntry vDelete%idx% x+m yp w80 h20, Delete
}

; Function to add a new empty item entry
AddNewItemEntry() {
    ; Calculate yPos based on non-deleted entries
    yPos := 60
    for each, entry in ItemSchedulerEntries {
        if (!entry.Deleted) {
            yPos += 30
        }
    }

    entry := {Enabled: 1
        , ItemName: ""
        , Quantity: 1
        , Frequency: 1
        , TimeUnit: "Minutes"}
    
    idx := ItemSchedulerEntries.Length() + 1
    AddItemEntry(idx, entry, 20, yPos)
    ItemSchedulerEntries.Push(entry)
}

; Function to save item settings
SaveItemSchedulerSettings() {
    global configPath, options, ItemSchedulerEntries

    ; Clear current entries
    ItemSchedulerEntries := []

    ; Flush entries from options to avoid leaving deleted entries
    for i, v in options {
        if (InStr(i, "ISEntry", 1) = 1) {
            options.Delete(i)
        }
    }

    ; Save each entry's settings
    Gui, ItemSchedulerSettings:Default
    idx := 1
    Loop {
        ; OutputDebug, % "Saving index " idx

        GuiControlGet, visible, Visible, Enable%idx%CheckBox
        if (ErrorLevel) {
            break
        }

        if (!visible) { ; Skip "deleted" entries - AHK v1 has no way to delete controls so they are hidden instead
            idx++
            continue
        }

        ; Retrieve values from the controls
        GuiControlGet, enabled,, Enable%idx%CheckBox
        GuiControlGet, itemName,, Item%idx%DropDown
        GuiControlGet, quantity,, Quantity%idx%Edit
        GuiControlGet, frequency,, Frequency%idx%Edit
        GuiControlGet, timeUnit,, TimeUnit%idx%DropDown

        ; OutputDebug, % "  Item: " itemName
        ; OutputDebug, % "  Enabled: " enabled
        ; OutputDebug, % "  Quantity: " quantity
        ; OutputDebug, % "  Frequency: " frequency
        ; OutputDebug, % "  Min/Hr: " timeUnit

        entry := {Enabled: enabled
            , ItemName: itemName
            , Quantity: quantity
            , Frequency: frequency
            , TimeUnit: timeUnit}

        ; Add the entry to the ItemSchedulerEntries array
        ItemSchedulerEntries.Push(entry)

        idx++
    }

    ; Save settings to global options
    for i, entry in ItemSchedulerEntries {
        options["ISEntry" i] := entry.Enabled "," entry.ItemName "," entry.Quantity "," entry.Frequency "," entry.TimeUnit
    }
}

; Function to delete an item entry
DeleteItemEntry() {
    Gui, ItemSchedulerSettings:Default

    ; Extract the index from the control's variable name
    RegExMatch(A_GuiControl, "\d+", idx)

    ; Mark the entry as deleted (keeps the array length consistent)
    ItemSchedulerEntries[idx].Deleted := true

    ; Hide the controls associated with the entry
    GuiControl, Hide, Enable%idx%CheckBox
    GuiControl, Hide, Item%idx%DropDown
    GuiControl, Hide, Quantity%idx%Edit
    GuiControl, Hide, Frequency%idx%Edit
    GuiControl, Hide, TimeUnit%idx%DropDown
    GuiControl, Hide, Delete%idx%

    ; Reposition remaining controls
    yPos := 60
    for i, entry in ItemSchedulerEntries {
        if (!entry.Deleted) {
            ; Update the position of visible controls
            GuiControl, Move, Enable%i%CheckBox, y%yPos%
            GuiControl, Move, Item%i%DropDown, y%yPos%
            GuiControl, Move, Quantity%i%Edit, y%yPos%
            GuiControl, Move, Frequency%i%Edit, y%yPos%
            GuiControl, Move, TimeUnit%i%DropDown, y%yPos%
            GuiControl, Move, Delete%i%, y%yPos%

            ; Force redraw to ensure no blurriness or overlap
            GuiControl, MoveDraw, Enable%i%CheckBox
            GuiControl, MoveDraw, Item%i%DropDown
            GuiControl, MoveDraw, Quantity%i%Edit
            GuiControl, MoveDraw, Frequency%i%Edit
            GuiControl, MoveDraw, TimeUnit%i%DropDown
            GuiControl, MoveDraw, Delete%i%
            yPos += 30
        }
    }
}

LoadItemSchedulerOptions() {
    global configPath, ItemSchedulerEntries

    savedRetrieve := getINIData(configPath)
    if (!savedRetrieve) {
        logMessage("[LoadItemSchedulerOptions] Unable to read config.ini")
        return
    }

    ItemSchedulerEntries := []
    for i, v in savedRetrieve {
        if (InStr(i, "ISEntry", 1) = 1) {
            parts := StrSplit(v, ",")
            entry := {Enabled: parts[1], ItemName: parts[2], Quantity: parts[3], Frequency: parts[4], TimeUnit: parts[5]}
            entry.NextRunTime := getUnixTime() ; Run once on load. TODO: Add option to menu entries

            if (entry.ItemName = "") {
                continue
            }
            ItemSchedulerEntries.Push(entry)
        }
    }

    ; Add entries to options - Handled in Save function which is only called when Scheduler is closed
    for i, entry in ItemSchedulerEntries {
        options["ISEntry" i] := entry.Enabled "," entry.ItemName "," entry.Quantity "," entry.Frequency "," entry.TimeUnit
    }
}

; Function to highlight coordinates
HighlightItemCoordinates() {
    ; Highlight where mouse will click to automatically use items
    ; For user to test accuracy

    ; 850, 330 Search box
    Highlight(850-5, 330-5, 10, 10, 5000)

    ; 860, 400 1st search result
    Highlight(860-5, 400-5, 10, 10, 5000)

    ; 590, 600 Quantity box
    Highlight(590-5, 600-5, 10, 10, 5000)

    ; 700, 600 Use button
    Highlight(700-5, 600-5, 10, 10, 5000)
}
/*
    End Item Scheduler Section
*/

global directValues := {"ObbyCheckBox":"DoingObby"
    ,"AzertyCheckBox":"AzertyLayout"
    ,"ObbyBuffCheckBox":"CheckObbyBuff"
    ,"CollectCheckBox":"CollectItems"
    ,"VIPCheckBox":"VIP"
    ,"BackOffsetUpDown":"BackOffset"
    ,"AutoEquipCheckBox":"AutoEquipEnabled"
    ,"CraftingIntervalUpDown":"CraftingInterval"
    ,"ItemCraftingCheckBox":"ItemCraftingEnabled"
    ,"InvScreenshotinterval":"ScreenshotInterval"
    ,"PotionCraftingCheckBox":"PotionCraftingEnabled"
    ,"PotionAutoAddCheckBox":"PotionAutoAddEnabled"          ; Amraki
    ,"PotionAutoAddIntervalUpDown":"PotionAutoAddInterval"   ; Amraki
    ,"ReconnectCheckBox":"ReconnectEnabled"
    ,"RestartRobloxCheckBox":"RestartRobloxEnabled"          ; Amraki
    ,"RestartRobloxIntervalUpDown":"RestartRobloxInterval"   ; Amraki
    ,"WebhookCheckBox":"WebhookEnabled"
    ,"WebhookInput":"WebhookLink"
    ,"WebhookImportantOnlyCheckBox":"WebhookImportantOnly"
    ,"WebhookRollImageCheckBox":"WebhookAuraRollImages"
    ,"WebhookUserIDInput":"DiscordUserID"
    ,"WebhookInventoryScreenshots":"InvScreenshotsEnabled"
    ,"StatusBarCheckBox":"StatusBarEnabled"
    ,"OCREnabledCheckBox":"OCREnabled" ; Amraki
    ,"ScanLoopAttemptsUpDownInterval": "ScanLoopInterval" ; Noteab
    ,"StorageYPosScanInterval":"StorageButtonYPosScanVALUE" ; Noteab
    ,"StorageYOffsetInterval": "StorageYOffsetIntervalVALUE"
    ,"AutoClaimQuestCheckBox":"AutoClaimQuestEnabled"} ; Noteab         

global directNumValues := {"WebhookRollSendInput":"WebhookRollSendMinimum"
    ,"WebhookRollPingInput":"WebhookRollPingMinimum"}
updateUIOptions(){
    for i,v in directValues {
        GuiControl,,%i%,% options[v]
    }

    for i,v in directNumValues {
        GuiControl,,%i%,% options[v]
    }

    if (options.PrivateServerId){
        GuiControl,, PrivateServerInput,% privateServerPre options.PrivateServerId
    } else {
        GuiControl,, PrivateServerInput,% ""
    }
    
    Loop 7 {
        v := options["ItemSpot" . A_Index]
        GuiControl,,CollectSpot%A_Index%CheckBox,%v%
    }

    Loop 3 {
        v := options["PotionCraftingSlot" . A_Index]
        GuiControl,ChooseString,PotionCraftingSlot%A_Index%DropDown,% potionIndex[v]
    }
}
updateUIOptions()

validateWebhookLink(link){
    return RegexMatch(link, "i)https:\/\/(canary\.|ptb\.)?(discord|discordapp)\.com\/api\/webhooks\/([\d]+)\/([a-z0-9_-]+)") ; filter by natro
}

applyNewUIOptions(){
    global hGui
    Gui mainUI:Default

    VarSetCapacity(wp, 44), NumPut(44, wp)
    DllCall("GetWindowPlacement", "uint", hGUI, "uint", &wp)
	x := NumGet(wp, 28, "int"), y := NumGet(wp, 32, "int")
    
    options.WindowX := x
    options.WindowY := y

    for i,v in directValues {
        GuiControlGet, rValue,,%i%
        options[v] := rValue
    }

    for i,v in directNumValues {
        GuiControlGet, rValue,,%i%
        m := 0
        if rValue is number
            m := 1
        options[v] := m ? rValue : 0
    }

    GuiControlGet, privateServerL,,PrivateServerInput
    if (privateServerL){
        RegExMatch(privateServerL, "(?<=privateServerLinkCode=)(.{32})", serverId)
        if (!serverId && RegExMatch(privateServerL, "(?<=code=)(.{32})")){
            MsgBox, % "The private server link you provided is a share link, instead of a privateServerLinkCode link. To get the code link, paste the share link into your browser and run it. This should convert the link to a privateServerLinkCode link. Copy and paste the converted link into the Private Server setting to fix this issue.`n`nThe link should look like: https://www.roblox.com/games/15532962292/Sols-RNG?privateServerLinkCode=..."
        }
        options.PrivateServerId := serverId ""
    }

    GuiControlGet, webhookLink,,WebhookInput
    if (webhookLink){
        valid := validateWebhookLink(webhookLink)
        if (valid){
            options.WebhookLink := webhookLink
        } else {
            if (options.WebhookLink){
                MsgBox,0,New Webhook Link Invalid, % "Invalid webhook link, the link has been reverted to your previous valid one."
            } else {
                MsgBox,0,Webhook Link Invalid, % "Invalid webhook link, the webhook option has been disabled."
                options.WebhookEnabled := 0
            }
        }
    }

    Loop 7 {
        GuiControlGet, rValue,,CollectSpot%A_Index%CheckBox
        options["ItemSpot" . A_Index] := rValue
    }

    Loop 3 {
        GuiControlGet, rValue,,PotionCraftingSlot%A_Index%DropDown
        options["PotionCraftingSlot" . A_Index] := reversePotionIndex[rValue]
    }
}

global importingSettings := 0
handleImportSettings(){
    global configPath

    if (importingSettings){
        return
    }

    MsgBox, % 1 + 4096, % "Import Settings", % "To import the settings from a previous version folder of the Macro, please select the ""config.ini"" file located in the previous version's ""settings"" folder when prompted. Press OK to begin."

    IfMsgBox, Cancel
        return
    
    importingSettings := 1

    FileSelectFile, targetPath, 3,, Import dolphSol Settings Through a config.ini File, % "Configuration settings (config.ini)"

    if (targetPath && RegExMatch(targetPath,"\\config\.ini")){
        if (targetPath != configPath){
            FileRead, retrieved, %targetPath%

            if (!ErrorLevel){
                FileDelete, %configPath%
                FileAppend, %retrieved%, %configPath%

                loadData()
                updateUIOptions()
                saveOptions()

                MsgBox, 0,Import Settings,% "Success!"
            } else {
                MsgBox,0,Import Settings Error, % "An error occurred while reading the file, please try again."
            }
        } else {
            MsgBox, 0,Import Settings Error, % "Cannot import settings from the current macro!"
        }
    }

    importingSettings := 0
}

handleWebhookEnableToggle(){
    Gui mainUI:Default
    GuiControlGet, rValue,,WebhookCheckBox

    if (rValue){
        GuiControlGet, link,,WebhookInput
        if (!validateWebhookLink(link)){
            GuiControl, , WebhookCheckBox,0
            MsgBox,0,Webhook Link Invalid, % "Invalid webhook link, the webhook option has been disabled."
        }
    }
}

global statDisplayInfo := {"RunTime":"Run Time"
    ,"Disconnects":"Disconnects"
    ,"ObbyCompletes":"Obby Completes"
    ,"ObbyAttempts":"Obby Attempts"
    ,"CollectionLoops":"Collection Loops"}

formatNum(n,digits := 2){
    n := Floor(n+0.5)
    cDigits := Max(1,Ceil(Log(Max(n,1))))
    final := n
    if (digits > cDigits){
        loopCount := digits-cDigits
        Loop %loopCount% {
            final := "0" . final
        }
    }
    return final
}

getTimerDisplay(t){
    return formatNum(Floor(t/86400)) . ":" . formatNum(Floor(Mod(t,86400)/3600)) . ":" . formatNum(Floor(Mod(t,3600)/60)) . ":" . formatNum(Mod(t,60))
}

updateStats(){
    ; per 1s
    if (running){
        options.RunTime += 1
    }

    statText := ""
    for i,v in statDisplayInfo {
        value := options[i]
        if (statText){
            statText .= "`n"
        }
        if (i = "RunTime"){
            value := getTimerDisplay(value)
        }
        statText .= v . ": " . value
    }
    Gui mainUI:Default
    GuiControl, , StatsDisplay, % statText
}
SetTimer, updateStats, 1000

global statusColors := {"Starting Macro":3447003
    ,"Roblox Disconnected":15548997
    ,"Reconnecting":9807270
    ,"Reconnecting, Roblox Opened":9807270
    ,"Reconnecting, Game Loaded":9807270
    ,"Reconnect Complete":3447003
    ,"Initializing":3447003
    ,"Searching for Items":15844367
    ,"Doing Obby":15105570
    ,"Completed Obby":5763719
    ,"Obby Failed, Retrying":11027200
    ,"Macro Stopped":3447003
    ,"Beginning Crafting Cycle":1752220}

updateStatus(newStatus){
    logMessage("[updateStatus] New status: " newStatus)
    if (options.WebhookEnabled){
        FormatTime, fTime, , HH:mm:ss
        if (!options.WebhookImportantOnly || importantStatuses[newStatus]){
            try webhookPost({embedContent: "[" fTime "]: " newStatus,embedColor: (statusColors[newStatus] ? statusColors[newStatus] : 1)})
        }
    }
    GuiControl,statusBar:,StatusBarText,% "Status: " newStatus
}

startDim(clickthru := 0,topText := ""){
    removeDim()
    w:=A_ScreenWidth,h:=A_ScreenHeight-2
    if (clickthru){
        Gui Dimmer:New,+AlwaysOnTop +ToolWindow -Caption +E0x20 ;Clickthru
    } else {
        Gui Dimmer:New,+AlwaysOnTop +ToolWindow -Caption
    }
    Gui Color, 333333
    Gui Show,NoActivate x0 y0 w%w% h%h%,Dimmer
    WinSet Transparent,% 75,Dimmer
    Gui DimmerTop:New,+AlwaysOnTop +ToolWindow -Caption +E0x20
    Gui Color, 222222
    Gui Font, s13
    Gui Add, Text, % "x0 y0 w400 h40 cWhite 0x200 Center", % topText
    Gui Show,% "NoActivate x" (A_ScreenWidth/2)-200 " y25 w400 h40"
}

removeDim(){
    Gui Dimmer:Destroy
    Gui DimmerTop:Destroy
}

global selectingAutoEquip := 0
startAutoEquipSelection(){
    if (selectingAutoEquip || macroStarted){
        return
    }

    MsgBox, % 1 + 4096, Begin Auto Equip Selection, % "Once you press OK, please click on the inventory slot that you would like to automatically equip.`n`nPlease ensure that your storage is open upon pressing OK. Press Cancel if it is not open yet."

    IfMsgBox, Cancel
        return
    
    if (macroStarted){
        return
    }

    selectingAutoEquip := 1

    startDim(1,"Click the target storage slot (Right-click to cancel)")

    Gui mainUI:Hide
}

cancelAutoEquipSelection(){
    if (!selectingAutoEquip) {
        return
    }
    removeDim()
    Gui mainUI:Show
    selectingAutoEquip := 0
}

completeAutoEquipSelection(){
    if (!selectingAutoEquip){
        return
    }
    applyNewUIOptions()

    MouseGetPos, mouseX,mouseY
    uv := getAspectRatioUVFromPosition(mouseX,mouseY,storageAspectRatio)
    options.AutoEquipX := uv[1]
    options.AutoEquipY := uv[2]

    saveOptions()
    cancelAutoEquipSelection()

    MsgBox, 0,Auto Equip Selection,Success!
}

handleLClick(){
    if (selectingAutoEquip){
        completeAutoEquipSelection()
    }
}

handleRClick(){
    if (selectingAutoEquip){
        cancelAutoEquipSelection()
    }
}

global guis := Object(), timers := Object()

Highlight(x="", y="", w="", h="", showTime=2000, color="Red", d=2) {
    ; If no coordinates are provided, clear all highlights
    if (x = "" || y = "" || w = "" || h = "") {
        for key, timer in timers {
            SetTimer, % timer, Off
            Gui, %key%Top:Destroy
            Gui, %key%Left:Destroy
            Gui, %key%Bottom:Destroy
            Gui, %key%Right:Destroy
            guis.Delete(key)
        }
        timers := Object()
        return
    }

    x := Floor(x)
    y := Floor(y)
    w := Floor(w)
    h := Floor(h)

    ; Create a new highlight
    key := "Highlight" x y w h
    Gui, %key%Top:New, +AlwaysOnTop -Caption +ToolWindow
    Gui, %key%Top:Color, %color%
    Gui, %key%Top:Show, x%x% y%y% w%w% h%d%

    Gui, %key%Left:New, +AlwaysOnTop -Caption +ToolWindow
    Gui, %key%Left:Color, %color%
    Gui, %key%Left:Show, x%x% y%y% h%h% w%d%

    Gui, %key%Bottom:New, +AlwaysOnTop -Caption +ToolWindow
    Gui, %key%Bottom:Color, %color%
    Gui, %key%Bottom:Show, % "x"x "y"(y+h-d) "w"w "h"d

    Gui, %key%Right:New, +AlwaysOnTop -Caption +ToolWindow
    Gui, %key%Right:Color, %color%
    Gui, %key%Right:Show, % "x"(x+w-d) "y"y "w"d "h"h

    ; Store the gui and set a timer to remove it
    guis[key] := true
    if (showTime > 0) {
        timerKey := Func("RemoveHighlight").Bind(key)
        timers[key] := timerKey
        SetTimer, % timerKey, -%showTime%
    }
}

RemoveHighlight(key) {
    global guis, timers
    Gui, %key%Top:Destroy
    Gui, %key%Left:Destroy
    Gui, %key%Bottom:Destroy
    Gui, %key%Right:Destroy
    guis.Delete(key)
    timers.Delete(key)
}

startMacro(){
    logMessage("=====================================")
    updateStatus("Starting Macro")

    ; Log system information and relevant variables
    logMessage("System Information:")
    logMessage("OS Version: " A_OSVersion, 1)
    logMessage("AHK Version: " A_AhkVersion, 1)
    logMessage("Screen Width: " A_ScreenWidth, 1)
    logMessage("Screen Height: " A_ScreenHeight, 1)
    logMessage("Screen DPI: " A_ScreenDPI, 1)
    logMessage("Active Language: " getCurrentLanguage(), 1)

    ; Log macro variables
    logMessage("Macro Variables:")
    logMessage("Version: " version, 1)
    logMessage("OCR Enabled: " options.OCREnabled, 1)

    if (!canStart){
        logMessage("[startMacro] canStart is false, exiting...")
        return
    }
    if (macroStarted && running) { ; Added extra running check to prevent exiting prematurely
        logMessage("[startMacro] macroStarted is already true, exiting...")
        return
    }

    macroStarted := 1
    updateStatus("Macro Started")

    ; cancel any interfering stuff
    cancelAutoEquipSelection()

    ; Save any changes made in the UI
    applyNewUIOptions()
    saveOptions()

    Gui, mainUI:+LastFoundExist
    WinSetTitle, % "dolphSol Macro " version " (Running)"

    ; Run, % """" . A_AhkPath . """ """ mainDir . "lib\status.ahk"""
    Run, *RunAs "%A_AhkPath%" /restart "%mainDir%lib\status.ahk"

    if (options.StatusBarEnabled){
        Gui statusBar:Show, % "w220 h25 x" (A_ScreenWidth-300) " y100", dolphSol Status
    }
    
    ; Log game information and relevant variables
    logMessage("Roblox Information:")
    
    robloxId := GetRobloxHWND()
    if (!robloxId){
        logMessage("[startMacro] Roblox ID not found, attempting to reconnect...")
        attemptReconnect()
    }

    ; Get window position and size
    getRobloxPos(pX,pY,width,height)
    logMessage("Window ID: " robloxId, 1)
    logMessage("Width: " width, 1)
    logMessage("Height: " height, 1)


    options.LastRobloxRestart := getUnixTime() ; Reset so isn't immediately triggered
    running := 1
    logMessage("") ; empty line for separation
    logMessage("[startMacro] Starting main loop")
    WinActivate, ahk_id %robloxId%
    while running {
        try {
            mainLoop()
        } catch e {
            ewhat := e.what, efile := e.file, eline := e.line, emessage := e.message, eextra := e.extra
            logMessage("[startMacro] Error: `nwhat: " ewhat "`nfile: " efile "`nline: " eline "`nmessage: " emessage "`nextra: " eextra)
            try {
                webhookPost({embedContent: "what: " e.what ", file: " e.file
                . ", line: " e.line ", message: " e.message ", extra: " e.extra, embedTitle: "Error Received", color: 15548997})
            }
            MsgBox, 16,, % "Error!`n`nwhat: " e.what "`nfile: " e.file
                . "`nline: " e.line "`nmessage: " e.message "`nextra: " e.extra
            
            running := 0
        }
        
        Sleep, 2000
    }
}

if (!options.FirstTime){
    options.FirstTime := 1
    saveOptions()
    MsgBox, 0,dolphSol Macro - Welcome, % "Welcome to dolphSol macro!`n`nIf this is your first time here, make sure to go through all of the tabs to make sure your settings are right.`n`nIf you are here from an update, remember that you can import all of your previous settings in the Settings menu.`n`nMake sure join the Discord server and check the GitHub page for the community and future updates, which can both be found in the Credits page. (Discord link is also in the bottom right corner)"
}

if (!options.WasRunning){
    options.WasRunning := 1
    saveOptions()
}

canStart := 1

return

; button stuff

StartClick:
    if (running) {
        return
    }
    startMacro()
    return

PauseClick:
    if (!running) {
        return
    }
    ; MsgBox, 0,% "Pause",% "Please note that the pause feature isn't very stable currently. It is suggested to stop instead."
    handlePause()
    return

StopClick:
    if (!running) {
        return
    }
    stop()
    Reload
    return

AutoEquipSlotSelectClick:
    startAutoEquipSelection()
    return

DiscordServerClick:
    Run % "https://discord.gg/DYUqwJchuV"
    return

EnableWebhookToggle:
    handleWebhookEnableToggle()
    return

ImportSettingsClick:
    handleImportSettings()
    return

WebhookRollImageCheckBoxClick:
    Gui mainUI:Default
    GuiControlGet, v,, WebhookRollImageCheckBox
    if (v){
        MsgBox, 0, Aura Roll Image Warning, % "Warning: Currently, the aura image display for the webhook is fairly unstable, and may cause random delays in webhook sends due to image loading. Enable at your own risk."
    }
    return

GetRobloxVersion:
    Gui, Submit, NoHide
    options["RobloxUpdatedUI"] := (RobloxUpdatedUIRadio1 = 1) ? 1 : 2
    return

OCREnabledCheckBoxClick:
    Gui mainUI:Default
    GuiControlGet, v,, OCREnabledCheckBox
    if (v) {
        options.OCREnabled := 0
        currentLanguage := getCurrentLanguage()
        if (currentLanguage = "English") {
            options.OCREnabled := 1
        }
        ocrLanguages := getOCRLanguages()
        if (InStr(ocrLanguages, "en-US")) {
            options.OCREnabled := 1
        }

        if (options.OCREnabled) { ; Confirm resolution settings
            if (A_ScreenWidth <> 1920 || A_ScreenHeight <> 1080 || A_ScreenDPI <> 96) {
                options.OCREnabled := 0
                MsgBox, 0, OCR Error, % "A monitor resolution of 1920x1080 with a 100% scale is required for OCR at this time.`n"
                                      . "We will continue working to support more configurations."
            } else {
                ; getRobloxPos(pX, pY, pW, pH)
                ; if not (pW = 1920 && pH = 1080 && A_ScreenDPI = 96) { ; Disable if Roblox isnt in fullscreen
                ;     MsgBox, 0, Another Error, % "Roblox must be in fullscreen to use OCR."
                ;     options.OCREnabled := 0
                ; } else {
                ;     return
                ; }
            }
        } else {
            MsgBox, 0, OCR Language Error, % "Unable to use OCR. Please set your language to English-US in your PC settings and restart to enable OCR."
        }
        ; GuiControl, , OCREnabledCheckBox, 0
    }
    return

MoreCreditsClick:
    creditText =
    (
    Development

    - Assistant Developer - Stanley (stanleyrekt)
    - Path Contribution - sanji (sir.moxxi), Flash (drflash55)
    - Path Inspiration - Aod_Shanaenae

    Supporters (Donations)

    - @Bigman
    - @sir.moxxi (sanji)
    - @zrx
    - @dj_frost
    - @FlamePrince101 - Member
    - @jw
    - @Maz - Member
    - @dead_is4
    - @CorruptExpy_II
    - @Ami.n
    - @s.a.t.s
    - @UnamedWasp - Member
    - @JujuFRFX
    - @Xon67
    - @NightLT98 - Member

    Thank you to everyone who currently supports and uses the macro! You guys are amazing!
    )
    MsgBox, 0, More Credits, % creditText
    return

; help buttons
ObbyHelpClick:
    MsgBox, 0, Obby, % "Section for attempting to complete the Obby on the map for the +30% luck buff every 2 minutes. If you have the VIP Gamepass, make sure to enable it in Settings.`n`nCheck For Obby Buff Effect - Checks your status effects upon completing the obby and attempts to find the buff. If it is missing, the macro will retry the obby one more time. Disable this if your macro keeps retrying the obby after completing it. The ObbyCompletes stat will only increase if this check is enabled.`n`nPLEASE NOTE: The macro's obby completion ability HIGHLY depends on a stable frame-rate, and will likely fail from any frame freezes. If your macro is unable to complete the obby at all, it is best to disable this option."
    return

AutoEquipHelpClick:
    MsgBox, 0, Auto Equip, % "Section for automatically equipping a specified aura every macro round. This is important for equipping auras without walk animations, which may interfere with the macro. This defaults to your first storage slot if not selected. Enabling this will close your chat window due to it possibly getting in the way of the storage button.`n`nUse the Select Storage Slot button to select a slot in your Aura Storage to automatically equip. Right click when selecting to cancel.`n`nThis feature is HIGHLY RECOMMENDED to be used on a non-animation aura for best optimization."
    return

CollectHelpClick:
    MsgBox, 0, Item Collecting, % "Section for automatically collecting naturally spawned items around the map. Enabling this will have the macro check the selected spots every loop after doing the obby (if enabled and ready).`n`nYou can also specify which spots to collect from. If a spot is disabled, the macro will not grab any items from the spot. Please note that the macro always takes the same path, it just won't collect from a spot if it's disabled. This feature is useful if you are sharing a server with a friend, and split the spots with them.`n`nItem Spots:`n 1 - Left of the Leaderboards`n 2 - Bottom left edge of the Map`n 3 - Under a tree next to the House`n 4 - Inside the House`n 5 - Under the tree next to Jake's Shop`n 6 - Under the tree next to the Mountain`n 7 - On top of the Hill with the Cave"
    return

WebhookHelpClick:
    MsgBox, 0, Discord Webhook, % "Section for connecting a Discord Webhook to have status messages displayed in a target Discord Channel. Enable this option by entering a valid Discord Webhook link.`n`nTo create a webhook, you must have Administrator permissions in a server (preferably your own, separate server). Go to your target channel, then configure it. Go to Integrations, and create a Webhook in the Webhooks Section. After naming it whatever you like, copy the Webhook URL, then paste it into the macro. Now you can enable the Discord Webhook option!`n`nRequires a valid Webhook URL to enable.`n`nImportant events only - The webhook will only send important events such as disconnects, rolls, and initialization, instead of all of the obby/collecting/crafting ones.`n`nYou can provide your Discord ID here as well to be pinged for rolling a rarity group or higher when detected by the system. You can select the minimum notification/send rarity in the Roll Detection system.`n`nHourly Inventory Screenshots - Screenshots of both your Aura Storage and Item Inventory are sent to your webhook."
    return

RollDetectionHelpClick:
    MsgBox, 0, Roll Detection, % "Section for detecting rolled auras through the registered star color (if 10k+). Any 10k+ auras that can be sent will be sent to the webhook, with the option to ping if the rarity is above the minimum.`n`nFor minimum settings, the number determines the lowest possible rarity the webhook will send/ping for. Values of 0 will disable the option completely. Values under 10,000 will toggle all 1k+ rolls, due to them being near undetectable.`n`nAura Images can be toggled to show the wiki-based images of your rolled auras in the webhook. WARNING: After some testing, this has proven to show some lag, leading to some send delay issues. Use at your own risk!"
    return

OCRHelpClick:
    MsgBox, 0, OCR, % "OCR allows the macro to respond to events instead of blindly pressing keys and moving the mouse. Currently requires Roblox to be ran at 1920x1080 resolution and 100% scale."
	return

UIHelpClick:
    Gui, New 
    Gui, Add, Picture, x20 y50, % mainDir "images\UIInformation.png" ; Change to the path of your image file
    Gui, Show, AutoSize  ; Adjust the GUI window size to fit the image
    return

; gui close buttons
mainUIGuiClose:
    stop(1)
return

AuraGuiClose:
    applyAuraSettings() ; Update options with the new aura settings
    saveOptions()  ; Save the options to the config file
    Gui, AuraSettings:Destroy
return

BiomeGuiClose:
    applyBiomeSettings() ; Update options
    saveOptions()  ; Save the options
    Gui, BiomeSettings:Destroy
return

ItemSchedulerGuiClose:
    SaveItemSchedulerSettings() ; Update options
    saveOptions()  ; Save the options
    Gui, ItemSchedulerSettings:Destroy
return

ClearToolTip:
    ToolTip
return

; hotkeys
#If !running
    F1::startMacro()

    ^F1::
        closeRoblox()
        Sleep, 1500
        startMacro()
        return

    ^F2::
        alignCamera()
        Sleep, 2000
        reset()
        return
#If

#If running || reconnecting
    F2::handlePause()

    ^F2::
        handlePause()
        Sleep, 500
        alignCamera()
        Sleep, 500
        reset()
        Sleep, 1500
        handlePause()
        return

    ; F8::
    ;     Sleep, 500
    ;     alignCamera()
    ;     Sleep, 2000
    ;     reset()
    ;     Sleep, 500
    ;     handlePause()
    ;     return

    F3::
        stop()
        Reload
        return

    ^F1::
        closeRoblox()
        stop()
        Reload
        Sleep, 3500
        startMacro()
        return
#If

#If selectingAutoEquip
    ~LButton::handleLClick()
    ~RButton::handleRClick()
#If

; Disable keyboard control of macro GUI to avoid accidental changes
#If WinActive("ahk_id" hGUI)
    Up::
    Down::
    Left::
    Right::
    Space::
    Tab::
    Enter::Return
#If

F4::
    Gui mainUI:Show
    return

F5:: ; For debugging/testing
    disableAlignment := !disableAlignment
    ToolTip, % disableAlignment ? "Initial Align Disabled" : "Initial Align Enabled"
    SetTimer, ClearToolTip, -5000
    return

