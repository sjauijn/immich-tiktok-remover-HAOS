<p align="center">
  <img src="https://raw.githubusercontent.com/sjauijn/immich-tiktok-remover-HAOS/main/icon.png" alt="icon">
</p>

# Immich TikTok Remover

I maintain this app, along with my other Home Assistant apps, solely for my own use. As long as I'm actively using them myself, I'll continue developing and updating them; otherwise, support for apps I no longer need will be discontinued.

## Quick Start

1. Open the **Configuration** tab of the add-on and fill in one entry under **Scan jobs**:
   - `immich_url` — your Immich server URL (with scheme and port)
   - `api_key` — an API key generated on that Immich account
2. Save the configuration, then start the add-on.
3. Check the **Log** tab to see detected TikTok videos and results.

By default the add-on runs once, processes matching videos, then repeats every `run_every_seconds` (3600s / 1 hour). Set `run_every_seconds` to `0` if you'd rather trigger a single scan from a Home Assistant automation instead of running it continuously.

## How detection works (stable-lite)

A video is flagged as a TikTok export if it matches all enabled heuristics:

- File extension is one of `file_types` (default `mp4`)
- Filename (without extension) length equals `file_name_length` (default `32`, TikTok's typical export length) — set to `0` to disable
- Filename (without extension) is purely alphanumeric, unless `file_name_is_not_alumn` is enabled
- Video creation date is after `file_created_after` (unix timestamp, default `1472688000` = Sept 1, 2016) — set to `0` to disable

Once a video matches, it is trashed (default) or archived (`archive: true`).

## Configuration Options

Two global options apply to every job:

| Option | Default | Description |
|--------|---------|--------------|
| `run_every_seconds` | `3600` | How often to re-run **all** jobs, in seconds. `0` runs once and exits. |
| `verbose` | `false` | Print detailed API calls for every job. |

Each entry under `jobs` scans one Immich account:

| Option | Required | Default | Description |
|--------|----------|---------|--------------|
| `immich_url` | Yes | — | Immich server URL, with scheme and port. |
| `api_key` | Yes | — | API key generated on this Immich account. |
| `output_all` | No | `false` | Log every checked video, not just detected TikTok ones. |
| `archive` | No | `false` | Archive detected videos instead of trashing them. |
| `search_archived` | No | `false` | Also scan already-archived videos. |
| `file_types` | No | `mp4` | Comma separated list of extensions to check. |
| `file_name_length` | No | `32` | Expected filename length without extension. `0` disables the check. |
| `file_name_is_not_alumn` | No | `false` | Disable the alphanumeric filename requirement. |
| `file_created_after` | No | `1472688000` | Unix timestamp; only checks videos created after this. `0` disables the check. |

A job with a missing `immich_url` or `api_key` is skipped (with a warning in the log) rather than stopping the other jobs.

### Multiple jobs

`jobs` is a list, so a single add-on instance can scan several Immich accounts/servers. Click **Add** under **Scan jobs** in the Configuration tab to add another entry.

## Note on the ML variant

Upstream also ships a `stable` image that adds EasyOCR-based watermark image recognition (~4.1GB) for higher accuracy on videos whose filenames don't match TikTok's pattern. That path is not included in this add-on; only the lightweight, filename/date-based `stable-lite` logic is ported.
