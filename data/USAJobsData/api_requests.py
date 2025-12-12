import requests
import json
import time

# API configuration
api_key = "M4j0Kq+yHXJQ+DC79jIODphkl0efmEOLFMZty6MeFFA="
api_url = "https://data.usajobs.gov/api/Search"
head = {'Authorization-Key': api_key} 
     

# list of job codes extracted from file
with open('data/USAJobsData/usajobs-code-list.json') as f:
    job_code_data = json.load(f)

codelist = []
for code in job_code_data['CodeList'][0]['ValidValue']:
    codelist.append(code["Code"])

# function to call API
def call_api(job_code):
    param = {'JobCategoryCode': job_code}
    try:
        response = requests.get(api_url, headers = head, params = param)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {value}: {e}")
        return None

# loop over list to call api
results = {}
for value in codelist:
    data = call_api(value)
    if data is not None:
        results[value] = data
    time.sleep(1)

with open("data/USAJobsData/all-listings.json", "w") as f:
    json.dump(results, f)