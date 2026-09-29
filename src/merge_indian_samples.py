from pathlib import Path
import pandas as pd

PROCESSED_DIR = Path("data/processed")
RAW_DIR = Path("data/raw")

MAIN_FILE = PROCESSED_DIR / "smartguard_dataset.csv"
INDIAN_FILE = RAW_DIR / "indian_context_samples.csv"
OUTPUT_FILE = PROCESSED_DIR / "smartguard_dataset.csv"


def main():
    print("Loading main dataset...")
    main_df = pd.read_csv(MAIN_FILE)

    print("Loading Indian-context samples...")
    indian_df = pd.read_csv(INDIAN_FILE)

    # Keep only the required columns
    indian_df = indian_df[["text", "label", "source"]]

    # Add Indian samples
    combined = pd.concat(
        [
            main_df[["text", "label", "source"]],
            indian_df
        ],
        ignore_index=True
    )

    # Clean text
    combined["text"] = (
        combined["text"]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Remove empty emails
    combined = combined[combined["text"].str.len() > 0]

    # Remove exact duplicate emails
    before = len(combined)
    combined = combined.drop_duplicates(
        subset=["text"]
    ).reset_index(drop=True)

    removed = before - len(combined)

    # Create fresh IDs
    combined.insert(
        0,
        "id",
        range(1, len(combined) + 1)
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nDataset merged successfully.")
    print(f"Duplicate rows removed: {removed}")
    print(f"Total rows: {len(combined)}")

    print("\nClass distribution:")
    print(combined["label"].value_counts())

    print("\nClass percentages:")
    print(
        (combined["label"].value_counts(normalize=True) * 100)
        .round(2)
    )

    print("\nSources:")
    print(combined["source"].value_counts())

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()