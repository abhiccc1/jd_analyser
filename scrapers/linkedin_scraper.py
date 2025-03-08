from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.firefox.service import Service as FirefoxService  # For Firefox
from webdriver_manager.firefox import GeckoDriverManager  # For Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# For Edge, use these imports:
# from selenium.webdriver.edge.service import Service as EdgeService
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
# from selenium.webdriver.edge.options import Options as EdgeOptions

from bs4 import BeautifulSoup
import time
import urllib.parse  # For URL encoding

class LinkedInScraper:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.linkedin.com/jobs/search"
        self.driver = self.get_driver()

    def get_driver(self):
        options = FirefoxOptions()  # Or EdgeOptions() if using Edge
        options.add_argument('--headless')
        # options.add_argument('--disable-gpu') # Not always needed for Firefox
        options.add_argument('--no-sandbox')
        options.add_argument(f"user-agent={self.config['SCRAPING']['user_agent']}")
        service = FirefoxService(executable_path=GeckoDriverManager().install()) # Or EdgeService
        driver = webdriver.Firefox(service=service, options=options) # Or webdriver.Edge
        return driver

    def scrape_jobs(self, keywords, location, skills, max_jobs):
        all_jobs_data = []
        for keyword in keywords:
            try:
                encoded_keyword = urllib.parse.quote_plus(keyword)
                encoded_location = urllib.parse.quote_plus(location)
                url = f"{self.base_url}?keywords={encoded_keyword}&location={encoded_location}"
                self.driver.get(url)

                job_count = 0
                last_height = self.driver.execute_script("return document.body.scrollHeight")

                while (max_jobs == -1 or job_count < max_jobs):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(int(self.config['SCRAPING']['request_delay']))
                    new_height = self.driver.execute_script("return document.body.scrollHeight")

                    if new_height == last_height:
                        try:
                            see_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button")
                            if see_more_button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", see_more_button)
                                time.sleep(int(self.config['SCRAPING']['request_delay']))
                                new_height = self.driver.execute_script("return document.body.scrollHeight")
                                if new_height == last_height:
                                    break
                        except NoSuchElementException:
                            break

                    last_height = new_height

                    job_urls = self.extract_job_links()
                    if max_jobs != -1:
                        job_urls = job_urls[:max_jobs - job_count]  # Limit URLs to remaining count
                    if not job_urls:
                        break

                    for job_url in job_urls:
                        job_data = self.scrape_single_job(job_url)
                        if job_data:
                            all_jobs_data.append(job_data)
                            job_count += 1
                        if max_jobs != -1 and job_count >= max_jobs:
                            break

                    if max_jobs != -1 and job_count >= max_jobs:
                        break

            except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                print(f"Selenium error while scraping LinkedIn with keyword {keyword}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while scraping LinkedIn with keyword {keyword}: {e}")
            finally:
                pass # ensure driver is not closed within loop

        self.driver.quit()  # Close driver after all keywords
        return all_jobs_data

    def extract_job_links(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        job_links = soup.find_all('a', class_='base-card__full-link')
        job_urls = []
        for link in job_links:
            href = link.get('href')
            if href:
                job_urls.append(href)
        return list(set(job_urls))  # Remove duplicates

    def scrape_single_job(self, job_url):
        try:
            self.driver.get(job_url)

            # Wait for a key element.  Waiting for top-card-layout is more reliable.
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "top-card-layout"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # --- Extract Job Details ---

            # Title:  Use a more specific selector.
            title = self.safe_find(soup, 'h1', class_='top-card-layout__title')

            # Company: The link is inside a span, inside a div.
            company_container = soup.find('div', class_='topcard__flavor-row')
            company = self.safe_find(company_container, 'a', class_='topcard__org-name-link') if company_container else None

            # Location:  Similar structure to company.
            location_container = soup.find('div', class_='topcard__flavor-row')
            location = self.safe_find(location_container, 'span', class_='topcard__flavor--bullet') if location_container else None

            # Description
            description_container = soup.find('div', class_='description__text')
            description = description_container.get_text(separator=" ", strip=True) if description_container else None

            if not all([title, company, description]):
                print(f"Skipping job due to missing data: {job_url}")
                return None

            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'url': job_url,
                'source': 'linkedin'
            }

        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Selenium error while scraping job details from {job_url}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while scraping job details from {job_url}: {e}")
            return None


    def safe_find(self, soup, tag, **kwargs):
        """Safely finds an element and returns its text, or None if not found."""
        try:
            element = soup.find(tag, **kwargs)
            return element.text.strip() if element else None
        except AttributeError:
            return None

def scrape_jobs(keywords, location, skills, max_jobs, config):
    scraper = LinkedInScraper(config)
    return scraper.scrape_jobs(keywords, location, skills, max_jobs)