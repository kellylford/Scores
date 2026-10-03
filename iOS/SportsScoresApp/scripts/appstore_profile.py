"""Install an App Store provisioning profile for the release build.

The archive used automatic signing, which on a fresh CI runner has Xcode
create a new Apple Development certificate every run. Apple caps how many an
account may hold; on 2026-10-03 the third run in an hour failed with "Your
account has reached the maximum number of certificates". Releases now sign
manually with the Apple Distribution certificate the workflow already imports,
and this script supplies the matching App Store profile through the App Store
Connect API, so no certificate is ever created.

It finds an active IOS_APP_STORE profile for the bundle id that includes the
imported certificate, creating one if there is none, installs it where Xcode
looks, and prints its name for PROVISIONING_PROFILE_SPECIFIER.

Environment:
  ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8   App Store Connect API key
  BUNDLE_ID                               e.g. com.sportsscores.app
  CERT_SERIAL                             serial of the imported distribution
                                          certificate, hex as openssl prints it
"""

import base64
import os
import plistlib
import re
import sys
import time

import jwt
import requests

API = "https://api.appstoreconnect.apple.com/v1"
PROFILE_DIRS = [
    "~/Library/MobileDevice/Provisioning Profiles",
    "~/Library/Developer/Xcode/UserData/Provisioning Profiles",  # Xcode 16+
]


def token():
    now = int(time.time())
    return jwt.encode(
        {"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 1200,
         "aud": "appstoreconnect-v1"},
        os.environ["ASC_KEY_P8"], algorithm="ES256",
        headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})


def call(method, path, ok=(), **kwargs):
    """One API request. Status codes in `ok` return {} instead of failing."""
    resp = requests.request(method, API + path, timeout=60,
                            headers={"Authorization": f"Bearer {token()}"}, **kwargs)
    if resp.status_code in ok:
        return {}
    if resp.status_code >= 400:
        sys.exit(f"::error::{method} {path} failed ({resp.status_code}): {resp.text}")
    return resp.json() if resp.content else {}


def normalize_serial(serial):
    return re.sub(r"[^0-9A-F]", "", serial.upper()).lstrip("0")


def main():
    bundle = os.environ["BUNDLE_ID"]
    serial = normalize_serial(os.environ["CERT_SERIAL"])

    bundle_ids = call("GET", "/bundleIds", params={"filter[identifier]": bundle})["data"]
    bundle_ids = [b for b in bundle_ids if b["attributes"]["identifier"] == bundle]
    if not bundle_ids:
        sys.exit(f"::error::No bundle id {bundle} in the developer account.")
    bundle_id = bundle_ids[0]["id"]

    certs = call("GET", "/certificates", params={"limit": 200})["data"]
    cert = next((c for c in certs
                 if normalize_serial(c["attributes"].get("serialNumber", "")) == serial), None)
    if not cert:
        sys.exit(f"::error::The imported certificate (serial {serial}) isn't in the account. "
                 "Is DIST_CERT_P12_BASE64 a current Apple Distribution certificate?")
    print(f"Signing certificate: {cert['attributes'].get('name')} "
          f"({cert['attributes'].get('certificateType')})")

    profiles = call("GET", f"/bundleIds/{bundle_id}/profiles", params={"limit": 200})["data"]
    chosen = None
    for p in profiles:
        a = p["attributes"]
        if a.get("profileType") != "IOS_APP_STORE" or a.get("profileState") != "ACTIVE":
            continue
        # Profiles Xcode manages for automatic signing are listed under the
        # bundle id but answer 404 when opened; they aren't for manual use.
        cert_ids = {c["id"] for c in
                    call("GET", f"/profiles/{p['id']}/certificates", ok=(404,)).get("data", [])}
        if cert["id"] in cert_ids:
            chosen = p
            break

    if chosen:
        print(f"Using existing profile: {chosen['attributes']['name']}")
    else:
        name = f"Sports Scores App Store CI {time.strftime('%Y-%m-%d %H%M')}"
        chosen = call("POST", "/profiles", json={"data": {
            "type": "profiles",
            "attributes": {"name": name, "profileType": "IOS_APP_STORE"},
            "relationships": {
                "bundleId": {"data": {"type": "bundleIds", "id": bundle_id}},
                "certificates": {"data": [{"type": "certificates", "id": cert["id"]}]},
            }}})["data"]
        print(f"Created profile: {name}")

    content = base64.b64decode(chosen["attributes"]["profileContent"])
    # The UUID is inside the CMS-signed plist; Xcode finds profiles by it.
    start, end = content.find(b"<?xml"), content.find(b"</plist>") + len(b"</plist>")
    uuid = plistlib.loads(content[start:end])["UUID"]
    for d in PROFILE_DIRS:
        path = os.path.expanduser(d)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, f"{uuid}.mobileprovision"), "wb") as f:
            f.write(content)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"profile_name={chosen['attributes']['name']}\n")
    print(f"Installed profile {uuid}")


if __name__ == "__main__":
    main()
