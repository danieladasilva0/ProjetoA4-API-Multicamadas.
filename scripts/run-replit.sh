#!/usr/bin/env bash
set -euo pipefail

api_pid=""
nginx_conf="$(mktemp)"
nginx_pid_file="$(mktemp)"
nginx_pid=""
rm -f "$nginx_pid_file"

cleanup() {
  local exit_code=$?
  trap - EXIT INT TERM
  if [[ -n "$nginx_conf" && -n "$nginx_pid_file" ]]; then
    nginx -s quit -c "$nginx_conf" 2>/dev/null || true
  fi
  if [[ -n "$nginx_pid" ]]; then
    kill "$nginx_pid" 2>/dev/null || true
    wait "$nginx_pid" 2>/dev/null || true
  fi
  if [[ -n "$api_pid" ]]; then
    stop_process_tree "$api_pid"
    wait "$api_pid" 2>/dev/null || true
  fi
  rm -f "$nginx_pid_file"
  rm -f "$nginx_conf"
  exit "$exit_code"
}

stop_process_tree() {
  local parent="$1"
  local child
  for child in $(pgrep -P "$parent" 2>/dev/null || true); do
    stop_process_tree "$child"
  done
  kill "$parent" 2>/dev/null || true
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

uv run --no-sync uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8000 \
  --proxy-headers --forwarded-allow-ips='*' &
api_pid=$!

sed -e 's/listen 80;/listen 5000;/' \
    -e 's#http://api:8000#http://127.0.0.1:8000#' \
    -e "s#pid /tmp/nginx.pid;#pid ${nginx_pid_file};#" \
    nginx/nginx.conf > "$nginx_conf"

nginx -e stderr -t -c "$nginx_conf"

api_ready=false
for _ in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:8000/health >/dev/null; then
    api_ready=true
    break
  fi
  sleep 1
done

if [[ "$api_ready" != true ]]; then
  echo "A API não iniciou na porta 8000." >&2
  exit 1
fi

nginx -e stderr -g 'daemon off;' -c "$nginx_conf" &
nginx_pid=$!

nginx_ready=false
for _ in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:5000/health >/dev/null; then
    nginx_ready=true
    break
  fi
  sleep 1
done

if [[ "$nginx_ready" != true ]]; then
  echo "O Nginx não iniciou na porta 5000." >&2
  exit 1
fi

wait "$nginx_pid"
