#singleinstance, force
#noenv
RegExMatch(A_ScriptDir, ".*(?=\\paths)", mainDir)
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen
#Include ..\lib\pathReference.ahk

; revision by sanji (sir.moxxi) and Flash (drflash55)

; 2nd revision by InnocentHuman

; 3rd revision by InnocentHuman and _justalin (Allan)

; new version of default dolphsol collect path - noteab 

Spot1() { ; Allan's Fix
	
	if (options.IsNikoPath = 1) {
		walkSend("w","Down")
		walkSend("d","Down")
		walkSleep(1100)
		walkSend("d","Up")
		walkSleep(2500)
		walkSend("w","Up")
		collect(1)
		
	} else {
		walkSend("s","Down")
		walkSend("a","Down")
		walkSleep(1100)
		walkSend("a","Up")
		walkSleep(2500)
		walkSend("s","Up")
		collect(1)
	}
	
}

Spot2() {  ; Allan's Fix

	if (options.IsNikoPath = 1) {
		walkSend("a","Down")
		walkSleep(3400)
		walkSend("a", "Up")
		collect(2)
	} else {
		walkSend("d","Down")
		walkSleep(3400)
		walkSend("d", "Up")
		collect(2)
	}

}

Spot3() {

	if (options.IsNikoPath = 1) {
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

	} else {
		walkSend("d","Down")
		walkSleep(300)
		jump()
		walkSleep(350)
		walkSend("w","Down")
		walkSleep(250)
		jump()
		walkSleep(350)
		walkSend("d","Up")
		walkSleep(250)
		jump()
		walkSleep(350)
		walkSend("w","Up")
		walkSend("d","Down")
		walkSleep(100)
		jump()
		walkSleep(350)
		walkSend("s","Down")
		walkSleep(750)
		walkSend("d","Up")
		walkSend("s","Up")
		collect(3)
	}
	

}

Spot4() { ; Allan's Fix

	if (options.IsNikoPath = 1) {
		walkSend("s", "Down")
		walkSleep(1500)
		walkSend("s", "Up")
		walkSend("a","Down")
		walkSleep(820)
		walkSend("a","Up")
		walkSend("w", "Down")
		walkSleep(600)
		walkSend("w", "Up")
		collect(4)
	} else {
		walkSend("d","Down")
		walkSleep(200)
		walkSend("w","Down")
		walkSleep(750)
		walkSend("d","Up")
		walkSleep(200)
		walkSend("w","Up")
		collect(4)
	}

}

Spot5() { ; Allan's Fix

	if (options.IsNikoPath = 1) {
		walkSend("d","Down")
		walkSend("s","Down")
		walkSleep(3700)
		walkSend("d","Up")
		walkSleep(150)
		jump()
		walkSleep(500)
		walkSend("s","Up")
		collect(5)
	} else {
		walkSend("a","Down")
		walkSend("w","Down")
		walkSleep(3700)
		walkSend("a","Up")
		walkSleep(150)
		jump()
		walkSleep(500)
		walkSend("w","Up")
		collect(5)
	}
}

Spot6() { ; Allan's Fix
	if (options.IsNikoPath = 1) {
		walkSend("d","Down")
		walkSleep(900)
		jump()
		press("s", 400)
		walkSleep(2500)
		walkSleep(100)
		walkSend("d","Up")
		press("w", 300)
		collect(6)
	} else {
		walkSend("a","Down")
		walkSleep(900)
		jump()
		press("w", 400)
		walkSleep(2500)
		walkSleep(100)
		walkSend("a","Up")
		press("s", 300)
		collect(6)
	}
	
}

