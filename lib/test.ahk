#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

hwnd := WinExist("Roblox")
OutputDebug, % hwnd
DllCall("SetWindowPos",UInt,hwnd,Int,0,Int,100,Int,100,Int,200,Int,200,UInt,0x416)