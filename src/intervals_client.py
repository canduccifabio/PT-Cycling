"""Intervals.icu REST API Client.

Handles communication with Intervals.icu:
- Fetching historical completed activities (from MyWhoosh / Garmin Edge)
- Reading and updating athlete FTP
- Querying, creating and cleaning up planned structured workouts
"""

import base64
import logging
from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("pt_cycling.intervals")

MANAGED_TAG = "[PT-CYCLING-AUTO]"


class IntervalsClient:
    """Client for Intervals.icu REST API."""

    def __init__(self, athlete_id: str, api_key: str, base_url: str = "https://intervals.icu/api/v1"):
        self.athlete_id = athlete_id.strip() if athlete_id else ""
        self.api_key = api_key.strip() if api_key else ""
        self.base_url = base_url.rstrip("/")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        if self.api_key:
            auth_str = f"API_KEY:{self.api_key}"
            encoded_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            session.headers.update({
                "Authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "PT-Cycling-WorldTour-Serverless/1.0"
            })
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def is_configured(self) -> bool:
        return bool(self.athlete_id and self.api_key)

    def get_athlete(self) -> Dict[str, Any]:
        """Fetch athlete information including current configured FTP."""
        if not self.is_configured():
            logger.warning("Intervals.icu client credentials not configured. Operating in local mode.")
            return {"id": self.athlete_id or "local_athlete", "icu_ftp": 205}

        url = f"{self.base_url}/athlete/{self.athlete_id}"
        resp = self.session.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def update_ftp(self, new_ftp: int) -> bool:
        """Update athlete FTP across Intervals.icu profile and cycling sport settings."""
        if not self.is_configured():
            logger.info(f"[DRY-RUN] Updating FTP to {new_ftp}W (local mode)")
            return True

        logger.info(f"Updating FTP on Intervals.icu to {new_ftp}W for athlete {self.athlete_id}...")
        try:
            # 1. Update athlete profile
            url = f"{self.base_url}/athlete/{self.athlete_id}"
            payload = {"icu_ftp": new_ftp}
            resp = self.session.put(url, json=payload, timeout=15)
            resp.raise_for_status()

            # 2. Update sport settings for cycling/Ride if available
            try:
                settings_url = f"{self.base_url}/athlete/{self.athlete_id}/sport-settings"
                settings_resp = self.session.get(settings_url, timeout=10)
                if settings_resp.status_code == 200:
                    sports = settings_resp.json()
                    for sport in sports:
                        if sport.get("types", []) and any(t in ["Ride", "VirtualRide"] for t in sport.get("types", [])):
                            sport["ftp"] = new_ftp
                    self.session.put(settings_url, json=sports, timeout=15)
            except Exception as sport_err:
                logger.debug(f"Sport settings update note: {sport_err}")

            logger.info(f"Successfully updated Intervals.icu FTP to {new_ftp}W")
            return True
        except Exception as e:
            logger.error(f"Failed to update FTP on Intervals.icu: {e}")
            return False

    def get_activities(self, oldest: str, newest: str) -> List[Dict[str, Any]]:
        """Retrieve recorded activities between oldest (YYYY-MM-DD) and newest (YYYY-MM-DD)."""
        if not self.is_configured():
            logger.warning("[DRY-RUN] No Intervals.icu credentials. Returning empty activity list.")
            return []

        url = f"{self.base_url}/athlete/{self.athlete_id}/activities"
        params = {"oldest": oldest, "newest": newest}
        resp = self.session.get(url, params=params, timeout=20)
        resp.raise_for_status()
        activities = resp.json()
        logger.info(f"Fetched {len(activities)} activities from Intervals.icu between {oldest} and {newest}")
        return activities

    def get_events(self, oldest: str, newest: str) -> List[Dict[str, Any]]:
        """Retrieve planned calendar events between oldest and newest."""
        if not self.is_configured():
            logger.warning("[DRY-RUN] No Intervals.icu credentials. Returning empty events list.")
            return []

        url = f"{self.base_url}/athlete/{self.athlete_id}/events"
        params = {"oldest": oldest, "newest": newest}
        resp = self.session.get(url, params=params, timeout=20)
        resp.raise_for_status()
        events = resp.json()
        return events

    def cleanup_managed_events(self, oldest: str, newest: str) -> int:
        """Find and remove any existing future workouts tagged with [PT-CYCLING-AUTO].

        Ensures that if the athlete changes days (e.g. from MON/WED/FRI to TUE/THU/FRI)
        or re-triggers the workflow, duplicate workouts are wiped cleanly.
        """
        if not self.is_configured():
            logger.info("[DRY-RUN] Would cleanup managed events between " f"{oldest} and {newest}")
            return 0

        events = self.get_events(oldest, newest)
        deleted_count = 0
        for ev in events:
            ev_id = ev.get("id")
            name = ev.get("name", "")
            description = ev.get("description", "")
            category = ev.get("category", "")
            if category == "WORKOUT" and (MANAGED_TAG in name or MANAGED_TAG in description):
                logger.info(f"Deleting previously managed event {ev_id}: '{name}' on {ev.get('start_date_local')}")
                del_url = f"{self.base_url}/athlete/{self.athlete_id}/events/{ev_id}"
                del_resp = self.session.delete(del_url, timeout=15)
                if del_resp.status_code in [200, 204]:
                    deleted_count += 1
                else:
                    logger.warning(f"Could not delete event {ev_id}: {del_resp.status_code}")
        logger.info(f"Cleaned up {deleted_count} managed events between {oldest} and {newest}")
        return deleted_count

    def create_workout_event(
        self,
        date_iso: str,
        name: str,
        description: str,
        indoor: bool = True,
        load_tss: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a planned structured workout event on the athlete's Intervals.icu calendar.

        Intervals.icu automatically parses textual description syntax and syncs with
        MyWhoosh and Garmin Edge 850.
        """
        tagged_name = f"{name} {MANAGED_TAG}" if MANAGED_TAG not in name else name

        payload: Dict[str, Any] = {
            "category": "WORKOUT",
            "start_date_local": date_iso,
            "type": "Ride",
            "name": tagged_name,
            "description": description,
            "indoor": indoor
        }
        if load_tss:
            payload["icu_training_load"] = load_tss

        if not self.is_configured():
            logger.info(f"[DRY-RUN] Would create workout '{tagged_name}' at {date_iso}")
            return {"id": "dry_run_id", **payload}

        url = f"{self.base_url}/athlete/{self.athlete_id}/events"
        resp = self.session.post(url, json=payload, timeout=20)
        resp.raise_for_status()
        created = resp.json()
        logger.info(f"Created workout event #{created.get('id')} on {date_iso}: {tagged_name}")
        return created
