' This vbs script is adopted from the following source:
' Source: https://www.robvanderwoude.com/sourcecode.php?src=runnhide_vbs

Option Explicit

Dim i, strArguments, wshShell

If WScript.Arguments.Count = 0 Then Syntax
If WScript.Arguments(0) = "/?" Then Syntax

strArguments = ""

For i = 0 To WScript.Arguments.Count - 1
	strArguments = strArguments & " " & WScript.Arguments(i)
Next

Set wshShell = CreateObject( "WScript.Shell" )
wshShell.Run Trim( strArguments ), 0, False
Set wshShell = Nothing


Sub Syntax
	Dim strMsg
	strMsg = "RunNHide.vbs,  Version 2.00" & vbCrLf _
	       & "Run a batch file or (console) command in a hidden window" & vbCrLf _
	       & vbCrLf _
	       & "Usage:  RUNNHIDE.VBS  some_command  [ some_arguments ]" & vbCrLf _
	       & vbCrLf _
	       & "Where:  ""some_command""    is the batch file or (console) command" & vbCrLf _
	       & "                          you want to run hidden" & vbCrLf _
	       & "        ""some_arguments""  are optional arguments for ""some_command""" & vbCrLf _
	       & vbCrLf _
	       & "Based on a ""one-liner"" by Alistair Johnson" & vbCrLf _
	       & "www.microsoft.com/technet/scriptcenter/csc/scripts/scripts/running/cscte009.mspx" _
	       & vbCrLf & vbCrLf _
	       & "Written by Rob van der Woude" & vbCrLf _
	       & "http://www.robvanderwoude.com"
	WScript.Echo strMsg
	WScript.Quit 1
End Sub
