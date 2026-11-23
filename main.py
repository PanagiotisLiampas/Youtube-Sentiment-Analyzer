from youtube_api import extract_video_id, fetch_video_comments
from analyzer import CommentAnalyzer
from visualizer import create_dashboard


def run_pipeline():
    print(" YouTube Comment Sentiment & Keyword Analyzer (BERT)")

    video_url = input("\n Επικόλλησε το URL του YouTube βίντεο: ").strip()
    video_id = extract_video_id(video_url)

    if not video_id:
        print(" Μη έγκυρο YouTube URL. Δοκίμασε ξανά.")
        return

    # 1. Extract: Ανάκτηση σχολίων από YouTube API
    comments = fetch_video_comments(video_url, max_comments=300)
    if not comments:
        print(" Δεν βρέθηκαν σχόλια για ανάλυση.")
        return

    # 2. Analyze: BERT Sentiment Analysis & Keyword Extraction
    analyzer = CommentAnalyzer()
    sentiment_results = analyzer.analyze_sentiment(comments)
    top_keywords = analyzer.extract_top_keywords(comments, top_n=10)

    # 3. Report στο Terminal
    counts = sentiment_results["counts"]
    details = sentiment_results["details"]

    print(f"Σύνολο αναλυμένων σχολίων: {len(comments)}")
    print(f" Positive: {counts['Positive']} |  Neutral: {counts['Neutral']} |  Negative: {counts['Negative']}")

    print("\n Top 5 Λέξεις-Κλειδιά:")
    for word, freq in top_keywords[:5]:
        print(f"   • {word}: {freq} φορές")

    # Εύρεση κορυφαίου θετικού και αρνητικού σχολίου βάσει confidence
    positives = [d for d in details if d["sentiment"] == "Positive"]
    negatives = [d for d in details if d["sentiment"] == "Negative"]

    if positives:
        best_pos = max(positives, key=lambda x: x["confidence"])
        print(f"\n Πιο Θετικό Σχόλιο ({best_pos['raw_stars']}, conf: {best_pos['confidence']}):")
        print(f"   \"{best_pos['comment'][:150]}...\"" if len(best_pos['comment']) > 150 else f"   \"{best_pos['comment']}\"")

    if negatives:
        most_neg = max(negatives, key=lambda x: x["confidence"])
        print(f"\n Πιο Αρνητικό Σχόλιο ({most_neg['raw_stars']}, conf: {most_neg['confidence']}):")
        print(f"   \"{most_neg['comment'][:150]}...\"" if len(most_neg['comment']) > 150 else f"   \"{most_neg['comment']}\"")

    # 4. Visualize: Δημιουργία & Αποθήκευση Dashboard
    create_dashboard(
        sentiment_counts=counts,
        top_keywords=top_keywords,
        video_id=video_id
    )

if __name__ == "__main__":
    run_pipeline()