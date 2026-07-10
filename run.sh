#!/usr/bin/with-contenv bashio

OPTIONS_FILE="/data/options.json"

RUN_EVERY_SECONDS="$(bashio::config 'run_every_seconds')"
VERBOSE="$(bashio::config 'verbose')"
JOB_COUNT="$(jq '.jobs | length' "${OPTIONS_FILE}")"

VERBOSE_FLAG=""
if [ "${VERBOSE}" = "true" ]; then
  VERBOSE_FLAG="--verbose"
fi

run_job() {
  local idx="$1"
  local job
  job="$(jq -c ".jobs[${idx}]" "${OPTIONS_FILE}")"

  local immich_url api_key output_all archive search_archived file_types
  local file_name_length file_name_is_not_alumn file_created_after
  immich_url="$(echo "${job}" | jq -r '.immich_url')"
  api_key="$(echo "${job}" | jq -r '.api_key')"
  output_all="$(echo "${job}" | jq -r '.output_all')"
  archive="$(echo "${job}" | jq -r '.archive')"
  search_archived="$(echo "${job}" | jq -r '.search_archived')"
  file_types="$(echo "${job}" | jq -r '(.file_types // ["mp4"]) | join(",")')"
  file_name_length="$(echo "${job}" | jq -r '.file_name_length // 32')"
  file_name_is_not_alumn="$(echo "${job}" | jq -r '.file_name_is_not_alumn')"
  file_created_after="$(echo "${job}" | jq -r '.file_created_after // 1472688000')"

  if [ -z "${immich_url}" ] || [ "${immich_url}" = "null" ] || \
     [ -z "${api_key}" ] || [ "${api_key}" = "null" ]; then
    bashio::log.warning "Job ${idx}: skipped, missing immich_url / api_key"
    return 0
  fi

  local -a bool_args=()
  [ "${output_all}" = "true" ] && bool_args+=(--output-all)
  [ "${archive}" = "true" ] && bool_args+=(--archive)
  [ "${search_archived}" = "true" ] && bool_args+=(--search-archived)
  [ "${file_name_is_not_alumn}" = "true" ] && bool_args+=(--file-name-is-not-alumn)

  bashio::log.info "Job ${idx}: scanning ${immich_url} for TikTok videos (stable-lite, filename/date only)"

  python3 -m immich_tiktok_remover \
    --key "${api_key}" \
    --server "${immich_url}" \
    --file-types "${file_types}" \
    --file-name-length "${file_name_length}" \
    --file-created-after "${file_created_after}" \
    "${bool_args[@]}" \
    ${VERBOSE_FLAG}
}

bashio::log.info "Starting immich-tiktok-remover (stable-lite) with ${JOB_COUNT} job(s)"

while true; do
  for ((i = 0; i < JOB_COUNT; i++)); do
    run_job "${i}"
  done

  if [ -z "${RUN_EVERY_SECONDS}" ] || [ "${RUN_EVERY_SECONDS}" -le 0 ]; then
    bashio::log.info "run_every_seconds <= 0, exiting after single pass"
    break
  fi

  bashio::log.info "Sleeping ${RUN_EVERY_SECONDS}s before next pass"
  sleep "${RUN_EVERY_SECONDS}"
done
