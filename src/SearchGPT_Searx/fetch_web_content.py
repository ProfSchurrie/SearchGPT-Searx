import threading
import time
from SearchGPT_Searx.web_crawler import WebScraper
from SearchGPT_Searx.searx_service import SearxClient  # Use SearxClient instead of SerperClient

class WebContentFetcher:
    def __init__(self, query):
        # Initialize the fetcher with a search query
        self.query = query
        self.web_contents = []  # Stores the fetched web contents
        self.error_urls = []  # Stores URLs that resulted in an error during fetching
        self.web_contents_lock = threading.Lock()  # Lock for thread-safe operations on web_contents
        self.error_urls_lock = threading.Lock()  # Lock for thread-safe operations on error_urls

    def _web_crawler_thread(self, thread_id: int, urls: list):
        # Thread function to crawl each URL
        try:
            print(f"Starting web crawler thread {thread_id}")
            start_time = time.time()

            url = urls[thread_id]
            scraper = WebScraper()
            content = scraper.scrape_url(url, 0)

            # If the scraped content is too short, try extending the crawl rules
            if 0 < len(content) < 800:
                content = scraper.scrape_url(url, 1)

            # If the content length is sufficient, add it to the shared list
            if len(content) > 300:
                with self.web_contents_lock:
                    self.web_contents.append({"url": url, "content": content})

            end_time = time.time()
            print(f"Thread {thread_id} completed! Time consumed: {end_time - start_time:.2f}s")

        except Exception as e:
            # Handle any exceptions, log the error, and store the URL
            with self.error_urls_lock:
                self.error_urls.append(url)
            print(f"Thread {thread_id}: Error crawling {url}: {e}")

    def _searx_launcher(self):
        # Function to launch the Searx client and get search results
        searx_client = SearxClient()
        searx_results = searx_client.search(self.query)
        return searx_client.extract_components(searx_results)

    def _crawl_threads_launcher(self, url_list):
        # Create and start threads for each URL in the list
        threads = []
        for i in range(len(url_list)):
            thread = threading.Thread(target=self._web_crawler_thread, args=(i, url_list))
            threads.append(thread)
            thread.start()
        # Wait for all threads to finish execution
        for thread in threads:
            thread.join()

    def fetch(self):
        # Main method to fetch web content based on the query
        searx_response = self._searx_launcher()
        if searx_response:
            url_list = searx_response["links"]
            self._crawl_threads_launcher(url_list)
            # Reorder the fetched content to match the order of URLs
            ordered_contents = [
                next((item['content'] for item in self.web_contents if item['url'] == url), '')
                for url in url_list
            ]
            return ordered_contents, searx_response
        return [], None

# Example usage
if __name__ == "__main__":
    fetcher = WebContentFetcher("What happened to Silicon Valley Bank")
    contents, searx_response = fetcher.fetch()

    print(searx_response)
    print(contents, '\n\n')
