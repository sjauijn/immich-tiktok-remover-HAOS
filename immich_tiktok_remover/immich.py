"""
Holds the logic for interacting with the Immich API.
"""

import json
import requests


def pingServer(domain: str, api_key: str) -> bool:
    """
    Ping the server to check if it's reachable.
    """
    url = domain + "api/server-info/ping"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    return response.status_code == 200


def getAllAssets(domain: str, api_key: str, search_archived: bool):
    """
    Retrieve all VIDEO assets from the server with paginated requests.
    """
    url = domain + "api/search/metadata"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    all_assets = []
    next_page = 1
    payload = {"type": "VIDEO", "page": 1}

    if search_archived:
        payload["isArchived"] = True

    while next_page:
        payload["page"] = next_page
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            assets = data.get("assets", {}) or {}
            items = assets.get("items", [])
            all_assets.extend(items)
            next_page = assets.get("nextPage")
        else:
            print("Error while trying to connect to Immich:", response.text)
            break

    return all_assets


def serveVideo(domain: str, api_key: str, asset_id: str):
    """
    Fetch video content based on the provided ID.
    """
    url = domain + "api/assets/" + asset_id + "/video/playback"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content
    print("Error while trying to serve video:", response.text)
    return None


def getVideoAdditionalData(domain: str, api_key: str, asset_id: str):
    """
    Get additional data about a video asset.
    """
    url = domain + "api/assets/" + asset_id
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    print("Error while trying to get video data:", response.text)
    return None


def trashVideo(domain: str, api_key: str, asset_id: str):
    """
    Trash a video based on the provided ID.
    """
    url = domain + "api/assets"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = json.dumps({"force": False, "ids": [asset_id]})

    response = requests.delete(url, headers=headers, data=payload)

    if response.status_code == 204:
        print("Successfully trashed video.")
    else:
        print("Error while trying to trash video:", response.text)
        print("If this error persists, please check the Immich URL / API key configuration.")


def archiveVideo(domain: str, api_key: str, asset_id: str):
    """
    Archive a video based on the provided ID.
    """
    url = domain + "api/assets"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = json.dumps({"ids": [asset_id], "visibility": "archive"})

    response = requests.put(url, headers=headers, data=payload)

    if response.status_code == 204:
        print("Successfully archived video.")
    else:
        print("Error while trying to archive video:", response.text)
        print("If this error persists, please check the Immich URL / API key configuration.")
