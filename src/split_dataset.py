from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split


INPUT_FILE = Path("data/processed/smartguard_dataset.csv")
OUTPUT_DIR = Path("data/processed")


def main():
    print("Loading dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Total samples: {len(df)}")

    # First split:
    # 70% training
    # 30% temporary data
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"]
    )

    # Split temporary data equally:
    # 15% validation
    # 15% testing
    validation_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"]
    )

    # Save files
    train_df.to_csv(
        OUTPUT_DIR / "train.csv",
        index=False
    )

    validation_df.to_csv(
        OUTPUT_DIR / "validation.csv",
        index=False
    )

    test_df.to_csv(
        OUTPUT_DIR / "test.csv",
        index=False
    )

    print("\nDataset split completed.")

    print("\nTrain:")
    print(f"Rows: {len(train_df)}")
    print(train_df["label"].value_counts())

    print("\nValidation:")
    print(f"Rows: {len(validation_df)}")
    print(validation_df["label"].value_counts())

    print("\nTest:")
    print(f"Rows: {len(test_df)}")
    print(test_df["label"].value_counts())

    print("\nFiles created:")
    print("data/processed/train.csv")
    print("data/processed/validation.csv")
    print("data/processed/test.csv")


if __name__ == "__main__":
    main()