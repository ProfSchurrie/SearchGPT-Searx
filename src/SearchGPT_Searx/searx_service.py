import requests


class SearxClient:
    def __init__(self, instance_url):  # Local Searx instance URL
        self.instance_url = instance_url

    def search(self, query: str):
        # Configure the query parameters for Searx API
        params = {
            "q": query,
            "format": "json"
        }

        # Perform the GET request to the Searx API and return the JSON response
        response = requests.get(f"{self.instance_url}/search", params=params)
        response.raise_for_status()  # Raise an error for unsuccessful requests
        return response.json()

    def extract_components(self, searx_response: dict):
        # Initialize lists to store the extracted components
        titles, links, snippets = [], [], []

        # Iterate through the response and extract information
        for item in searx_response.get("results", []):
            titles.append(item.get("title", ""))
            links.append(item.get("url", ""))
            snippets.append(item.get("content", ""))

        # Retrieve additional information from the response
        query = searx_response.get("query", "")
        count = len(links)
        language = searx_response.get("language", "en")

        # Organize the extracted data into a dictionary and return
        output_dict = {
            'query': query,
            'language': language,
            'count': count,
            'titles': titles,
            'links': links,
            'snippets': snippets
        }

        return output_dict


# Usage example
if __name__ == "__main__":
    client = SearxClient()
    query = "What happened to Silicon Valley Bank"
    response = client.search(query)
    components = client.extract_components(response)
    print(components)
