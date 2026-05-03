"""
Auto-update checker for Koda.
Checks GitHub releases on startup, notifies user if a newer version is available.
"""

import json
import logging
import re
import threading
import urllib.request
import urllib.error
import webbrowser
from packaging.version import InvalidVersion, Version

logger = logging.getLogger("koda")

GITHUB_REPO = "Moonhawk80/koda"
# We list ALL releases and filter ourselves rather than calling /releases/latest,
# because that endpoint just returns the most-recently-created non-pre-release —
# which breaks the moment we publish a non-version release (e.g. model assets).
RELEASES_LIST_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases?per_page=30"
RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases/latest"

# Tag must look like a semver release: optional 'v', then N.N.N, optional pre-release suffix.
_VERSION_TAG_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:[-.][A-Za-z0-9.-]+)?$")


def check_for_update(current_version, callback=None):
    """Check GitHub for a newer release. Runs in a background thread.

    Args:
        current_version: Current app version string (e.g. "4.1.0")
        callback: Called with (latest_version, download_url) if update available,
                  or (None, None) if up to date or check failed.
    """
    thread = threading.Thread(
        target=_check_update_worker,
        args=(current_version, callback),
        daemon=True,
    )
    thread.start()
    return thread


def _check_update_worker(current_version, callback):
    """Worker thread that hits the GitHub API."""
    try:
        latest_version, download_url = _fetch_latest_release()
        if latest_version and _is_newer(latest_version, current_version):
            logger.info("Update available: %s (current: %s)", latest_version, current_version)
            if callback:
                callback(latest_version, download_url)
        else:
            logger.debug("Koda is up to date (current: %s, latest: %s)",
                         current_version, latest_version)
            if callback:
                callback(None, None)
    except Exception as e:
        logger.debug("Update check failed: %s", e)
        if callback:
            callback(None, None)


def _fetch_latest_release():
    """List GitHub releases, filter to semver-shaped Koda version tags,
    return the highest version's (version_string, download_url).

    Skips drafts, pre-releases, and any release whose tag doesn't match a
    semver pattern (e.g. asset-only tags like 'whisper-models-v1'). Falls
    back to (None, None) on any failure — auto-update is best-effort.
    """
    req = urllib.request.Request(
        RELEASES_LIST_API,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Koda-Voice-App",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        releases = json.loads(resp.read().decode("utf-8"))

    candidates = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        tag = release.get("tag_name", "")
        if not _VERSION_TAG_RE.match(tag):
            continue
        try:
            version = Version(tag.lstrip("v"))
        except InvalidVersion:
            continue
        candidates.append((version, release))

    if not candidates:
        return None, None

    candidates.sort(key=lambda pair: pair[0], reverse=True)
    top_version, top_release = candidates[0]

    download_url = RELEASES_PAGE
    for asset in top_release.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("KodaSetup") and name.endswith(".exe"):
            download_url = asset.get("browser_download_url", RELEASES_PAGE)
            break

    return str(top_version), download_url


def _is_newer(latest, current):
    """Compare version strings. Returns True if latest > current."""
    try:
        return Version(latest) > Version(current)
    except Exception:
        # Fallback: simple string comparison
        return latest != current
