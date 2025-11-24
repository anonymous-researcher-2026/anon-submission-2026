#!/usr/bin/env python3
import os, json, re

BASE = "annotation_data"    # top-level annotation folder
IMG_ROOT = "gamestates/images"
JSON_ROOT = "gamestates/json"

# Extract filename from any URL
URL_EXTRACT = re.compile(r".*/([^/?]+)(?:\?.*)?$")

def convert_to_local(url, prefix, game_folder):
    """Convert GitHub or remote URL → local relative path."""
    if isinstance(url, list):
        return [convert_to_local(u, prefix, game_folder) for u in url]

    if not isinstance(url, str) or not url.strip():
        return url

    m = URL_EXTRACT.match(url)
    if not m:
        return url

    filename = m.group(1)
    return f"{prefix}/{game_folder}/{filename}"


def sanitize_json(path):
    with open(path, "r") as f:
        data = json.load(f)

    # Determine folder from Game name
    game = data.get("Game", "")
    game_folder = game.lower().replace(" ", "_")

    # Convert image URLs → local folder paths
    if "game_state_url" in data:
        data["game_state_url"] = convert_to_local(
            data["game_state_url"], IMG_ROOT, game_folder
        )

    # Convert JSON state URLs → local JSON folder paths
    if "json_game_state_url" in data:
        data["json_game_state_url"] = convert_to_local(
            data["json_game_state_url"], JSON_ROOT, game_folder
        )

    # Remove rationale text (double-blind)
    if "Rationale" in data:
        data["Rationale"] = ""

    # Write back sanitized JSON
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("✔ Sanitized:", path)


def walk_all():
    for root, _, files in os.walk(BASE):
        for f in files:
            if f.endswith(".json"):
                sanitize_json(os.path.join(root, f))


if __name__ == "__main__":
    walk_all()
    print("\nAll JSON files sanitized successfully!")
