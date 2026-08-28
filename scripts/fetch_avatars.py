#!/usr/bin/env python3
"""
Fetch Codeforces + LeetCode profile avatars and save them locally
so a GitHub Action can commit them into the repo on a schedule.

Codeforces: uses the official public API (stable).
LeetCode:   uses the unofficial GraphQL endpoint (can break if LeetCode
            changes their schema — that's the tradeoff of "no official API").
"""

import os
import sys
import json
import urllib.request

CF_HANDLE = "Habib101"
LC_USERNAME = "habibprogrammerbd"

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def save_image(url, filename):
    img_bytes = fetch(url)
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, "wb") as f:
        f.write(img_bytes)
    print(f"Saved {filename} from {url}")


def update_codeforces_avatar():
    api_url = f"https://codeforces.com/api/user.info?handles={CF_HANDLE}"
    raw = fetch(api_url)
    data = json.loads(raw)
    if data.get("status") != "OK":
        print("Codeforces API error:", data)
        return False
    avatar_url = data["result"][0]["titlePhoto"]
    if avatar_url.startswith("//"):
        avatar_url = "https:" + avatar_url
    save_image(avatar_url, "cf_avatar.png")
    return True


def update_leetcode_avatar():
    query = {
        "query": """
        query userPublicProfile($username: String!) {
          matchedUser(username: $username) {
            profile {
              userAvatar
            }
          }
        }
        """,
        "variables": {"username": LC_USERNAME},
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://leetcode.com/{LC_USERNAME}/",
    }
    raw = fetch(
        "https://leetcode.com/graphql",
        data=json.dumps(query).encode("utf-8"),
        headers=headers,
    )
    data = json.loads(raw)
    avatar_url = data["data"]["matchedUser"]["profile"]["userAvatar"]
    save_image(avatar_url, "lc_avatar.png")
    return True


if __name__ == "__main__":
    ok = True
    try:
        update_codeforces_avatar()
    except Exception as e:
        print("Codeforces fetch failed:", e)
        ok = False

    try:
        update_leetcode_avatar()
    except Exception as e:
        print("LeetCode fetch failed:", e)
        ok = False

    sys.exit(0 if ok else 1)