Spot7() { ; Allan's Fix

	if (options.IsNikoPath = 1) {
		walkSend("d","Down") ; Walks to 
		walkSleep(2500)
		walkSend("d","Up")

		walkSend("w","Down")
		walkSleep(500)
		jump()
		walkSleep(600)
		walkSend("w", "Up")
		walkSend("d","Down")
		walkSleep(100)
		jump()
		walkSleep(200)
		walkSend("d","Up")
		walkSend("w","Down")
		walkSleep(200)
		jump()
		walkSleep(600)
		walkSend("d","Down")
		jump()
		walkSleep(200)
		walkSend("d","Up")
		walkSleep(100)
		walkSend("w", "Up")

		walkSend("w","Down")
		walkSleep(200)
		jump()
		walkSleep(500)
		press("d","200")
		jump()
		walkSleep(400)
		walkSend("w", "Up")
		walkSend("a", "Down")
		walkSleep(400)
		walkSend("a", "Up")
		collect(7)
	} else {
		walkSend("a","Down")
		walkSleep(2500)
		walkSend("a","Up")

		walkSend("s","Down")
		walkSleep(500)
		jump()
		walkSleep(600)
		walkSend("s", "Up")
		walkSend("a","Down")
		walkSleep(100)
		jump()
		walkSleep(200)
		walkSend("a","Up")
		walkSend("s","Down")
		walkSleep(200)
		jump()
		walkSleep(600)
		walkSend("a","Down")
		jump()
		walkSleep(200)
		walkSend("a","Up")
		walkSleep(100)
		walkSend("s", "Up")

		walkSend("s","Down")
		walkSleep(200)
		jump()
		walkSleep(500)
		press("a","200")
		jump()
		walkSleep(400)
		walkSend("s", "Up")
		walkSend("d", "Down")
		walkSleep(400)
		walkSend("d", "Up")
		collect(7)
	}
}

