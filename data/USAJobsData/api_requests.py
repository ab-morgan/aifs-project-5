import requests
import json

# API configuration
api_key = "M4j0Kq+yHXJQ+DC79jIODphkl0efmEOLFMZty6MeFFA="
api_url = "https://data.usajobs.gov/api/Search"
head = {'Authorization-Key': api_key} 
     

# Replace this with full list of job codes
# extract from usajobs-code-list.json
code_list = ['0804']

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
for value in code_list:
    data = call_api(value)
    if data is not None:
        results[value] = data

with open("test.json", "w") as f:
    json.dump(results, f)