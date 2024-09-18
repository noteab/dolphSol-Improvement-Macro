#singleinstance, force
#noenv
RegExMatch(A_ScriptDir, ".*(?=\\paths)", mainDir)
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen
#Include ..\lib\pathReference.ahk

sleep, 1000
walkSend("s", "Down")
;walkSleep(4880)
walkSleep(4630)
press("a",500)
walkSleep(1000)
press("a",250)
walkSleep(100)


if (options.VIP){
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
    jump()
    walkSleep(250)
    walkSend("s", "Up")
    walkSleep(300)
    jump()
    walkSend("s", "Down")
    walkSleep(350)
    walkSend("a","Up")
    walkSleep(300)
    walkSend("a","Down")
    jump()
    walkSleep(700)
    jump()
    walkSleep(500)
    walkSend("a","Up")
    walkSleep(500)
    walkSend("s","Up")
} else {
    walkSend("s","Down")
    walkSend("a","Down")
    jump()
    walkSleep(600)
    walkSend("a","Up")
    walkSleep(150)
    jump()
    walkSleep(200)
    walkSend("s", "Up")
    Sleep, 500
    jump()
    press("s", 500)
    Sleep, 200
    press("w", 50)
    Sleep, 100
    jump()
    walkSend("s", "Down")
    walkSleep(600)
    walkSend("a","Down")
    walkSleep(500)
    walkSend("s", "Up")
    walkSleep(100)
    jump()
    Sleep, 100
    walkSend("s", "Down")
    Sleep, 500
    jump()
    walkSend("s", "Down")
    walkSleep(350)
    walkSend("a","Up")
    walkSleep(300)
    walkSend("s","Down")
    walkSend("a","Down")
    jump()
    walkSleep(700)
    jump()
    walkSleep(600)
    walkSend("a","Up")
    walkSleep(500)
    walkSend("s", "Up")
}
