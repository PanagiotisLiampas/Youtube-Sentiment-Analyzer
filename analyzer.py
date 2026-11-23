import re
from collections import Counter
from typing import Dict, List, Tuple, Any
import torch
from transformers import pipeline


class CommentAnalyzer:
    # Βασικά stopwords για να φιλτράρουμε λέξεις χωρίς νόημα
    STOPWORDS = {
        "the", "and", "to", "of", "a", "in", "is", "it", "that", "for", "you",
        "was", "with", "on", "as", "are", "this", "but", "be", "have", "from",
        "or", "not", "they", "what", "so", "if", "my", "like", "just", "all",
        "can", "about", "there", "when", "out", "some", "them", "would", "were",
        "more", "had", "has", "their", "really", "very", "its", "one", "get",
        "και", "το", "να", "τα", "του", "της", "των", "σε", "με", "για", "από",
        "που", "είναι", "δεν", "θα", "στο", "στη", "στον", "στην", "στα", "τι"
    }

    def __init__(self, model_name: str = "nlptown/bert-base-multilingual-uncased-sentiment"):
        # Αυτόματη επιλογή GPU (CUDA) αν υπάρχει, αλλιώς CPU
        self.device = 0 if torch.cuda.is_available() else -1
        device_label = "GPU (CUDA)" if self.device == 0 else "CPU"
        print(f" Φόρτωση BERT μοντέλου ({model_name}) σε {device_label}...")

        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=self.device,
            truncation=True,
            max_length=512
        )

    @staticmethod
    def _map_stars_to_sentiment(label: str) -> str:
        stars = int(label.split()[0])
        if stars >= 4:
            return "Positive"
        elif stars == 3:
            return "Neutral"
        else:
            return "Negative"

    def analyze_sentiment(self, comments: List[str]) -> Dict[str, Any]:
        if not comments:
            return {"counts": {"Positive": 0, "Neutral": 0, "Negative": 0}, "details": []}

        print(f" Ανάλυση συναισθήματος σε {len(comments)} σχόλια...")
        predictions = self.sentiment_pipeline(comments, batch_size=16)

        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
        details = []

        for comment, pred in zip(comments, predictions):
            category = self._map_stars_to_sentiment(pred["label"])
            counts[category] += 1
            details.append({
                "comment": comment,
                "sentiment": category,
                "raw_stars": pred["label"],
                "confidence": round(pred["score"], 3)
            })

        return {"counts": counts, "details": details}

    def extract_top_keywords(self, comments: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        all_words = []
        for comment in comments:
            # Κρατάμε μόνο λέξεις με 3 ή περισσότερους χαρακτήρες (Αγγλικά ή Ελληνικά)
            words = re.findall(r"\b[a-zA-Zα-ωΑ-Ωά-ώ]{3,}\b", comment.lower())
            filtered_words = [w for w in words if w not in self.STOPWORDS]
            all_words.extend(filtered_words)

        return Counter(all_words).most_common(top_n)


# Block δοκιμής του analyzer με πραγματικά δείγματα
if __name__ == "__main__":
    sample_comments = [
        "Some of my favorites!",
        "I miss marvel so much, excited for the new movie",
        "Avengers was a great example of good storytelling."
    ]

    analyzer = CommentAnalyzer()
    sentiment_res = analyzer.analyze_sentiment(sample_comments)
    keywords_res = analyzer.extract_top_keywords(sample_comments, top_n=5)

    print("\n Αποτελέσματα Sentiment ")
    print("Σύνολα:", sentiment_res["counts"])
    for item in sentiment_res["details"]:
        print(f"[{item['sentiment']} | {item['raw_stars']} | conf: {item['confidence']}] -> {item['comment']}")

    print("\n Top Λέξεις-Κλειδιά ")
    print(keywords_res)