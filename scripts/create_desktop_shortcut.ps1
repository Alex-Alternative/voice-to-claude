param(
    [string]$KodaDir = (Split-Path -Parent $PSScriptRoot)
)

# Prefer the Public desktop (C:\Users\Public\Desktop) — it's not OneDrive-synced,
# so the shortcut won't get a blue sync-status overlay. Falls back to the user's
# personal desktop (which may be OneDrive-managed) if Public isn't writable.
$publicDesktop = Join-Path $env:PUBLIC 'Desktop'
$userDesktop = [Environment]::GetFolderPath('Desktop')

try {
    $null = [IO.File]::Create((Join-Path $publicDesktop '.koda_write_test')).Close()
    Remove-Item (Join-Path $publicDesktop '.koda_write_test') -Force -ErrorAction SilentlyContinue
    $desktop = $publicDesktop
} catch {
    $desktop = $userDesktop
}

# Clean up any prior shortcut on the OneDrive/user desktop so we don't show two
if ($desktop -ne $userDesktop) {
    $staleUserShortcut = Join-Path $userDesktop 'Koda.lnk'
    if (Test-Path $staleUserShortcut) {
        Remove-Item $staleUserShortcut -Force -ErrorAction SilentlyContinue
    }
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut((Join-Path $desktop 'Koda.lnk'))
$shortcut.TargetPath = (Join-Path $KodaDir 'start.bat')
$shortcut.WorkingDirectory = $KodaDir
$shortcut.IconLocation = (Join-Path $KodaDir 'koda.ico') + ',0'
$shortcut.WindowStyle = 7
$shortcut.Description = 'Koda - push-to-talk voice transcription'
$shortcut.Save()

Write-Host "Desktop shortcut created at: $desktop\Koda.lnk"
