param(
  [string]$Display = "host.docker.internal:0",
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

docker run --rm `
  -e RUN_GUI=1 `
  -e DISPLAY=$Display `
  -v "${pwdStr}:/project" `
  -v "${dicomFull}:/data" `
  -v /tmp/.X11-unix:/tmp/.X11-unix `
  -w /project `
  proyecto-neumonia:gui `
  python -m src.models.detector_neumonia
