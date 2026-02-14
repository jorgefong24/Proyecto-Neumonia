param(
  [string]$Display = "host.docker.internal:0.0",
  [string]$DicomDir = "DICOM"
)

# Resolve host paths
$pwdStr = ${PWD}.Path

if ([System.IO.Path]::IsPathRooted($DicomDir)) {
  $dicomFull = $DicomDir
} else {
  $dicomFull = Join-Path $pwdStr $DicomDir
}

if (-not (Test-Path $dicomFull)) {
  Write-Error "DICOM directory not found: $dicomFull"
  exit 1
}

# Validate X server reachability on Windows host (DISPLAY :N -> TCP 6000+N)
$displayNumber = 0
if ($Display -match ":(\d+)(?:\.\d+)?$") {
  $displayNumber = [int]$matches[1]
}
$x11Port = 6000 + $displayNumber
$x11Test = Test-NetConnection -ComputerName "127.0.0.1" -Port $x11Port -WarningAction SilentlyContinue
if (-not $x11Test.TcpTestSucceeded) {
  Write-Error "No X server listening on localhost:$x11Port for DISPLAY '$Display'. Start VcXsrv/XLaunch with TCP enabled and Disable access control, then retry."
  exit 1
}

# Detect common incompatible X server (Xming) that causes Qt6/XInput issues.
$listenConn = Get-NetTCPConnection -LocalPort $x11Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listenConn) {
  try {
    $owner = Get-Process -Id $listenConn.OwningProcess -ErrorAction Stop
    if ($owner.ProcessName -ieq "Xming") {
      Write-Error "DISPLAY '$Display' is currently served by Xming (PID $($owner.Id)). Qt6 in container usually fails with Xming. Close Xming and run VcXsrv, then retry."
      exit 1
    }
  } catch {
    # If process lookup fails, continue; docker run may still work.
  }
}

docker run --rm `
  -e RUN_GUI=1 `
  -e DISPLAY=$Display `
  -e QT_QPA_PLATFORM=xcb `
  -e QT_XCB_NO_XI2=1 `
  -e QT_X11_NO_MITSHM=1 `
  -e QT_OPENGL=software `
  -e LIBGL_ALWAYS_SOFTWARE=1 `
  -e LIBGL_ALWAYS_INDIRECT=1 `
  -e NO_AT_BRIDGE=1 `
  -v "${pwdStr}:/project" `
  -v "${dicomFull}:/data" `
  -w /project `
  proyecto-neumonia:gui `
  python -m src.models.detector_neumonia
