#!/usr/bin/env bash
# Usage: ./run_cli.sh [image_path] [model_path] [out_dir] [dicom_dir]
IMAGE_PATH=${1:-normal.dcm}
MODEL_PATH=${2:-conv_MLP_84.h5}
OUT_DIR=${3:-out}
DICOM_DIR=${4:-DICOM}

PWD_DIR="$(pwd)"

# Resolve absolute DICOM dir if relative
if [ -d "${DICOM_DIR}" ]; then
  DICOM_FULL="${PWD_DIR}/${DICOM_DIR}"
else
  # if user passed an absolute path, use it; otherwise default to ${PWD}/DICOM
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

# Mount DICOM to /data and project to /project. Model path is relative to project.
docker run --rm \
  -v "${DICOM_FULL}:/data" \
  -v "${PWD_DIR}:/project" \
  -w /data \
  proyecto-neumonia:latest \
  python /app/cli.py --image /data/${IMAGE_PATH} --model /project/${MODEL_PATH} --out /data/${OUT_DIR}
