#singleinstance, force
#noenv
RegExMatch(A_ScriptDir, ".*(?=\\paths)", mainDir)
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen
#Include ..\lib\pathReference.ahk


Sleep, 1000

if (options.IsNikoPath = 1) {
    walkSend("s", "Down")
    ;walkSleep(4880)
    walkSleep(4630)
    press("a",500)
    walkSleep(1000)
    press("a",250)
    walkSleep(100)
} else {
    walkSend("w", "Down")
    ;walkSleep(4880)
    walkSleep(4630)
    press("d",500)
    walkSleep(1000)
    press("d",250)
    walkSleep(100)
}

if (options.VIP){
    ; Boat Jump (Niko)
    if (options.IsNikoPath = 1) {
        walkSend("s","Down")
        walkSend("a","Down")
        jump()
        walkSleep(500)
        walkSend("a","Up")
        walkSleep(200)
        jump()
        walkSleep(150)
        walkSend("s", "Up")
        Sleep, 500

        ; 1st Island
        jump()
        press("s", 500)
        Sleep, 200
        press("w", 50)
        Sleep, 100
        jump()
        walkSend("s", "Down")
        walkSleep(600)
        walkSend("a","Down")
        walkSleep(550)

        ; 2nd Island
        jump()
        walkSleep(350)
        walkSend("s", "Up")
        walkSleep(150)
        jump()
        walkSend("s", "Down")
        walkSleep(350)
        walkSend("a","Up")
        walkSleep(400)

        ; Star Island
        jump()
        walkSleep(100)
        walkSend("a","Down")
        jump()
        walkSleep(1500)
        walkSend("a","Up")
        walkSend("s","Up")

    } else {
        walkSend("w","Down")
        walkSend("d","Down")
        jump()
        walkSleep(500)
        walkSend("d","Up")
        walkSleep(200)
        jump()
        walkSleep(150)
        walkSend("w", "Up")
        Sleep, 500

        ; 1st Island
        jump()
        press("w", 500)
        Sleep, 200
        press("s", 50)
        Sleep, 100
        jump()
        walkSend("w", "Down")
        walkSleep(600)
        walkSend("d","Down")
        walkSleep(550)

        ; 2nd Island
        jump()
        walkSleep(350)
        walkSend("w", "Up")
        walkSleep(150)
        jump()
        walkSend("w", "Down")
        walkSleep(350)
        walkSend("d","Up")
        walkSleep(400)

        ; Star Island
        jump()
        walkSleep(100)
        walkSend("d","Down")
        jump()
        walkSleep(1500)
        walkSend("d","Up")
        walkSend("w","Up")
    }
 
} else {

    if (options.IsNikoPath = 1) {
        walkSend("s","Down")
        walkSend("a","Down")
        jump()
        walkSleep(600)
        walkSend("a","Up")
        walkSleep(150)
        walkSend("s","Up")
        walkSleep(150)
        walkSend("s","Down")
        jump()
        walkSleep(150)
        walkSend("s","Up")
        Sleep, 500

        ; 1st Island
        walkSend("s","Down")
        walkSleep(50)
        jump()
        walkSleep(450)
        walkSend("s","Up")
        Sleep, 200
        press("w", 50)
        Sleep, 100
        jump()
        walkSend("s", "Down")
        walkSleep(700)
        walkSend("a","Down")
        walkSleep(520)

        ; 2nd Island
        jump()
        walkSleep(200)
        walkSend("s", "Up")
        walkSleep(300)
        walkSend("a", "Up")
        walkSend("s", "Down")
        jump()
        walkSleep(200)
        walkSend("a", "Down")
        walkSend("s", "Up")
        walkSleep(350)
        walkSend("a", "Up")
        walkSend("s", "Down")
        walkSleep(300)
        jump()
        walkSleep(100)
        walkSend("a", "Down")

        ; Star Island
        walkSleep(300)
        walkSend("a", "Down")
        jump()
        walkSleep(1100)
        walkSend("a","Up")
        walkSleep(200)
        walkSend("s", "Up")
    }

    
}
