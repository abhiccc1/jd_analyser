import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse

class GlassdoorScraper:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.glassdoor.com"

    def scrape_jobs(self, keywords, location, skills, max_jobs):
        all_jobs_data = []
        for keyword in keywords:
            try:
                job_count = 0
                page_num = 1
                while job_count < max_jobs or max_jobs == -1:
                    encoded_keyword = urllib.parse.quote_plus(keyword)
                    encoded_location = urllib.parse.quote_plus(location)
                    # Example URL - adjust based on Glassdoor's actual URL structure
                    url = f"{self.base_url}/Job/{encoded_location}-{encoded_keyword}-jobs-SRCH_IL.0,7_IC1147401_KO8,22_IP{page_num}.htm"


                    headers = self.get_headers()
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_elements = soup.find_all('li', class_=re.compile('react-job-listing'))

                    if not job_elements:
                        break

                    for job_element in job_elements:
                        try:
                            job_link_element = job_element.find('a', class_=re.compile('jobLink'))
                            if job_link_element:
                                job_url = self.base_url + job_link_element['href']
                            else:
                                continue
                        except:
                            continue
                        job_data = self.scrape_single_job(job_url)
                        if job_data:
                            all_jobs_data.append(job_data)
                            job_count += 1
                        if max_jobs != -1 and job_count >= max_jobs:
                            break
                    if max_jobs != -1 and job_count >= max_jobs:
                        break

                    next_button = soup.find('li', {'class': 'next'})
                    if not next_button or 'disabled' in next_button.get('class', []):
                        break

                    page_num += 1
                    time.sleep(int(self.config['SCRAPING']['request_delay']))
            except requests.exceptions.RequestException as e:
                print(f"Request error while scraping Glassdoor: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
        return all_jobs_data


    def scrape_single_job(self, job_url):
        try:
            headers = self.get_headers()
            response = requests.get(job_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = self.safe_find(soup, 'div', class_='e1tk4kwz1')
            company = self.safe_find(soup, 'div', class_='e1tk4kwz4')
            location = self.safe_find(soup, 'div', class_='e1tk4kwz5')
            description_section = soup.find('div', id='JobDescriptionContainer')
            description = description_section.get_text(separator=" ", strip=True) if description_section else None

            if not all([title, company, description]):
                print(f"Skipping job due to missing data: {job_url}")
                return None

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'glassdoor'
            }
        except requests.exceptions.RequestException as e:
            print(f"Request error while scraping single job on Glassdoor: {e}")
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
        """Safely finds an element and returns its text or None if not found"""
        try:
            element = soup.find(tag, **kwargs)
            return element.get_text(separator=" ", strip=True) if element else None
        except AttributeError:
            return None

def scrape_jobs(keywords, location, skills, max_jobs, config):
    scraper = GlassdoorScraper(config)
    return scraper.scrape_jobs(keywords, location, skills, max_jobs)