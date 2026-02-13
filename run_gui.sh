#!/usr/bin/env bash
# Usage: ./run_gui.sh [display] [dicom_dir]
DISPLAY_ENV=${1:-${DISPLAY:-:0}}
DICOM_DIR=${2:-DICOM}

PWD_DIR="$(pwd)"

if [ -d "${DICOM_DIR}" ]; then
  DICOM_FULL="${PWD_DIR}/${DICOM_DIR}"
else
  if [[ "${DICOM_DIR}" = /* ]]; then
    DICOM_FULL="${DICOM_DIR}"
  else
    DICOM_FULL="${PWD_DIR}/${DICOM_DIR}"
  fi
fi

if [ ! -d "${DICOM_FULL}" ]; then
  echo "DICOM directory not found: ${DICOM_FULL}" >&2
  exit 1
fi

docker run --rm \
  -e RUN_GUI=1 \
  -e DISPLAY=${DISPLAY_ENV} \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "${PWD_DIR}:/project" \
  -v "${DICOM_FULL}:/data" \
  -w /project \
  proyecto-neumonia:gui \
  python -m src.models.detector_neumonia
