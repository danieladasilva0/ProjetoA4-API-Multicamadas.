#!/usr/bin/env bash
set -euo pipefail

uv run --no-sync uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8000 \
  --proxy-headers --forwarded-allow-ips='*' &
api_pid=$!
nginx_conf="$(mktemp)"

cleanup() {
  kill "$api_pid" 2>/dev/null || true
  rm -f "$nginx_conf"
}
trap cleanup EXIT INT TERM

sed -e 's/listen 80;/listen 5000;/' \
    -e 's#http://api:8000#http://127.0.0.1:8000#' \
    nginx/nginx.conf > "$nginx_conf"

for _ in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 1
done

nginx -e stderr -g 'daemon off;' -c "$nginx_conf"
