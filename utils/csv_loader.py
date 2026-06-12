import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_learning_material(csv_path: str) -> pd.DataFrame:
    """
    Loads learning materials from a CSV file.
    Expects 'topic' and 'content' columns.
    """
    try:
        df = pd.read_csv(csv_path)

        # Validation
        if 'topic' not in df.columns or 'content' not in df.columns:
            raise ValueError("CSV must contain 'topic' and 'content' columns.")

        # Clean data
        df = df.dropna(subset=['topic', 'content'])
        df = df.drop_duplicates()

        logger.info(f"Successfully loaded {len(df)} topics from {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV {csv_path}: {e}")
        raise
