from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

SPAM_FILE = RAW_DIR / "SpamAssasin.csv"
PHISHING_FILE = RAW_DIR / "Nazario.csv"

OUTPUT_FILE = PROCESSED_DIR / "smartguard_dataset.csv"


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Find a column using several possible names.
    """
    normalized = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in df.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower().replace(" ", "_")

        if key in normalized:
            return normalized[key]

    return None


def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Load CSV safely.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        return pd.read_csv(file_path)
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin-1")


def combine_subject_body(
    df: pd.DataFrame,
    subject_candidates: list[str],
    body_candidates: list[str],
) -> pd.Series:
    """
    Combine subject and body when available.
    """
    subject_col = find_column(df, subject_candidates)
    body_col = find_column(df, body_candidates)

    if subject_col and body_col:
        return (
            df[subject_col].fillna("").astype(str)
            + " "
            + df[body_col].fillna("").astype(str)
        ).str.strip()

    if body_col:
        return df[body_col].fillna("").astype(str).str.strip()

    if subject_col:
        return df[subject_col].fillna("").astype(str).str.strip()

    raise ValueError(
        f"Could not find subject/body columns. Available columns: {list(df.columns)}"
    )


def prepare_spam_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert SpamAssasin dataset into SmartGuard format.
    """
    text = combine_subject_body(
        df,
        subject_candidates=[
            "subject",
            "email_subject",
            "title",
        ],
        body_candidates=[
            "body",
            "text",
            "message",
            "email",
            "content",
        ],
    )

    label_col = find_column(
        df,
        [
            "label",
            "class",
            "category",
            "type",
        ],
    )

    if label_col is None:
        raise ValueError(
            f"Could not find label column in SpamAssasin dataset. "
            f"Available columns: {list(df.columns)}"
        )

    labels = df[label_col].fillna("").astype(str).str.strip().str.lower()

    result = pd.DataFrame({
        "text": text,
        "original_label": labels,
        "label": None,
        "source": "SpamAssasin",
    })

    # Try to identify ham/spam labels.
    result.loc[
        result["original_label"].isin(["ham", "0", "legitimate", "normal"]),
        "label"
    ] = "HAM"

    result.loc[
        result["original_label"].isin(["spam", "1"]),
        "label"
    ] = "SPAM"

    return result


def prepare_phishing_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert Nazario dataset into SmartGuard format.
    Every record in this dataset is treated as PHISHING
    after manual/source verification.
    """
    text = combine_subject_body(
        df,
        subject_candidates=[
            "subject",
            "email_subject",
            "title",
        ],
        body_candidates=[
            "body",
            "text",
            "message",
            "email",
            "content",
        ],
    )

    result = pd.DataFrame({
        "text": text,
        "original_label": "phishing",
        "label": "PHISHING",
        "source": "Nazario",
    })

    return result


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning and exact duplicate removal.
    """
    df = df.copy()

    # Remove empty emails.
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df[df["text"].str.len() > 0]

    # Remove rows where label is unknown.
    df = df[df["label"].notna()]

    # Normalize whitespace.
    df["text"] = (
        df["text"]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Remove exact duplicate emails.
    before = len(df)
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)
    removed = before - len(df)

    print(f"Exact duplicate emails removed: {removed}")

    # Keep only valid SmartGuard labels.
    valid_labels = {"HAM", "SPAM", "PHISHING"}
    df = df[df["label"].isin(valid_labels)]

    # Create final ID.
    df.insert(0, "id", range(1, len(df) + 1))

    return df[["id", "text", "label", "source"]]


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading SpamAssasin dataset...")
    spam_df = load_csv(SPAM_FILE)

    print(f"SpamAssasin rows: {len(spam_df)}")
    print(f"SpamAssasin columns: {list(spam_df.columns)}")

    print("\nLoading Nazario dataset...")
    phishing_df = load_csv(PHISHING_FILE)

    print(f"Nazario rows: {len(phishing_df)}")
    print(f"Nazario columns: {list(phishing_df.columns)}")

    print("\nPreparing SpamAssasin data...")
    spam_prepared = prepare_spam_dataset(spam_df)

    print("\nPreparing Nazario data...")
    phishing_prepared = prepare_phishing_dataset(phishing_df)

    combined = pd.concat(
        [spam_prepared, phishing_prepared],
        ignore_index=True
    )

    print("\nCleaning combined dataset...")
    combined = clean_dataset(combined)

    print("\nFinal dataset summary:")
    print(combined["label"].value_counts())

    print("\nFinal dataset shape:")
    print(combined.shape)

    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved dataset to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()