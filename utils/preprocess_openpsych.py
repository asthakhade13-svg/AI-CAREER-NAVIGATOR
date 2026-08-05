import os
import zipfile
import requests
import io
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# URL definitions
RIASEC_URL = "https://openpsychometrics.org/_rawdata/RIASEC_data12Dec2018.zip"
BIG5_URL = "https://openpsychometrics.org/_rawdata/BIG5.zip"

RAW_DATA_DIR = "data/raw_psychometrics"
PROCESSED_DATA_PATH = "data/preprocessed_psychometrics.csv"

def download_and_extract(url, extract_to):
    """Downloads a zip file from URL and extracts it to a local folder."""
    os.makedirs(extract_to, exist_ok=True)
    zip_name = url.split("/")[-1]
    local_zip_path = os.path.join(extract_to, zip_name)
    
    if not os.path.exists(local_zip_path):
        logger.info(f"Downloading {url} to {local_zip_path}...")
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        with open(local_zip_path, "wb") as f:
            f.write(res.content)
        logger.info(f"Download complete.")
    else:
        logger.info(f"ZIP already cached at {local_zip_path}.")

    logger.info(f"Extracting {local_zip_path} to {extract_to}...")
    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    logger.info(f"Extraction complete.")

def scale_1_5_to_100(val):
    """Converts a 1-5 Likert scale to 0-100 percentage."""
    return ((val - 1.0) / 4.0) * 100.0

