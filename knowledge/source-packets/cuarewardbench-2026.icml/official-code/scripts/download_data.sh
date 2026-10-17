#!/usr/bin/env bash
set -euo pipefail

# Download public trajectory archives, normalize them to the CUARewardBench layout,
# verify against data/manifest.jsonl, and materialize a real benchmark directory
# at data/trajectories/osworld_verified.
#
# By default the bulky download/preprocess cache lives outside the repository in
# a sibling directory so a fresh git clone stays lightweight.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

WORKSPACE="${WORKSPACE:-${REPO_ROOT}/../data_build_workspace}"
ARCHIVE_CONFIG="${ARCHIVE_CONFIG:-${WORKSPACE}/source_archives.json}"
RAW_ARCHIVES="${RAW_ARCHIVES:-${WORKSPACE}/raw_archives}"
RAW_EXTRACTED="${RAW_EXTRACTED:-${WORKSPACE}/raw_extracted}"
OUTPUT_ROOT="${OUTPUT_ROOT:-${WORKSPACE}/prepared/osworld_verified}"
BENCHMARK_ROOT="${BENCHMARK_ROOT:-${REPO_ROOT}/data/trajectories/osworld_verified}"
ONLY_MODEL_SETTING="${ONLY_MODEL_SETTING:-}"
SKIP_DOWNLOAD="${SKIP_DOWNLOAD:-0}"
SKIP_EXTRACT="${SKIP_EXTRACT:-0}"
DOWNLOAD_ONLY="${DOWNLOAD_ONLY:-0}"
CLEAN_OUTPUT="${CLEAN_OUTPUT:-1}"
VERIFY_CHECKSUM="${VERIFY_CHECKSUM:-1}"
INSTALL_TO_REPO="${INSTALL_TO_REPO:-1}"

mkdir -p "${RAW_ARCHIVES}" "${RAW_EXTRACTED}" "${OUTPUT_ROOT}" "${WORKSPACE}/logs"

if [[ ! -f "${ARCHIVE_CONFIG}" ]]; then
  echo "[ERROR] archive config not found: ${ARCHIVE_CONFIG}" >&2
  exit 2
fi

mapfile -t ARCHIVES < <(python3 - "${ARCHIVE_CONFIG}" "${ONLY_MODEL_SETTING}" <<'PY'
import json, os, sys
path, only = sys.argv[1], sys.argv[2]
items = json.load(open(path, encoding="utf-8"))
for item in items:
    if item.get("unused_in_cuarewardbench_v0_4"):
        continue
    if only and item["model_setting"] != only:
        continue
    url = item["url"]
    filename = item.get("filename") or url.rsplit("/", 1)[-1].split("?", 1)[0]
    print("\t".join([item["model_setting"], url, filename]))
PY
)

if [[ "${#ARCHIVES[@]}" -eq 0 ]]; then
  echo "[ERROR] no archives selected. ONLY_MODEL_SETTING=${ONLY_MODEL_SETTING}" >&2
  exit 2
fi

echo "[INFO] selected archives: ${#ARCHIVES[@]}"

if [[ "${SKIP_DOWNLOAD}" != "1" ]]; then
  for row in "${ARCHIVES[@]}"; do
    IFS=$'\t' read -r model_setting url filename <<< "${row}"
    dest="${RAW_ARCHIVES}/${filename}"
    echo "[INFO] downloading ${model_setting}: ${url}"
    if command -v wget >/dev/null 2>&1; then
      wget -c -O "${dest}" "${url}"
    elif command -v curl >/dev/null 2>&1; then
      curl -L --fail --continue-at - --output "${dest}" "${url}"
    else
      echo "[ERROR] neither wget nor curl is available" >&2
      exit 2
    fi
  done
else
  echo "[INFO] SKIP_DOWNLOAD=1; reuse archives in ${RAW_ARCHIVES}"
fi

if [[ "${DOWNLOAD_ONLY}" == "1" ]]; then
  echo "[OK] DOWNLOAD_ONLY=1; stop after download."
  exit 0
fi

if [[ "${SKIP_EXTRACT}" != "1" ]]; then
  if ! command -v unzip >/dev/null 2>&1; then
    echo "[ERROR] unzip is required to extract trajectory archives" >&2
    exit 2
  fi
  for row in "${ARCHIVES[@]}"; do
    IFS=$'\t' read -r model_setting _url filename <<< "${row}"
    archive="${RAW_ARCHIVES}/${filename}"
    extract_dir="${RAW_EXTRACTED}/${model_setting}"
    if [[ ! -f "${archive}" ]]; then
      echo "[ERROR] archive missing: ${archive}" >&2
      exit 2
    fi
    echo "[INFO] extracting ${archive} -> ${extract_dir}"
    rm -rf "${extract_dir}"
    mkdir -p "${extract_dir}"
    unzip -q "${archive}" -d "${extract_dir}"
  done
else
  echo "[INFO] SKIP_EXTRACT=1; reuse extracted files in ${RAW_EXTRACTED}"
fi

PREPARE_ARGS=(
  --raw_root "${RAW_EXTRACTED}"
  --output_root "${OUTPUT_ROOT}"
  --manifest data/manifest.jsonl
  --annotation_file data/annotations/cuarewardbench-v0.4.json
)
if [[ "${CLEAN_OUTPUT}" == "1" ]]; then
  PREPARE_ARGS+=(--clean)
fi

echo "[INFO] normalizing downloaded trajectories -> ${OUTPUT_ROOT}"
python3 scripts/prepare_downloaded_trajs.py "${PREPARE_ARGS[@]}"

echo "[INFO] verifying size-only first"
python3 scripts/verify_data.py --trajectory_root "${OUTPUT_ROOT}" --no-checksum

if [[ "${VERIFY_CHECKSUM}" == "1" ]]; then
  echo "[INFO] verifying sha256"
  python3 scripts/verify_data.py --trajectory_root "${OUTPUT_ROOT}"
else
  echo "[INFO] VERIFY_CHECKSUM=0; skipped sha256 verification"
fi

echo "[OK] workspace cache is ready at: ${OUTPUT_ROOT}"

if [[ "${INSTALL_TO_REPO}" == "1" ]]; then
  echo "[INFO] materializing verified benchmark tree -> ${BENCHMARK_ROOT}"
  rm -rf "${BENCHMARK_ROOT}"
  mkdir -p "$(dirname "${BENCHMARK_ROOT}")"
  cp -a "${OUTPUT_ROOT}" "${BENCHMARK_ROOT}"
  echo "[OK] benchmark data is ready at: ${BENCHMARK_ROOT}"
else
  echo "[INFO] INSTALL_TO_REPO=0; skipped copying verified tree into repository layout."
fi