Spot8VIP() { ; All credits to Allan & me

	if (options.IsNikoPath = 1) {
		;tree obby
		walkSend("w","Down")
		walkSleep(1800)
		press("d",500)
		walkSend("w","Up")
		sleep, 400

		walkSend("a","Down")
		walkSleep(420)
		walkSend("a","Up")

		walkSend("w","Down")
		walkSleep(100)
		jump()
		walkSleep(1500)
		walkSend("d","Down")
		walkSleep(20)
		jump()
		sleep, 700

		jump()
		walkSleep(100)
		walkSend("w","Up")
		walkSleep(300)

		walkSend("w","Down")
		walkSleep(100)
		jump()
		walkSleep(500)
		walkSend("w","Up")
		walkSleep(200)
		jump()
		walkSleep(400)
		jump()
		walkSleep(650)
		walkSend("d","Up")
		sleep, 300


		;mountain obby

		walkSend("s","Down")
		walkSleep(300)
		jump()
		walkSleep(800)
		jump()
		walkSleep(800)
		walkSend("s","Up")

		press("w","200")
		walkSend("s","Down")
		walkSend("d","Down")
		walkSleep(300)
		jump()
		walkSleep(200)
		walkSend("d","Up")
		walkSend("a","Down")
		walkSleep(500)
		walkSend("a","Up")
		walkSleep(400)
		jump()

		walkSleep(800)
		walkSend("s","Up")
		walkSend("a","Down")
		walkSleep(800)
		walkSend("a","Up")

		walkSend("s","Down")
		jump()
		walkSleep(900)
		walkSend("s","Up")

		walkSend("d","Down")
		walkSleep(1000)
		walkSend("d","Up")

		walkSend("w","Down")
		walkSend("d","Down")
		jump()
		walkSleep(50)
		walkSend("w","Up")
		walkSleep(200)
		walkSend("s","Down")
		walkSleep(500)
		walkSend("s","Up")

		jump()
		walkSleep(400)
		walkSend("s","Down")
		walkSend("d","Up")
		jump()
		walkSleep(1700)
		walkSend("s","Up")

		walkSend("a","Down")
		walkSleep(800)
		walkSend("a","Up")
		walkSend("s","Down")
		walkSleep(300)
		walkSend("s","Up")

		walkSend("w","Down")
		walkSleep(300)
		walkSend("w","Up")
		walkSend("a","Down")
		walkSleep(800)
		jump()
		walkSleep(500)
		walkSend("a","Up")

		walkSend("w","Down")
		walkSleep(270)
		walkSend("w","Up")
		walkSend("a","Down")
		walkSleep(420)


		jump()
		walkSleep(100)
		walkSend("a","Up")
		walkSend("s","Down")
		walkSend("a","Down")
		walkSleep(300)
		walkSend("a","Up")
		walkSend("s","Up")

		;end part

		sleep, 500
		walkSend("d","Down")
		walkSleep(500)
		walkSend("d","Up")
		walkSend("s","Down")
		walkSleep(300)
		walkSend("s","Up")
		walkSend("a","Down")
		walkSleep(400)
		walkSend("a","Up")
		walkSleep(500)
		walkSend("s","Down")
		walkSleep(300)
		walkSend("d","Down")
		walkSleep(150)
		walkSend("d","up")
		walkSleep(350)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(300)
		walkSend("d","Up")

		collect(8)
	} else {
		;tree obby

		walkSend("s","Down")
		walkSleep(1800)
		press("a",500)
		walkSend("s","Up")
		sleep, 400

		walkSend("d","Down")
		walkSleep(420)
		walkSend("d","Up")

		walkSend("s","Down")
		walkSleep(100)
		jump()
		walkSleep(1500)
		walkSend("a","Down")
		walkSleep(20)
		jump()
		sleep, 700

		jump()
		walkSleep(100)
		walkSend("s","Up")
		walkSleep(300)

		walkSend("s","Down")
		walkSleep(100)
		jump()
		walkSleep(500)
		walkSend("s","Up")
		walkSleep(200)
		jump()
		walkSleep(400)
		jump()
		walkSleep(650)
		walkSend("a","Up")
		sleep, 300


		;mountain obby

		walkSend("w","Down")
		walkSleep(300)
		jump()
		walkSleep(800)
		jump()
		walkSleep(800)
		walkSend("w","Up")

		press("w","200")
		walkSend("w","Down")
		walkSend("a","Down")
		walkSleep(300)
		jump()
		walkSleep(200)
		walkSend("a","Up")
		walkSend("d","Down")
		walkSleep(500)
		walkSend("d","Up")
		walkSleep(400)
		jump()

		walkSleep(800)
		walkSend("w","Up")
		walkSend("d","Down")
		walkSleep(800)
		walkSend("d","Up")

		walkSend("w","Down")
		jump()
		walkSleep(900)
		walkSend("w","Up")

		walkSend("a","Down")
		walkSleep(1000)
		walkSend("a","Up")

		walkSend("s","Down")
		walkSend("a","Down")
		jump()
		walkSleep(50)
		walkSend("s","Up")
		walkSleep(200)
		walkSend("w","Down")
		walkSleep(500)
		walkSend("w","Up")

		jump()
		walkSleep(400)
		walkSend("w","Down")
		walkSend("a","Up")
		jump()
		walkSleep(1700)
		walkSend("w","Up")

		walkSend("d","Down")
		walkSleep(800)
		walkSend("d","Up")
		walkSend("w","Down")
		walkSleep(300)
		walkSend("w","Up")

		walkSend("s","Down")
		walkSleep(300)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(800)
		jump()
		walkSleep(500)
		walkSend("d","Up")

		walkSend("s","Down")
		walkSleep(270)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(420)


		jump()
		walkSleep(100)
		walkSend("d","Up")
		walkSend("w","Down")
		walkSend("d","Down")
		walkSleep(300)
		walkSend("d","Up")
		walkSend("w","Up")

		;end part

		sleep, 500
		walkSend("a","Down")
		walkSleep(500)
		walkSend("a","Up")
		walkSend("w","Down")
		walkSleep(300)
		walkSend("w","Up")
		walkSend("d","Down")
		walkSleep(400)
		walkSend("d","Up")
		walkSleep(500)
		walkSend("w","Down")
		walkSleep(300)
		walkSend("a","Down")
		walkSleep(150)
		walkSend("a","up")
		walkSleep(350)
		walkSend("s","Up")
		walkSend("a","Down")
		walkSleep(300)
		walkSend("a","Up")

		collect(8)
	}
}

