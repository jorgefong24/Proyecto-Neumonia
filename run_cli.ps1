param(
  [string]$ImagePath = "normal.dcm",
  [string]$ModelPath = "conv_MLP_84.h5",
  [string]$OutDir = "out",
  [string]$DicomDir = "DICOM"
)

# Current working directory (host)
$pwdStr = ${PWD}.Path

# Resolve DICOM directory (absolute or relative to cwd)
if ([System.IO.Path]::IsPathRooted($DicomDir)) {
  $dicomFull = $DicomDir
} else {
  $dicomFull = Join-Path $pwdStr $DicomDir
}

if (-not (Test-Path $dicomFull)) {
  Write-Error "DICOM directory not found: $dicomFull"
  exit 1
}

# In-container paths
$containerImagePath = "/data/$ImagePath"
$containerModelPath = "/project/$ModelPath"

docker run --rm `
  -v "${dicomFull}:/data" `
  -v "${pwdStr}:/project" `
  -w /data `
  proyecto-neumonia:latest `
  python /app/cli.py --image $containerImagePath --model $containerModelPath --out /data/$OutDir
