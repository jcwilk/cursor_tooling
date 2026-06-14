#!/usr/bin/env bash
# Instrumented sleuth reset+refresh probe using pi-run fleet env and scratch layout.
set -euo pipefail

HOME_AI_ROOT="${PI_RUN_REPO_ROOT:-/home/user/workspace/home_ai}"
WORKTREE="${SLEUTH_PROJECT_ROOT:-/home/user/.cursor/worktrees/cursor_tooling/801f}"
SLEUTH_ID="${SLEUTH_ID:-tooling}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
ARTIFACT_DIR="${HOME_AI_ROOT}/.pi-run/scratch/sleuth-refresh-debug-${RUN_ID}"
SLEUTH_BIN="${WORKTREE}/.venv/bin/sleuth"
RPC_ENV="${HOME_AI_ROOT}/ansible/pi-agent-rpc.env"

mkdir -p "${ARTIFACT_DIR}"

log() { echo "[$(date -Iseconds)] $*" | tee -a "${ARTIFACT_DIR}/harness.log"; }

log "artifact_dir=${ARTIFACT_DIR}"
log "worktree=${WORKTREE} sleuth=${SLEUTH_ID}"

if [[ ! -x "${SLEUTH_BIN}" ]]; then
  log "building sleuth..."
  (cd "${WORKTREE}" && scripts/build-local-tools.sh) >> "${ARTIFACT_DIR}/build.log" 2>&1
fi

log "inference snapshot (before)"
(
  cd "${HOME_AI_ROOT}"
  ./tools/debug/inference-snapshot --dry-run
) > "${ARTIFACT_DIR}/inference-snapshot-before.yaml" 2>> "${ARTIFACT_DIR}/harness.log" || true

log "starting alienware log tail"
ssh -o BatchMode=yes user@192.168.1.110 \
  "journalctl -u llama-swap.service -u inference-gateway.service -f --no-pager -o short-iso" \
  > "${ARTIFACT_DIR}/alienware-journal.log" 2>&1 &
JOURNAL_PID=$!

cleanup() {
  kill "${JOURNAL_PID}" 2>/dev/null || true
  wait "${JOURNAL_PID}" 2>/dev/null || true
}
trap cleanup EXIT

log "pi-run rpc env profile: ${RPC_ENV}"
grep -E '^(PI_AGENT_TEXT_BASE_URL|PI_AGENT_TEXT_MODEL)=' "${RPC_ENV}" \
  | tee "${ARTIFACT_DIR}/inference-env.txt"

log "reset ${SLEUTH_ID}"
RESET_START=$(date +%s.%N)
"${SLEUTH_BIN}" --project-root "${WORKTREE}" reset --sleuth "${SLEUTH_ID}" \
  2> >(tee -a "${ARTIFACT_DIR}/sleuth-reset.log" >&2)
RESET_END=$(date +%s.%N)
printf 'reset_elapsed_sec=%.3f\n' "$(echo "${RESET_END} - ${RESET_START}" | bc)" \
  | tee "${ARTIFACT_DIR}/timing.txt"

log "refresh ${SLEUTH_ID}"
REFRESH_START=$(date +%s.%N)
set +e
"${SLEUTH_BIN}" --project-root "${WORKTREE}" refresh --sleuth "${SLEUTH_ID}" \
  2> >(tee -a "${ARTIFACT_DIR}/sleuth-refresh.log" >&1)
REFRESH_EXIT=$?
set -e
REFRESH_END=$(date +%s.%N)
{
  printf 'refresh_exit=%s\n' "${REFRESH_EXIT}"
  printf 'refresh_elapsed_sec=%.1f\n' "$(echo "${REFRESH_END} - ${REFRESH_START}" | bc)"
  printf 'refresh_elapsed_min=%.1f\n' "$(echo "(${REFRESH_END} - ${REFRESH_START}) / 60" | bc -l)"
} | tee -a "${ARTIFACT_DIR}/timing.txt"

log "inference snapshot (after)"
(
  cd "${HOME_AI_ROOT}"
  ./tools/debug/inference-snapshot --dry-run
) > "${ARTIFACT_DIR}/inference-snapshot-after.yaml" 2>> "${ARTIFACT_DIR}/harness.log" || true

log "summarize inference calls from sleuth log"
grep -E 'inference calls this refresh:' "${ARTIFACT_DIR}/sleuth-refresh.log" \
  | tee "${ARTIFACT_DIR}/inference-calls.txt" \
  | awk '{
      match($0, /inference calls this refresh: ([0-9]+)/, a)
      if (a[1] != "") printf "inference_calls_total=%s\n", a[1]
    }' >> "${ARTIFACT_DIR}/timing.txt" || true

log "summarize segments"
grep -E 'processing [0-9]+ segment' "${ARTIFACT_DIR}/sleuth-refresh.log" \
  | tee "${ARTIFACT_DIR}/segments.txt" || true

log "done refresh_exit=${REFRESH_EXIT} artifacts=${ARTIFACT_DIR}"
exit "${REFRESH_EXIT}"
