#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="$DIR/../environment/bundle"
DB="${1:-/work/rinzler.db}"
rinzler harbor init-db --bundle "$BUNDLE" --db "$DB"
python3 "$DIR/golden.py" --db "$DB" --config "$BUNDLE/config.toml" --target-completions 0 --prestige-floor 4.8985 --funds-hi-cents 169715587 --deadline-floor 0.9165
