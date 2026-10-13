#!/usr/bin/env bash
# 取得本来源包的 official-code 快照。需要网络，在仓库根目录执行：
#   bash knowledge/source-packets/agent-skill-induction-2504.06821/vendor-official-code.sh
set -euo pipefail

REV="377abe0623a37eaf7f03bdd26cb97bb5331acf47"
REPO="https://github.com/zorazrw/agent-skill-induction.git"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/official-code"

if [ -e "$DEST" ]; then
  echo "!! $DEST 已存在，避免覆盖，请人工确认后处理。" >&2
  exit 1
fi

tmp="$(mktemp -d)"
git clone --quiet "$REPO" "$tmp/upstream"
git -C "$tmp/upstream" checkout --quiet "$REV"

mkdir -p "$DEST"
cp -a "$tmp/upstream/." "$DEST/"
rm -rf "$DEST/.git"
rm -rf "$tmp"

echo "==> 已写入 $DEST"
echo "==> 请核对：许可证文件、entrypoint、依赖清单，并回填 source-packet.json 的"
echo "    official_code_version.retrieved_on / upstream_revision_date / snapshot_scope / license_status"