Spot8() { ; All credits to Allan & Me

	if (options.IsNikoPath = 1) {
		;tree obby

		walkSend("w","Down")
		walkSleep(1800)
		press("d",500)
		walkSend("w","Up")
		sleep, 400

		walkSend("a","Down")
		walkSleep(420)
		walkSend("a","Up")

		walkSend("w","Down")
		walkSleep(100)
		jump()
		walkSleep(550)
		jump()
		walkSleep(950)
		walkSend("w","Up")

		sleep, 500

		walkSend("w","Down")
		walkSend("d","Down")
		walkSleep(100)
		jump()
		walkSleep(500)
		jump()
		walkSleep(200)
		jump()
		walkSend("w","Up")
		walkSleep(200)
		jump()
		walkSend("w","Down")
		walkSleep(500)
		jump()
		walkSend("w","Up")
		walkSleep(300)
		jump()
		walkSleep(300)
		jump()
		walkSleep(600)
		walkSend("d","Up")

		;mountain obby

		walkSend("s","Down")
		walkSleep(400)
		jump()
		walkSleep(900)
		jump()
		walkSleep(800)
		walkSend("s","Up")

		press("w","200")
		walkSend("s","Down")
		walkSend("d","Down")
		walkSleep(300)
		jump()
		walkSleep(200)
		walkSend("d","Up")
		walkSend("a","Down")
		walkSleep(500)
		walkSend("a","Up")
		walkSleep(400)
		jump()

		walkSleep(800)
		walkSend("s","Up")
		walkSend("a","Down")
		walkSleep(800)
		walkSend("a","Up")

		walkSend("s","Down")
		jump()
		walkSleep(900)
		walkSend("s","Up")

		walkSend("d","Down")
		walkSleep(1000)
		walkSend("d","Up")

		walkSend("w","Down")
		walkSend("d","Down")
		jump()
		walkSleep(50)
		walkSend("w","Up")
		walkSleep(200)
		walkSend("d","Up")
		walkSend("s","Down")
		walkSend("d","Down")
		walkSleep(500)
		walkSleep(500)
		walkSend("s","Up")
		walkSend("d","Up")

		walkSend("d","Down")
		jump()
		walkSleep(350)
		walkSend("d","Up")

		jump()
		walkSend("s","Down")
		walkSleep(1700)
		walkSend("s","Up")

		walkSend("a","Down")
		walkSleep(800)
		walkSend("a","Up")
		walkSend("s","Down")
		walkSleep(300)
		walkSend("s","Up")

		walkSend("w","Down")
		walkSleep(300)
		walkSend("w","Up")
		walkSend("a","Down")
		walkSleep(800)
		jump()
		walkSleep(500)
		walkSend("a","Up")



		walkSend("w","Down")
		walkSleep(270)
		walkSend("w","Up")
		walkSend("a","Down")
		walkSleep(470)
		walkSend("a","Up")


		walkSend("a","Down")
		jump()
		walkSleep(100)
		walkSend("s","Down")
		walkSleep(500)
		walkSend("s","Up")
		walkSleep(100)
		walkSend("a","Up")
		sleep, 500
		walkSend("d","Down")
		walkSleep(1000)
		walkSend("d","Up")
		walkSend("s","Down")
		walkSleep(600)
		walkSend("s","Up")
		walkSleep(100)
		walkSend("a","Down")
		walkSleep(400)
		walkSend("a","Up")
		walkSleep(500)
		walkSend("s","Down")
		walkSleep(700)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(300)
		walkSend("d","Up")


		collect(8)

	} else {
		;tree obby
		walkSend("s","Down")
		walkSleep(1800)
		press("a",500)
		walkSend("s","Up")
		sleep, 400

		walkSend("d","Down")
		walkSleep(420)
		walkSend("d","Up")

		walkSend("s","Down")
		walkSleep(100)
		jump()
		walkSleep(550)
		jump()
		walkSleep(950)
		walkSend("s","Up")

		sleep, 500

		walkSend("s","Down")
		walkSend("a","Down")
		walkSleep(100)
		jump()
		walkSleep(500)
		jump()
		walkSleep(200)
		jump()
		walkSend("s","Up")
		walkSleep(200)
		jump()
		walkSend("s","Down")
		walkSleep(500)
		jump()
		walkSend("s","Up")
		walkSleep(300)
		jump()
		walkSleep(300)
		jump()
		walkSleep(600)
		walkSend("a","Up")

		;mountain obby

		walkSend("w","Down")
		walkSleep(400)
		jump()
		walkSleep(900)
		jump()
		walkSleep(800)
		walkSend("w","Up")

		press("s","200")
		walkSend("w","Down")
		walkSend("a","Down")
		walkSleep(300)
		jump()
		walkSleep(200)
		walkSend("a","Up")
		walkSend("d","Down")
		walkSleep(500)
		walkSend("d","Up")
		walkSleep(400)
		jump()

		walkSleep(800)
		walkSend("w","Up")
		walkSend("d","Down")
		walkSleep(800)
		walkSend("d","Up")

		walkSend("w","Down")
		jump()
		walkSleep(900)
		walkSend("w","Up")

		walkSend("a","Down")
		walkSleep(1000)
		walkSend("a","Up")

		walkSend("s","Down")
		walkSend("a","Down")
		jump()
		walkSleep(50)
		walkSend("s","Up")
		walkSleep(200)
		walkSend("a","Up")
		walkSend("w","Down")
		walkSend("a","Down")
		walkSleep(500)
		walkSleep(500)
		walkSend("w","Up")
		walkSend("a","Up")

		walkSend("a","Down")
		jump()
		walkSleep(350)
		walkSend("a","Up")

		jump()
		walkSend("w","Down")
		walkSleep(1700)
		walkSend("w","Up")

		walkSend("d","Down")
		walkSleep(800)
		walkSend("d","Up")
		walkSend("w","Down")
		walkSleep(300)
		walkSend("w","Up")

		walkSend("s","Down")
		walkSleep(300)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(800)
		jump()
		walkSleep(500)
		walkSend("d","Up")

		walkSend("s","Down")
		walkSleep(270)
		walkSend("s","Up")
		walkSend("d","Down")
		walkSleep(470)
		walkSend("d","Up")


		walkSend("d","Down")
		jump()
		walkSleep(100)
		walkSend("w","Down")
		walkSleep(500)
		walkSend("w","Up")
		walkSleep(100)
		walkSend("d","Up")
		sleep, 500
		walkSend("a","Down")
		walkSleep(1000)
		walkSend("a","Up")
		walkSend("w","Down")
		walkSleep(600)
		walkSend("w","Up")
		walkSleep(100)
		walkSend("d","Down")
		walkSleep(400)
		walkSend("d","Up")
		walkSleep(500)
		walkSend("w","Down")
		walkSleep(700)
		walkSend("w","Up")
		walkSend("a","Down")
		walkSleep(300)
		walkSend("a","Up")

		collect(8)
	}

}

if options["ItemSpot" . 1] or options["ItemSpot" . 2] {
	
	Spot1()
	
	if options["ItemSpot" . 2] {
	
		Spot2()
		
	}
	
	reset()
	Sleep, 1800
	
}

if options["ItemSpot" . 3] or options["ItemSpot" . 4] {
	
	Spot3()
	
	if options["ItemSpot" . 4] {
	
		Spot4()
		
	}
	
	reset()
	Sleep, 1800
	
}

if options["ItemSpot" . 5] or options["ItemSpot" . 6] or options["ItemSpot" . 7] or options["ItemSpot" . 8] {
	
	Spot5()
	
	if options["ItemSpot" . 6] or options["ItemSpot" . 7] or options["ItemSpot" . 8] {
	
		Spot6()

		if options["ItemSpot" . 7] or options["ItemSpot" . 8] {
		
			Spot7()

			if options["ItemSpot" . 8] and options.VIP {
			
				Spot8VIP()

			}
			
			if options["ItemSpot" . 8] and !options.VIP {
			
				Spot8()

			}

		}
	}
}