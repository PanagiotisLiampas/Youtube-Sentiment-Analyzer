from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt


def create_dashboard(
    sentiment_counts: Dict[str, int],
    top_keywords: List[Tuple[str, int]],
    video_id: str,
    output_dir: str = "output"
) -> str:
    # Δημιουργία του φακέλου output στον κεντρικό φάκελο του project αν δεν υπάρχει
    root_dir = Path(__file__).resolve().parent.parent
    save_folder = root_dir / output_dir
    save_folder.mkdir(parents=True, exist_ok=True)

    output_path = save_folder / f"analysis_{video_id}.png"

    # Ρύθμιση στυλ και μεγέθους figure (2 στήλες, 1 γραμμή)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    fig.suptitle(f"YouTube Audience Insights — Video ID: {video_id}", fontsize=15, fontweight="bold", y=0.98)

    # ΓΡΑΦΗΜΑ 1: Κατανομή Συναισθήματος
    categories = ["Positive", "Neutral", "Negative"]
    values = [sentiment_counts.get(cat, 0) for cat in categories]
    colors = ["#2ecc71", "#95a5a6", "#e74c3c"]  # Πράσινο, Γκρι, Κόκκινο

    bars1 = ax1.bar(categories, values, color=colors, width=0.55, edgecolor="none")
    ax1.set_title("Sentiment Distribution", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylabel("Number of Comments", fontsize=10)
    ax1.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 10)

    total_comments = sum(values)
    for bar, val in zip(bars1, values):
        pct = (val / total_comments * 100) if total_comments > 0 else 0
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (max(values) * 0.03 if max(values) > 0 else 0.2),
            f"{val} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    # ΓΡΑΦΗΜΑ 2: Top Λέξεις-Κλειδιά
    if top_keywords:
        words = [item[0] for item in top_keywords][::-1]  # Αντιστροφή για να είναι το #1 πάνω
        counts = [item[1] for item in top_keywords][::-1]

        bars2 = ax2.barh(words, counts, color="#3498db", height=0.6)
        ax2.set_title("Most Frequent Keywords", fontsize=12, fontweight="bold", pad=12)
        ax2.set_xlabel("Mentions", fontsize=10)
        ax2.set_xlim(0, max(counts) * 1.2)

        for bar, count in zip(bars2, counts):
            ax2.text(
                bar.get_width() + (max(counts) * 0.02),
                bar.get_y() + bar.get_height() / 2,
                str(count),
                va="center",
                ha="left",
                fontsize=9,
                fontweight="bold"
            )
    else:
        ax2.text(0.5, 0.5, "No keywords extracted", ha="center", va="center")

    # Καθαρισμός περιγραμμάτων (spines) για πιο modern look
    for ax in (ax1, ax2):
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(output_path)
    plt.close(fig)

    return str(output_path)