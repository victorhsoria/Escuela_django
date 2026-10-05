$folder = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop "Programa Vida y Ministerio.lnk"))
$shortcut.TargetPath = (Join-Path $folder "INICIAR.vbs")
$shortcut.WorkingDirectory = $folder
$shortcut.Description = "Programa Vida y Ministerio"
$shortcut.Save()
