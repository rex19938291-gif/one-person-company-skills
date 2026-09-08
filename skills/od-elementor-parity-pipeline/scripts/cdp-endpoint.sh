#!/bin/zsh
# Shared headless-Chrome CDP endpoint for sandboxed executors (Codex subagents,
# GLM, any API model) that cannot spawn Chrome themselves (symptoms: "invalid
# code signature", MachPort permission errors).
#
# Start this OUTSIDE the sandbox, then run any harness with:
# --cdp-url http://127.0.0.1:9223 (qa-measure.mjs also reads QA_CDP_URL,
# qa-reference-parity.mjs reads C 客戶_QA_CDP_URL)
#
# Binds to 127.0.0.1 only. Harnesses create/close their own tabs and must
# never kill this browser; stop it here when the measuring round is done.
#
# Usage: cdp-endpoint.sh start|stop|status (CDP_PORT env overrides, default 9223)
set -u
PORT="${CDP_PORT:-9223}"
DIR="/tmp/cdp-shared-${PORT}"
PIDFILE="${DIR}/chrome.pid"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

case "${1:-status}" in
 start)
 if curl -s "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
 echo "already running: http://127.0.0.1:${PORT}"
 exit 0
 fi
 mkdir -p "$DIR"
 nohup "$CHROME" \
 --headless=new \
 --remote-debugging-port="$PORT" \
 --disable-gpu --hide-scrollbars \
 --allow-file-access-from-files \
 --user-data-dir="$DIR/profile" \
 --no-first-run about:blank \
 >"$DIR/chrome.log" 2>&1 &
 echo $! > "$PIDFILE"
 for i in {1..50}; do
 if curl -s "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
 echo "CDP endpoint ready: http://127.0.0.1:${PORT}"
 exit 0
 fi
 sleep 0.2
 done
 echo "failed to start; see $DIR/chrome.log" >&2
 exit 1
 ;;
 stop)
 [ -f "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null
 pkill -f "remote-debugging-port=${PORT}" 2>/dev/null
 rm -rf "$DIR"
 echo "stopped"
 ;;
 status)
 if curl -s "http://127.0.0.1:${PORT}/json/version"; then
 echo
 else
 echo "not running (port ${PORT})"
 exit 1
 fi
 ;;
 *)
 echo "usage: cdp-endpoint.sh start|stop|status (CDP_PORT env, default 9223)" >&2
 exit 64
 ;;
esac
