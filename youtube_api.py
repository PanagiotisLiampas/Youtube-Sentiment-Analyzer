import os
import re
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Βρίσκει αυτόματα τον κεντρικό φάκελο του project (ένα επίπεδο πάνω από το src/)
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def extract_video_id(url: str) -> Optional[str]:
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def clean_comment(text: str) -> str:
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_video_comments(video_url: str, max_comments: int = 300) -> List[str]:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("Δεν βρέθηκε το YOUTUBE_API_KEY. Έλεγξε το αρχείο .env!")

    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError(f"Μη έγκυρο YouTube URL: {video_url}")

    # Αρχικοποίηση του YouTube API client
    youtube = build("youtube", "v3", developerKey=api_key)

    comments: List[str] = []
    next_page_token: Optional[str] = None

    print(f" Ανάκτηση σχολίων για το Video ID: {video_id}...")

    try:
        while len(comments) < max_comments:
            # Υπολογίζουμε πόσα σχόλια να ζητήσουμε σε αυτό το batch
            batch_size = min(100, max_comments - len(comments))

            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=batch_size,
                pageToken=next_page_token,
                textFormat="plainText",
                order="relevance"  # Φέρνει τα πιο σχετικά/δημοφιλή πρώτα
            )
            response = request.execute()

            for item in response.get("items", []):
                raw_text = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
                cleaned = clean_comment(raw_text)
                if cleaned:  # Αγνοούμε σχόλια που έμειναν κενά (π.χ. αν ήταν μόνο ένα link)
                    comments.append(cleaned)

            # Έλεγχος αν υπάρχει επόμενη σελίδα σχολίων
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

    except HttpError as e:
        print(f" Σφάλμα από το YouTube API: {e.resp.status} - {e.reason}")
        return []

    print(f" Κατέβηκαν επιτυχώς {len(comments)} σχόλια.")
    return comments


# Block δοκιμής: Τρέχει ΜΟΝΟ αν εκτελέσεις απευθείας αυτό το αρχείο
if __name__ == "__main__":
    test_url = input("Youtube URL: ")
    fetched = fetch_video_comments(test_url, max_comments=50)

    print("\n Δείγμα πρώτων 5 σχολίων ")
    for i, c in enumerate(fetched[:5], 1):
        print(f"{i}. {c}")