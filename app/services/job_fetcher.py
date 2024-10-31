# app/services/job_fetcher.py
import requests
from bs4 import BeautifulSoup


def fetch_job_listings():
    url = "https://campusenterprises.ncsu.edu/dept/hr/opportunities/student/jobs/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        job_listings = []
        # Target the job listings within #ce-jazzhr-open > ul
        job_elements = soup.select("#ce-jazzhr-open > ul > li")
        for job in job_elements:
            title = job.get_text(strip=True)
            link_tag = job.find("a")
            link = link_tag["href"] if link_tag else "#"
            job_listings.append({"title": title, "link": link})

        return job_listings
    else:
        print(f"Failed to fetch jobs, status code: {response.status_code}")
        return []


# print(fetch_job_listings())#%%
