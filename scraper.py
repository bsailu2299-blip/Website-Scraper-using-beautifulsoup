import csv
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import requests

# Configure logging to monitor the scraping process
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def scrape_website(target_url, output_filename="scraped_data.csv"):
    """Scrapes titles and prices from a target web page and saves them to a CSV file."""
    # Step 1: Set up a standard User-Agent header to avoid being blocked by servers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    logging.info(f"Initiating connection to: {target_url}")

    try:
        # Step 2: Send HTTP GET request
        response = requests.get(target_url, headers=headers, timeout=15)

        # Step 3: Validate response status code
        if response.status_code != 200:
            logging.error(
                f"Failed to fetch page. HTTP Status Code: {response.status_code}"
            )
            return False

        logging.info("Successfully connected. Starting HTML parsing...")

        # Step 4: Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Step 5: Data Extraction
        # NOTE: 'product-card', 'product-title', and 'product-price' are standard demo classes.
        # These can be updated based on the specific HTML layout of your target website.
        cards = soup.find_all(class_="product-card")
        dataset = []

        # If no explicit cards are found, fallback to generic item structures (like standard articles/listings)
        if not cards:
            cards = soup.find_all(["div", "article", "li"], class_=True)

        for index, card in enumerate(cards, start=1):
            try:
                # Find title/headline element
                title_element = card.find(
                    ["h2", "h3", "a", "span"],
                    class_=["product-title", "title", "headline"],
                )
                title = (
                    title_element.text.strip()
                    if title_element
                    else "No Title Available"
                )

                # Find price element
                price_element = card.find(
                    ["span", "div", "p"], class_=["product-price", "price"]
                )
                price = (
                    price_element.text.strip()
                    if price_element
                    else "No Price Listed"
                )

                # Find internal link if available
                link_element = card.find("a", href=True)
                resource_url = (
                    link_element["href"] if link_element else target_url
                )

                # Generate metadata fields
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Structure data into a record row
                record = {
                    "Item_ID": index,
                    "Timestamp": current_time,
                    "Title_Headline": title,
                    "Extracted_Price": price,
                    "Resource_URL": resource_url,
                }
                dataset.append(record)

            except Exception as item_error:
                logging.warning(
                    f"Skipping a corrupted data element row: {item_error}"
                )
                continue

        # Step 6: Data Structuring and Storage
        if not dataset:
            logging.warning(
                "No structured elements were extracted. Check target HTML selectors."
            )
            return False

        # Define dataset column schema headers
        fieldnames = [
            "Item_ID",
            "Timestamp",
            "Title_Headline",
            "Extracted_Price",
            "Resource_URL",
        ]

        # Write data rows to a permanent CSV flat file dataset
        with open(
            output_filename, mode="w", newline="", encoding="utf-8"
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dataset)

        logging.info(
            f"Success! Perfect dataset exported with {len(dataset)} entries saved to '{output_filename}'."
        )
        return True

    except requests.exceptions.RequestException as network_error:
        logging.critical(f"Network / Timeout Exception: {network_error}")
        return False
    except Exception as general_error:
        logging.critical(f"Unexpected operational crash: {general_error}")
        return False


# Execution entry point block
if __name__ == "__main__":
    demo_url = "https://webscraper.io"
    scrape_website(demo_url)
