#!/usr/bin/env bash
# simple wrapper to run the report pipeline from the minimal project folder
# usage: ./run_report.sh [--month YYYY-MM] [--skip-fetch] [--no-send]

set -euo pipefail
cd "$(dirname "$0")"

# load .env if present
if [ -f .env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source .env
  set +o allexport
fi

PYTHON="../.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  echo "warning: python not found at $PYTHON; trying system python"
  PYTHON="python"
fi

# default month: last month
DEFAULT_MONTH=$(date --date='last month' +%Y-%m)
MONTH="$DEFAULT_MONTH"
SKIP_FETCH=""
NO_SEND=0

# parse args (simple)
while [ "$#" -gt 0 ]; do
  case "$1" in
    --month)
      MONTH="$2"; shift 2;;
    --skip-fetch)
      SKIP_FETCH="--skip-fetch"; shift;;
    --no-send)
      NO_SEND=1; shift;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

CMD=("$PYTHON" -m ks_reporter.scripts.run_report_pipeline --month "$MONTH")
if [ -n "$SKIP_FETCH" ]; then CMD+=("$SKIP_FETCH"); fi
if [ "$NO_SEND" -eq 1 ]; then
  CMD+=("--target-user" "0" "--channel-id" "");
fi

echo "Running: ${CMD[*]}"
"${CMD[@]}"
