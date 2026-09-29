from pathlib import Path
import pandas as pd


DATA_DIR = Path("data/raw")


def inspect_csv(file_path: Path) -> None:
    print("\n" + "=" * 60)
    print(f"FILE: {file_path.name}")
    print("=" * 60)

    try:
        df = pd.read_csv(file_path)

        print(f"\nRows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nColumn names:")
        for column in df.columns:
            print(f"  - {column}")

        print("\nFirst 5 rows:")
        print(df.head())

        print("\nMissing values:")
        print(df.isnull().sum())

        print("\nData types:")
        print(df.dtypes)

        print("\nPossible label columns:")
        for column in df.columns:
            unique_values = df[column].dropna().astype(str).unique()

            if len(unique_values) <= 10:
                print(f"\n{column}:")
                print(unique_values[:20])

    except Exception as error:
        print(f"Error reading {file_path.name}: {error}")


def main() -> None:
    if not DATA_DIR.exists():
        print("data/raw folder does not exist.")
        return

    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/raw.")
        return

    for file_path in csv_files:
        inspect_csv(file_path)


if __name__ == "__main__":
    main()