# job_analyser.py
import configparser
import os
import time
from datetime import datetime
from tqdm import tqdm

from scrapers import linkedin_scraper, indeed_scraper, glassdoor_scraper, stackoverflow_scraper
from text_analysis import preprocess, extract_technical_terms, rank_terms
import pandas as pd
import nltk  # Keep the import, as you still *use* nltk


def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def main():
    # download_nltk_data()  <-- REMOVE THIS LINE
    config = load_config()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = os.path.join(config['PATHS']['data_dir'], timestamp)
    os.makedirs(data_dir, exist_ok=True)

    all_jobs = []
    sites_to_scrape = [site.strip() for site in config['SCRAPING']['sites'].split(',')]
    keywords = [kw.strip() for kw in config['KEYWORDS']['keywords'].split(',')]
    skills = [s.strip() for s in config['KEYWORDS']['skills'].split(',')]
    location = config['KEYWORDS']['location']
    max_jobs = int(config['SCRAPING']['max_jobs_per_site'])

    for site in sites_to_scrape:
        scraper_module = None
        if site == 'linkedin':
            scraper_module = linkedin_scraper
        elif site == 'indeed':
            scraper_module = indeed_scraper
        elif site == 'glassdoor':
            scraper_module = glassdoor_scraper
        elif site == 'stackoverflow':
            scraper_module = stackoverflow_scraper
        else:
            print(f"Warning: No scraper found for site '{site}'. Skipping.")
            continue

        try:
            print(f"Scraping {site}...")
            site_jobs = scraper_module.scrape_jobs(keywords, location, skills, max_jobs, config)
            all_jobs.extend(site_jobs)
        except Exception as e:
            print(f"Error scraping {site}: {e}")

    raw_jobs_file = os.path.join(data_dir, 'raw_jobs.csv')
    if all_jobs:
        df_raw = pd.DataFrame(all_jobs)
        df_raw.to_csv(raw_jobs_file, index=False)
        print(f"Raw job data saved to: {raw_jobs_file}")
    else:
        print("No job data obtained, so raw data file is empty")
        return

    print("Performing text analysis...")
    all_descriptions = [job['description'] for job in all_jobs]

    all_processed_tokens = []
    for desc in tqdm(all_descriptions, desc="Preprocessing"):
        all_processed_tokens.extend(preprocess.preprocess_text(desc, config))

    technical_terms = extract_technical_terms.extract_terms(all_processed_tokens)
    ranked_terms = rank_terms.rank_terms(technical_terms, int(config['TEXT_ANALYSIS']['min_term_frequency']))

    term_rankings_file = os.path.join(data_dir, 'term_rankings.csv')
    df_rankings = pd.DataFrame(ranked_terms, columns=['Term', 'Count'])
    df_rankings.to_csv(term_rankings_file, index=False)
    print(f"Term rankings saved to: {term_rankings_file}")

if __name__ == "__main__":
    main()