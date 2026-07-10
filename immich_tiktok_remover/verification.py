"""
stable-lite verification: filename/length/alnum/date heuristics only.
No image recognition, no EasyOCR, no moviepy — matches the upstream
'Only uses filename to detect TikTok video / stable-lite' build.
"""

from datetime import datetime


def verifyVideoNameAndDate(
    file_name: str,
    created_at: str,
    file_types_to_check_for,
    file_name_length: int,
    file_name_is_alumn: bool,
    file_created_after: int,
) -> bool:
    """
    Verifies the name and creation date of a video file based on configured parameters.
    """
    if file_types_to_check_for and not file_name.lower().endswith(tuple(file_types_to_check_for)):
        return False

    name_without_extension = ""
    if file_name_length != 0:
        last_dot_index = file_name.rfind(".")
        if last_dot_index != -1:
            name_without_extension = file_name[:last_dot_index]
        else:
            name_without_extension = file_name
        if len(name_without_extension) != file_name_length:
            return False

    is_alnum = name_without_extension.isalnum()
    if file_name_is_alumn is not False and not is_alnum:
        return False

    if file_created_after != 0:
        video_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        timestamp = video_date.timestamp()
        if timestamp < file_created_after:
            return False

    return True


def processVideo(_video_content: bytes) -> int:
    """
    stable-lite always trusts the filename/date heuristic once it has
    matched; no frame is downloaded or inspected.
    """
    return 1
