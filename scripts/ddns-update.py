"""
Keeps the public DNS records for this stack's internet-facing hostnames (on
Cloudflare -- currently watch.<domain>, <domain>, and jellyseerr.<domain>)
pointed at this machine's current WAN IP. Run via pythonw.exe as a scheduled
task action, same pattern as scripts/rclone-sync.py -- pythonw has no console,
so nothing flashes on each run, and every outcome (including failures) goes to
a log file since an uncaught exception would otherwise vanish silently.

Why this exists at all: the WAN IP on a residential connection is not guaranteed
static (see README section 6). Caddy's DNS-01 ACME challenge and the router's
port-443 forward both depend on each of these hostnames resolving to wherever
this house currently is -- if the IP drifts and a record doesn't follow, the
cert still renews fine (DNS-01 only needs the TXT challenge record, not the A
record) but remote access to that one app silently starts failing to connect.

Cloudflare's API needs the DNS record's own ID to PATCH it -- there's no
"upsert by name" endpoint -- so this looks each record up by name first (GET),
then only PATCHes if the current value actually differs. Comparing before
writing means a no-op run (the common case, IP unchanged) makes one read-only
API call per record instead of an unconditional write every few minutes. One
record's lookup/update failure doesn't stop the others from being checked --
main() collects failures and reports them all at the end.
"""

import logging
import sys

import requests

from lib.config import get_config
from lib.logging import setup_logging
from lib.notifications import notify_ntfy

log = logging.getLogger(__name__)

CF_API = "https://api.cloudflare.com/client/v4"
IP_ECHO_SERVICES = [
    "https://api.ipify.org?format=json",
    "https://ifconfig.me/all.json",
]


def current_wan_ip():
    last_error = None
    for url in IP_ECHO_SERVICES:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            ip = data.get("ip") or data.get("ip_addr")
            if ip:
                return ip
        except (requests.RequestException, ValueError) as e:
            last_error = e
            log.warning(f"IP echo service failed ({url}): {e}")
    raise RuntimeError(f"all IP echo services failed; last error: {last_error}")


def cf_headers(api_token):
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }


def get_zone_id(zone, api_token):
    r = requests.get(
        f"{CF_API}/zones",
        headers=cf_headers(api_token),
        params={"name": zone},
        timeout=15,
    )
    r.raise_for_status()
    result = r.json()["result"]
    if not result:
        raise RuntimeError(f"Cloudflare zone not found: {zone}")

    return result[0]["id"]


def get_record(zone_id, hostname, api_token):
    t = requests.get(
        f"{CF_API}/zones/{zone_id}/dns_records",
        headers=cf_headers(api_token),
        params={
            "type": "A",
            "name": hostname,
        },
        timeout=15,
    )
    t.raise_for_status()

    result = t.json()["result"]

    if not result:
        raise RuntimeError(
            f"Cloudflare A record not found: {hostname} "
            "(create it once manually first)"
        )

    return result[0]


def update_record(zone_id, record_id, new_ip, api_token):
    r = requests.patch(
        f"{CF_API}/zones/{zone_id}/dns_records/{record_id}",
        headers=cf_headers(api_token),
        json={"content": new_ip},
        timeout=15,
    )
    r.raise_for_status()
    if not r.json().get("success"):
        raise RuntimeError(f"Cloudflare update reported failure: {r.text[:300]}")


def main(config: Config):
    new_ip = current_wan_ip()
    zone_id = get_zone_id(
        config.cf_zone,
        config.cf_api_token,
    )

    failures = []
    for hostname in config.ddns_records:
        try:
            record = get_record(
                zone_id,
                hostname,
                config.cf_api_token,
            )
            old_ip = record["content"]

            if old_ip == new_ip:
                log.info(
                    "no change: %s already %s",
                    hostname,
                    new_ip,
                )
                continue

            update_record(
                zone_id,
                record["id"],
                new_ip,
                config.cf_api_token,
            )

            log.info(
                "updated: %s %s -> %s",
                hostname,
                old_ip,
                new_ip,
            )

            notify_ntfy(
                config,
                "DDNS updated",
                f"{hostname}: {old_ip} -> {new_ip}",
            )

        except Exception as e:
            log.exception("failed to update %s", hostname)
            failures.append(f"{hostname}: {e}")

    if failures:
        raise RuntimeError(
            f"{len(failures)} of {len(config.ddns_records)} "
            f"record(s) failed: {'; '.join(failures)}"
        )


def run():
    config = get_config()

    setup_logging(
        config,
        logger_name="ddns-update",
    )

    try:
        main(config)
    except Exception:
        log.exception("ddns-update failed")

        notify_ntfy(
            config,
            "DDNS update FAILED",
            "see ddns-update.log",
        )

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())
