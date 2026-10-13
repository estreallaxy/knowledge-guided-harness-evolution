#!/usr/bin/env bash
# Get the official-code snapshot of this source package. A network is required. Execute in the root directory of the repository:
#   bash knowledge/source-packets/agent-skill-induction-2504.06821/vendor-official-code.sh
set -euo pipefail

REV="377abe0623a37eaf7f03bdd26cb97bb5331acf47"
REPO="https://github.com/zorazrw/agent-skill-induction.git"
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/official-code"

if [ -e "$DEST" ]; then
echo "!! $DEST already exists. To avoid overwriting, please manually confirm and process." >&2
  exit 1
fi

tmp="$(mktemp -d)"
git clone --quiet "$REPO" "$tmp/upstream"
git -C "$tmp/upstream" checkout --quiet "$REV"

mkdir -p "$DEST"
cp -a "$tmp/upstream/." "$DEST/"
rm -rf "$DEST/.git"
rm -rf "$tmp"

echo "==> Written to $DEST"
echo "==> Please check: license file, entrypoint, dependency list, and backfill source-packet.json"
echo "    official_code_version.retrieved_on / upstream_revision_date / snapshot_scope / license_status"
