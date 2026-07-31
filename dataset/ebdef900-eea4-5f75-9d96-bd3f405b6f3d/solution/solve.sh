#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$DIR/../environment/bundle"
DB="${1:-/work/rinzler.db}"
rinzler harbor init-db --bundle "$BUNDLE" --db "$DB"
python3 "$DIR/golden.py" --db "$DB" --config "$BUNDLE/config.toml" --target-completions 0 --prestige-floor 4.8956 --funds-hi-cents 297762184 --deadline-floor 0.9536
