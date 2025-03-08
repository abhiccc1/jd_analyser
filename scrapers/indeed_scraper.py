import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

class IndeedScraper:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.indeed.com"

    def scrape_jobs(self, keywords, location, skills, max_jobs):
        all_jobs_data = []
        for keyword in keywords:
            try:
                job_count = 0
                start_index = 0
                while job_count < max_jobs or max_jobs == -1:
                    encoded_keyword = urllib.parse.quote_plus(keyword)
                    encoded_location = urllib.parse.quote_plus(location)
                    url = f"{self.base_url}/jobs?q={encoded_keyword}&l={encoded_location}&start={start_index}"

                    headers = self.get_headers()  # Use a method for headers
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()  # Will raise HTTPError for bad codes (4xx, 5xx)

                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_elements = soup.find_all('div', class_=re.compile('job_seen_beacon'))

                    if not job_elements:
                        break

                    for job_element in job_elements:
                        job_link_element = job_element.find('a', class_=re.compile("jcs-JobTitle"))
                        if not job_link_element:
                            continue

                        job_url = self.base_url + job_link_element['href']
                        job_data = self.scrape_single_job(job_url)

                        if job_data:
                            all_jobs_data.append(job_data)
                            job_count += 1

                        if max_jobs != -1 and job_count >= max_jobs:
                            break

                    if max_jobs != -1 and job_count >= max_jobs:
                        break

                    next_page_link = soup.find('a', {'aria-label': 'Next Page'})
                    if not next_page_link:
                        break

                    next_page_url = self.base_url + next_page_link['href']
                    match = re.search(r"start=(\d+)", next_page_url)
                    if match:
                        start_index = int(match.group(1))
                    else:
                        break
                    time.sleep(int(self.config['SCRAPING']['request_delay']))

            except requests.exceptions.RequestException as e:
                print(f"Request error while scraping Indeed: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        return all_jobs_data

    def scrape_single_job(self, job_url):
        try:
            headers = self.get_headers()  # Use the same headers
            response = requests.get(job_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = self.safe_find(soup, 'h1', class_=re.compile('jobsearch-JobInfoHeader-title'))
            company = self.safe_find(soup, 'div', {'data-testid': 'inlineHeader-companyName'})

            try:
                location_div = soup.find('div', {'data-testid': 'jobsearch-JobInfoHeader-subtitle'})
                location = location_div.find_all('div')[-1].get_text(strip=True) if location_div else None
            except:
                location = None

            description = self.safe_find(soup, 'div', id='jobDescriptionText')

            if not all([title, company, description]):
                print(f"Skipping job due to missing data: {job_url}")
                return None

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'indeed'
            }
        except requests.exceptions.RequestException as e:
            print(f"Request error while scraping single job on Indeed: {e}")
            return None
        except Exception as e:
            print(f"Error scraping single job: {e}")
            return None

    def get_headers(self):
        return {
            'User-Agent': self.config['SCRAPING']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    def safe_find(self, soup, tag, **kwargs):
        """Safely finds an element and returns its text, or None if not found."""
        try:
            element = soup.find(tag, **kwargs)
            return element.get_text(separator=" ", strip=True) if element else None
        except AttributeError:
            return None
def scrape_jobs(keywords, location, skills, max_jobs, config):
    scraper = IndeedScraper(config)
    return scraper.scrape_jobs(keywords, location, skills, max_jobs)