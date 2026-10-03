"""Send an uploaded iOS build to external TestFlight testers.

ios-release.yml uploads the build, which reaches internal testers on its own.
External testers need three more steps in App Store Connect, done here through
its API so a release tag needs no clicking:

1. Wait for Apple to finish processing the upload (usually 10-30 minutes).
2. Set "What to Test" from the release notes. External builds require it.
3. Add the build to the external tester group(s) and submit it for Beta App
   Review. Apple reviews the first build of each version, typically within a
   day; later builds of the same version usually go out without waiting.

Environment:
  ASC_KEY_ID, ASC_ISSUER_ID   App Store Connect API key (the release secrets)
  ASC_KEY_P8                  the key itself, PEM text
  BUNDLE_ID                   e.g. com.sportsscores.app
  APP_VERSION, BUILD_NUMBER   which build to send
  RELEASE_NOTES               path to the release notes markdown
  EXTERNAL_GROUPS             optional, comma-separated group names; default is
                              every external group the app has
"""

import os
import re
import sys
import time

import jwt
import requests

API = "https://api.appstoreconnect.apple.com/v1"
PROCESSING_TIMEOUT = 75 * 60
WHAT_TO_TEST_LIMIT = 4000


def token():
    now = int(time.time())
    return jwt.encode(
        {"iss": os.environ["ASC_ISSUER_ID"], "iat": now, "exp": now + 1200,
         "aud": "appstoreconnect-v1"},
        os.environ["ASC_KEY_P8"], algorithm="ES256",
        headers={"kid": os.environ["ASC_KEY_ID"], "typ": "JWT"})


def call(method, path, ok=(), **kwargs):
    """One API request. Status codes in `ok` count as success even if >= 400."""
    resp = requests.request(method, API + path, timeout=60,
                            headers={"Authorization": f"Bearer {token()}"}, **kwargs)
    if resp.status_code >= 400 and resp.status_code not in ok:
        sys.exit(f"::error::{method} {path} failed ({resp.status_code}): {resp.text}")
    return resp.json() if resp.content else {}


def what_to_test(path):
    """Release notes as plain text, within TestFlight's limit.

    The notes cover both apps, but TestFlight testers only have the iPhone one,
    so they get just the title and the iPhone sections ("### iPhone: ..."), with
    the "iPhone:" prefix dropped. The opening paragraph and every other section
    are left out, since they describe Windows or both apps. Notes with no iPhone
    sections fall back to a generic line rather than Windows changes.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = text.split("\n---", 1)[0]                     # drop the platforms footer
    intro, *sections = re.split(r"\n(?=### )", text)
    title = intro.strip().splitlines()[0] if intro.strip() else ""
    iphone = [re.sub(r"^### (iPhone|iOS):?\s*(\w)", lambda m: "### " + m.group(2).upper(), s)
              for s in sections if re.match(r"### (iPhone|iOS)", s)]
    if iphone:
        text = "\n".join([title, ""] + iphone)
    else:
        text = f"{title}\n\nGeneral fixes and improvements. Please try the app as usual."
    text = re.sub(r"^#+\s*", "", text, flags=re.M)        # headings
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)          # bold
    text = re.sub(r"`([^`]*)`", r"\1", text)              # code
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:WHAT_TO_TEST_LIMIT]


def find_build(app_id, version, number):
    """The processed build, waiting while Apple processes the upload."""
    deadline = time.time() + PROCESSING_TIMEOUT
    while True:
        builds = call("GET", "/builds", params={
            "filter[app]": app_id, "filter[version]": number,
            "filter[preReleaseVersion.version]": version, "limit": 1})["data"]
        state = builds[0]["attributes"]["processingState"] if builds else "NOT YET VISIBLE"
        print(f"Build {version} ({number}): {state}", flush=True)
        if state == "VALID":
            return builds[0]["id"]
        if state in ("FAILED", "INVALID"):
            sys.exit(f"::error::Apple marked build {version} ({number}) {state}.")
        if time.time() > deadline:
            sys.exit(f"::error::Build {version} ({number}) still {state} after "
                     f"{PROCESSING_TIMEOUT // 60} minutes.")
        time.sleep(60)


def set_what_to_test(build_id, text):
    """Set "What to Test". The API calls the field whatsNew, not whatToTest."""
    existing = call("GET", f"/builds/{build_id}/betaBuildLocalizations")["data"]
    for loc in existing:
        if loc["attributes"]["locale"] == "en-US":
            call("PATCH", f"/betaBuildLocalizations/{loc['id']}", json={"data": {
                "type": "betaBuildLocalizations", "id": loc["id"],
                "attributes": {"whatsNew": text}}})
            return
    call("POST", "/betaBuildLocalizations", json={"data": {
        "type": "betaBuildLocalizations",
        "attributes": {"locale": "en-US", "whatsNew": text},
        "relationships": {"build": {"data": {"type": "builds", "id": build_id}}}}})


def external_groups(app_id, wanted):
    groups = call("GET", f"/apps/{app_id}/betaGroups", params={"limit": 200})["data"]
    external = [g for g in groups if not g["attributes"].get("isInternalGroup")]
    names = [g["attributes"]["name"] for g in external]
    if wanted:
        chosen = [g for g in external if g["attributes"]["name"] in wanted]
        missing = set(wanted) - {g["attributes"]["name"] for g in chosen}
        if missing:
            sys.exit(f"::error::No external group named {sorted(missing)}. External groups: {names}")
        return chosen
    if not external:
        sys.exit("::error::The app has no external TestFlight groups. Create one in App Store Connect.")
    return external


def main():
    version, number = os.environ["APP_VERSION"], os.environ["BUILD_NUMBER"]
    apps = call("GET", "/apps", params={"filter[bundleId]": os.environ["BUNDLE_ID"]})["data"]
    if not apps:
        sys.exit(f"::error::No app with bundle id {os.environ['BUNDLE_ID']}.")
    app_id = apps[0]["id"]

    build_id = find_build(app_id, version, number)
    set_what_to_test(build_id, what_to_test(os.environ["RELEASE_NOTES"]))
    print("Set What to Test from the release notes.")

    wanted = [n.strip() for n in os.environ.get("EXTERNAL_GROUPS", "").split(",") if n.strip()]
    for group in external_groups(app_id, wanted):
        call("POST", f"/betaGroups/{group['id']}/relationships/builds",
             json={"data": [{"type": "builds", "id": build_id}]})
        print(f"Added to external group: {group['attributes']['name']}")

    # 409 means it is already submitted or approved; either way, nothing to do.
    call("POST", "/betaAppReviewSubmissions", ok=(409,), json={"data": {
        "type": "betaAppReviewSubmissions",
        "relationships": {"build": {"data": {"type": "builds", "id": build_id}}}}})
    print("Submitted for Beta App Review. External testers get the build once Apple approves it.")


if __name__ == "__main__":
    main()
