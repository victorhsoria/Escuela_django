Set shell = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
shell.Run Chr(34) & folder & "\INICIAR.bat" & Chr(34), 0, False
WScript.Sleep 1800
shell.Run "http://127.0.0.1:8000/"
