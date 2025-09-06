import random
import socket
from typing import Any, Dict, List, Optional

import requests

# Based on Radio Browser docs, we should discover servers via DNS SRV or resolve all.api.radio-browser.info
# and randomize the list for resilience.
# We'll default to api.radio-browser.info which handles geo load-balancing and is recommended, but
# still support randomization across a few hardcoded mirrors as fallback.

DEFAULT_SERVERS = [
    "https://api.radio-browser.info",
    "https://de1.api.radio-browser.info",
    "https://de2.api.radio-browser.info",
    "https://fi1.api.radio-browser.info",
]

USER_AGENT = "Walls-RadioPlayer/1.0"


class RadioBrowserClient:
    def __init__(self, servers: Optional[List[str]] = None, timeout: int = 12):
        self.servers = list(servers or DEFAULT_SERVERS)
        random.shuffle(self.servers)
        self.timeout = timeout

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        last_error: Optional[Exception] = None
        for base in self.servers:
            url = f"{base}{path}"
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                if "application/json" in resp.headers.get("Content-Type", ""):
                    return resp.json()
                return resp.json()
            except Exception as e:
                last_error = e
                continue
        if last_error:
            raise last_error
        raise RuntimeError("No servers configured")

    def search(self, name: Optional[str] = None, tag: Optional[str] = None,
               countrycode: Optional[str] = None, language: Optional[str] = None,
               codec: Optional[str] = None, limit: int = 50, hide_broken: bool = True) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if name:
            params["name"] = name
        if tag:
            params["tag"] = tag
        if countrycode:
            params["countrycode"] = countrycode
        if language:
            params["language"] = language
        if codec:
            params["codec"] = codec
        if limit:
            params["limit"] = limit
        if hide_broken:
            params["hidebroken"] = "true"
        return self._request("/json/stations/search", params=params)

    def top_tags(self, limit: int = 100) -> List[Dict[str, Any]]:
        params = {"limit": limit} if limit else None
        return self._request("/json/tags", params=params)

    def countries(self) -> List[Dict[str, Any]]:
        return self._request("/json/countries")

    def count_click(self, stationuuid: str) -> Dict[str, Any]:
        # Increase click count when user starts playing a stream
        return self._request("/json/url/" + stationuuid)



    @staticmethod
    def resolved_url(station: Dict[str, Any]) -> Optional[str]:
        # Prefer url_resolved when present
        return station.get("url_resolved") or station.get("url")