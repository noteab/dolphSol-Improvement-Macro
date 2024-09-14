#singleinstance, force
#noenv
RegExMatch(A_ScriptDir, ".*(?=\\paths)", mainDir)
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen
#Include ..\lib\pathReference.ahk

; revision by sanji (sir.moxxi) and Flash (drflash55)

; 2nd revision by InnocentHuman

Spot1() {

	walkSend("w","Down")
	walkSend("d","Down")
	walkSleep(1300)
	walkSend("d","Up")
	walkSleep(2150)
	walkSend("w","Up")
	collect(1)

}

Spot2() {

	walkSend("a","Down")
	walkSleep(1000)
	press("w", 200)
	walkSleep(2300)
	walkSend("a", "Up")
	collect(2)

}

Spot3() {

	walkSend("a", "Down")
	walkSleep(300)
	jump()
	walkSleep(350)
	walkSend("s","Down")
	walkSleep(250)
	jump()
	walkSleep(350)
	walkSend("a", "Up")
	walkSleep(250)
	jump()
	walkSleep(350)
	walkSend("s","Up")
	walkSend("a", "Down")
	walkSleep(100)
	jump()
	walkSleep(350)
	walkSend("w","Down")
	walkSleep(750)
	walkSend("a", "Up")
	walkSend("w","Up")
	collect(3)

}

Spot4() {

	walkSend("a", "Down")
	walkSleep(200)
	walkSend("s","Down")
	walkSleep(750)
	walkSend("a", "Up")
	walkSleep(200)
	walkSend("s","Up")
	collect(4)

}

Spot5() {

	walkSend("d","Down")
	walkSend("s","Down")
	walkSleep(3700)
	walkSend("d","Up")
	jump()
	walkSleep(500)
	walkSend("s","Up")
	collect(5)

}

Spot6() {

	walkSend("d","Down")
	walkSleep(1100)
	jump()
	press("s", 250)
	walkSleep(220	0)
	press("w", 150)
	walkSleep(150)
	walkSend("d","Up")
	collect(6)

}

Spot7() {

	walkSend("d","Down")
	jump()
	press("w", 300)
	walkSleep(2400)
	walkSend("w","Down")
	walkSleep(400)
	walkSend("Space", "Down")
	walkSleep(600)
	walkSend("Space", "Up")
	walkSleep(400)
	walkSend("d","Up")
	jump()
	walkSleep(600)
	jump()
	walkSleep(550)
	jump()
	walkSleep(800)
	walkSend("w", "Up")
	collect(7)

}


if options["ItemSpot" . 1] or options["ItemSpot" . 2] {
	
	Spot1()
	
	if options["ItemSpot" . 2] {
	
		Spot2()
		
	}
	
	reset()
	Sleep, 1000
	
}

if options["ItemSpot" . 3] or options["ItemSpot" . 4] {
	
	Spot3()
	
	if options["ItemSpot" . 4] {
	
		Spot4()
		
	}
	
	reset()
	Sleep, 1000
	
}

if options["ItemSpot" . 5] or options["ItemSpot" . 6] or options["ItemSpot" . 7] {
	
	Spot5()
	
	if options["ItemSpot" . 6] or options["ItemSpot" . 7] {
	
		Spot6()

		if options["ItemSpot" . 7] {
		
			Spot7()
			
		}
	}
}