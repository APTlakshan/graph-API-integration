import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()

    page_id = os.getenv("PAGE_ID")
    page_access_token = os.getenv("PAGE_ACCESS_TOKEN")
    if not page_id or not page_access_token:
        raise SystemExit("Set PAGE_ID and PAGE_ACCESS_TOKEN in your .env file.")

    message = "Hello from my Facebook Page!"
    response = requests.post(
        f"https://graph.facebook.com/{page_id}/feed",
        data={"message": message, "access_token": page_access_token},
        timeout=30,
    )

    try:
        result = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    if not response.ok:
        error = result.get("error", {})
        raise SystemExit(f"Facebook API error: {error.get('message', response.text)}")

    print(f"Post published successfully. Post ID: {result.get('id', 'unknown')}")


if __name__ == "__main__":
    main()