def run_preprocessing():
    """Downloads, cleans, aggregates, and maps the RIASEC and BIG5 datasets."""
    logger.info("Initializing OpenPsychometrics data preprocessing pipeline...")
    
    # 1. Download and extract raw datasets
    download_and_extract(RIASEC_URL, RAW_DATA_DIR)
    download_and_extract(BIG5_URL, RAW_DATA_DIR)

    # Find the extracted files
    # RIASEC extracts into a subdirectory or directly to raw_psychometrics
    riasec_csv = os.path.join(RAW_DATA_DIR, "data.csv")
    if not os.path.exists(riasec_csv):
        # Check subdirectories
        for root, dirs, files in os.walk(RAW_DATA_DIR):
            if "data.csv" in files and "BIG5" not in root:
                riasec_csv = os.path.join(root, "data.csv")
                break

    big5_csv = os.path.join(RAW_DATA_DIR, "data.csv")
    for root, dirs, files in os.walk(RAW_DATA_DIR):
        if "data.csv" in files and "BIG5" in root:
            big5_csv = os.path.join(root, "data.csv")
            break
        # Fallback for alternative BIG5 structure (sometimes it has different names)
        for f in files:
            if "big5" in f.lower() and f.endswith(".csv"):
                big5_csv = os.path.join(root, f)
                break

    # Load RIASEC
    logger.info(f"Loading RIASEC data from {riasec_csv}...")
    # RIASEC is tab-separated
    riasec_df = pd.read_csv(riasec_csv, sep='\t', low_memory=False)
    logger.info(f"Loaded {len(riasec_df)} rows of RIASEC data.")

    # Load BIG5
    logger.info(f"Loading BIG5 data from {big5_csv}...")
    big5_df = pd.read_csv(big5_csv, sep='\t', low_memory=False)
    logger.info(f"Loaded {len(big5_df)} rows of BIG5 data.")

    # Clean missing/invalid values (OpenPsychometrics uses 0 for unanswered/skip)
    logger.info("Cleaning missing and zero-unanswered scores...")
    
    # RIASEC columns (48 questions, 8 per scale: R, I, A, S, E, C)
    r_cols = [f"R{i}" for i in range(1, 9)]
    i_cols = [f"I{i}" for i in range(1, 9)]
    a_cols = [f"A{i}" for i in range(1, 9)]
    s_cols = [f"S{i}" for i in range(1, 9)]
    e_cols = [f"E{i}" for i in range(1, 9)]
    c_cols = [f"C{i}" for i in range(1, 9)]
    all_riasec_cols = r_cols + i_cols + a_cols + s_cols + e_cols + c_cols

    # Convert columns to numeric and drop rows with 0s (unanswered)
    for col in all_riasec_cols:
        riasec_df[col] = pd.to_numeric(riasec_df[col], errors='coerce')
    riasec_df = riasec_df.dropna(subset=all_riasec_cols)
    riasec_df = riasec_df[(riasec_df[all_riasec_cols] > 0).all(axis=1)]

    # BIG5 columns (50 questions, 10 per scale: E, N, A, C, O)
    ext_cols = [f"E{i}" for i in range(1, 11)]
    est_cols = [f"N{i}" for i in range(1, 11)]
    agr_cols = [f"A{i}" for i in range(1, 11)]
    csn_cols = [f"C{i}" for i in range(1, 11)]
    opn_cols = [f"O{i}" for i in range(1, 11)]
    all_big5_cols = ext_cols + est_cols + agr_cols + csn_cols + opn_cols

    for col in all_big5_cols:
        big5_df[col] = pd.to_numeric(big5_df[col], errors='coerce')
    big5_df = big5_df.dropna(subset=all_big5_cols)
    big5_df = big5_df[(big5_df[all_big5_cols] > 0).all(axis=1)]

    # Take a sample of 25,000 clean rows from both to combine
    sample_size = min(len(riasec_df), len(big5_df), 25000)
    logger.info(f"Sampling {sample_size} records to compile synthetic student profiles...")
    
    r_sample = riasec_df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    b5_sample = big5_df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    # 2. Aggregate scales (1-5 mean)
    logger.info("Computing primary psychometric scales...")
    r_mean = r_sample[r_cols].mean(axis=1)
    i_mean = r_sample[i_cols].mean(axis=1)
    a_mean = r_sample[a_cols].mean(axis=1)
    s_mean = r_sample[s_cols].mean(axis=1)
    e_mean = r_sample[e_cols].mean(axis=1)
    c_mean = r_sample[c_cols].mean(axis=1)

    ext_mean = b5_sample[ext_cols].mean(axis=1)
    est_mean = b5_sample[est_cols].mean(axis=1)
    agr_mean = b5_sample[agr_cols].mean(axis=1)
    csn_mean = b5_sample[csn_cols].mean(axis=1)
    opn_mean = b5_sample[opn_cols].mean(axis=1)

    # Convert primary scales to 0-100 percentage
    R = scale_1_5_to_100(r_mean)
    I = scale_1_5_to_100(i_mean)
    A = scale_1_5_to_100(a_mean)
    S = scale_1_5_to_100(s_mean)
    E = scale_1_5_to_100(e_mean)
    C = scale_1_5_to_100(c_mean)

    EXT = scale_1_5_to_100(ext_mean)
    EST = scale_1_5_to_100(est_mean)
    AGR = scale_1_5_to_100(agr_mean)
    CSN = scale_1_5_to_100(csn_mean)
    OPN = scale_1_5_to_100(opn_mean)

    # 3. Map primary scales to our model's 11 personality and cognitive traits (0-100 scale)
    logger.info("Mapping primary scales to platform's 11 traits...")
    analytical_thinking = 0.7 * I + 0.3 * OPN
    creativity          = 0.6 * A + 0.4 * OPN
    curiosity           = 0.4 * I + 0.6 * OPN
    attention_to_detail = 0.5 * C + 0.5 * CSN
    communication       = 0.4 * S + 0.3 * EXT + 0.3 * AGR
    leadership          = 0.6 * E + 0.4 * EXT
    building_mindset    = 0.7 * R + 0.3 * CSN
    research_mindset    = 0.8 * I + 0.2 * OPN
    user_empathy        = 0.4 * A + 0.6 * AGR
    
    # Derive additional composite traits (matching basic_info_service.py)
    problem_solving     = 0.7 * analytical_thinking + 0.3 * building_mindset
    technical_depth     = 0.7 * I + 0.3 * attention_to_detail

    # Create processed dataframe
    processed_df = pd.DataFrame({
        "analytical_thinking": analytical_thinking,
        "creativity": creativity,
        "curiosity": curiosity,
        "attention_to_detail": attention_to_detail,
        "communication": communication,
        "leadership": leadership,
        "building_mindset": building_mindset,
        "research_mindset": research_mindset,
        "user_empathy": user_empathy,
        "problem_solving": problem_solving,
        "technical_depth": technical_depth
    })

    # Round trait scores to 1 decimal place
    for col in processed_df.columns:
        processed_df[col] = processed_df[col].round(1)

    # 4. Synthesize targets using weighted domain configurations
    # Goal weight profiles (simulated for sample data)
    # We will randomly distribute career preferences (placement, technical depth, research, entrepreneurship, leadership)
    np.random.seed(42)
    placement_focus     = np.random.uniform(30, 95, sample_size)
    technical_expertise = np.random.uniform(40, 95, sample_size)
    research_orient     = np.random.uniform(20, 85, sample_size)
    entrepreneurship    = np.random.uniform(10, 80, sample_size)
    leadership_mgmt     = np.random.uniform(20, 90, sample_size)
    existing_skills     = np.random.uniform(0, 90, sample_size)

    domain_configs = {
        "AI/ML": {
            "traits": {"analytical_thinking": 0.35, "curiosity": 0.25, "research_mindset": 0.25, "technical_depth": 0.15},
            "goals": {"research_orient": 0.60, "technical_expertise": 0.40}
        },
        "Data Science": {
            "traits": {"analytical_thinking": 0.40, "research_mindset": 0.30, "attention_to_detail": 0.20, "curiosity": 0.10},
            "goals": {"research_orient": 0.40, "technical_expertise": 0.60}
        },
        "Cyber Security": {
            "traits": {"attention_to_detail": 0.35, "problem_solving": 0.30, "curiosity": 0.20, "technical_depth": 0.15},
            "goals": {"technical_expertise": 0.70, "placement_focus": 0.30}
        },
        "Web Development": {
            "traits": {"building_mindset": 0.35, "problem_solving": 0.25, "creativity": 0.20, "user_empathy": 0.20},
            "goals": {"placement_focus": 0.60, "technical_expertise": 0.40}
        },
        "App Development": {
            "traits": {"building_mindset": 0.40, "problem_solving": 0.35, "creativity": 0.15, "user_empathy": 0.10},
            "goals": {"placement_focus": 0.50, "technical_expertise": 0.30, "entrepreneurship": 0.20}
        },
        "UI/UX Design": {
            "traits": {"creativity": 0.40, "user_empathy": 0.40, "communication": 0.20},
            "goals": {"placement_focus": 0.50, "leadership_mgmt": 0.50}
        },
        "Cloud Computing": {
            "traits": {"problem_solving": 0.40, "technical_depth": 0.30, "analytical_thinking": 0.20, "attention_to_detail": 0.10},
            "goals": {"technical_expertise": 0.60, "placement_focus": 0.40}
        },
        "DevOps": {
            "traits": {"problem_solving": 0.35, "technical_depth": 0.30, "attention_to_detail": 0.20, "building_mindset": 0.15},
            "goals": {"technical_expertise": 0.60, "placement_focus": 0.40}
        },
        "Game Development": {
            "traits": {"creativity": 0.35, "building_mindset": 0.35, "problem_solving": 0.20, "curiosity": 0.10},
            "goals": {"technical_expertise": 0.50, "entrepreneurship": 0.30, "placement_focus": 0.20}
        },
        "Software Engineering": {
            "traits": {"problem_solving": 0.35, "analytical_thinking": 0.30, "building_mindset": 0.20, "technical_depth": 0.15},
            "goals": {"placement_focus": 0.50, "technical_expertise": 0.30, "leadership_mgmt": 0.20}
        }
    }

    logger.info("Computing ground-truth target domains for each profile...")
    targets = []
    for idx, row in processed_df.iterrows():
        domain_scores = {}
        for domain, weights in domain_configs.items():
            t_score = sum(row[t] * w for t, w in weights["traits"].items())
            
            # Map goals to indices
            g_scores = {
                "placement_focus": placement_focus[idx],
                "technical_expertise": technical_expertise[idx],
                "research_orient": research_orient[idx],
                "entrepreneurship": entrepreneurship[idx],
                "leadership_mgmt": leadership_mgmt[idx]
            }
            g_score = sum(g_scores[g] * w for g, w in weights["goals"].items())
            
            final_score = 0.50 * t_score + 0.30 * g_score + 0.20 * existing_skills[idx]
            domain_scores[domain] = final_score
        
        # Pick the domain with the highest suitability score
        best_domain = max(domain_scores, key=domain_scores.get)
        targets.append(best_domain)

    processed_df["target_domain"] = targets

    # Save to data directory
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Dataset compiled and saved to {PROCESSED_DATA_PATH} ({len(processed_df)} rows).")
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_preprocessing()
