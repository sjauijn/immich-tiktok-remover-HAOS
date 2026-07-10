import time

import click

from .immich import (
    pingServer,
    getAllAssets,
    serveVideo,
    trashVideo,
    archiveVideo,
    getVideoAdditionalData,
)
from .verification import verifyVideoNameAndDate, processVideo


def run_once(domain, key, output_all, archive, search_archived,
             file_types_to_check_for, file_name_length, file_name_is_alumn,
             file_created_after):
    if not pingServer(domain, key):
        click.echo(click.style("Error while trying to connect to Immich. Check the server URL / API key.", fg="red"))
        return

    detected_tiktok_videos = 0
    no_tiktok_videos = 0
    total_tiktok_file_size = 0
    failed_videos = []

    start_time = time.time()

    click.echo("Getting all video files from Immich...")
    immich_videos = getAllAssets(domain, key, search_archived)

    click.echo("Processing videos. This may take a while... \n")
    if not output_all:
        click.echo("Note: Outputting only the filenames of videos detected as TikTok videos. Overridable with --output-all flag. \n")

    for video in immich_videos:
        video_id = video.get("id")
        matches = verifyVideoNameAndDate(
            video.get("originalFileName"),
            video.get("fileCreatedAt"),
            file_types_to_check_for,
            file_name_length,
            file_name_is_alumn,
            file_created_after,
        )

        if matches:
            try:
                is_tiktok = processVideo(serveVideo(domain, key, video_id))
            except Exception:
                is_tiktok = -1

            if is_tiktok == 1:
                video_data = getVideoAdditionalData(domain, key, video_id)
                file_size = 0
                if video_data:
                    exif = video_data.get("exifInfo") or {}
                    file_size = int(exif.get("fileSizeInByte") or 0)

                detected_tiktok_videos += 1
                total_tiktok_file_size += file_size

                name = (video_data or {}).get("originalFileName", video.get("originalFileName"))
                click.echo(f"{name} detected as a TikTok video.")

                if archive:
                    archiveVideo(domain, key, video_id)
                else:
                    trashVideo(domain, key, video_id)
                continue
            elif is_tiktok == 0 and output_all:
                click.echo(f"{video.get('originalFileName')} is not a TikTok video.")
            elif is_tiktok == -1:
                failed_videos.append(video.get("originalFileName"))
        no_tiktok_videos += 1

    total_tiktok_file_size_mb = total_tiktok_file_size / (1024 ** 2)
    click.echo(click.style(f"\nTotal videos: {detected_tiktok_videos + no_tiktok_videos}", fg="green"))
    click.echo(click.style(f"From those, {detected_tiktok_videos} were detected as TikTok videos and {no_tiktok_videos} were detected as non-TikTok videos.", fg="green"))
    click.echo(click.style(f"Total file size of TikTok videos: {total_tiktok_file_size_mb:.2f} MB.", fg="green"))

    if failed_videos:
        click.echo(click.style("\nThe following videos failed to process:", fg="red"))
        for name in failed_videos:
            click.echo(name)
        click.echo("You can trash/archive them manually or try running the script again.\n")

    elapsed_time = (time.time() - start_time) / 60
    click.echo(click.style("-" * 50, fg="green"))
    click.echo(click.style(f"Time taken: {elapsed_time:.0f} minutes", fg="green"))


@click.command()
@click.option("--key", help="Your Immich API Key", required=True)
@click.option("--server", help="Your Immich server URL", required=True)
@click.option("--output-all", is_flag=True, help="Output filenames of all videos, not just detected ones.")
@click.option("--archive", is_flag=True, help="Archive detected videos instead of trashing them.")
@click.option("--search-archived", is_flag=True, help="Also search already-archived videos.")
@click.option("--file-types", default="mp4", help="Comma separated list of file extensions to check.")
@click.option("--file-name-length", type=int, default=32, help="Expected filename length without extension. 0 disables the check.")
@click.option("--file-name-is-not-alumn", is_flag=True, help="Disable the alphanumeric-filename requirement.")
@click.option("--file-created-after", type=int, default=1472688000, help="Unix timestamp; only check videos created after this. 0 disables the check.")
@click.option("--verbose", is_flag=True, help="Enable verbose output for debugging")
@click.option("--run-every-seconds", type=int, default=0, show_default=True, help="Automatically rerun every N seconds (0 = run once).")
def tiktok_remover(
    key,
    server,
    output_all,
    archive,
    search_archived,
    file_types,
    file_name_length,
    file_name_is_not_alumn,
    file_created_after,
    verbose,
    run_every_seconds,
):
    domain = server if server.endswith("/") else server + "/"
    file_types_to_check_for = [t.strip() for t in file_types.split(",") if t.strip()]
    file_name_is_alumn = not file_name_is_not_alumn

    if run_every_seconds and run_every_seconds > 0:
        try:
            while True:
                run_once(domain, key, output_all, archive, search_archived,
                          file_types_to_check_for, file_name_length, file_name_is_alumn,
                          file_created_after)
                click.echo(f"Waiting {run_every_seconds} second(s) before next execution...")
                time.sleep(run_every_seconds)
        except KeyboardInterrupt:
            click.echo(click.style("Stop requested (Ctrl+C). Ending repeated execution.", fg="yellow"))
    else:
        run_once(domain, key, output_all, archive, search_archived,
                  file_types_to_check_for, file_name_length, file_name_is_alumn,
                  file_created_after)


def main(args=None):
    tiktok_remover()  # type: ignore[misc]


if __name__ == "__main__":
    tiktok_remover()  # type: ignore[misc]
