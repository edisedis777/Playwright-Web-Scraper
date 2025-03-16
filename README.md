# Playwright Web Scraper

A robust, object-oriented web scraping framework built with Python and Playwright designed for reliable data extraction from websites with pagination. The scraper generates structured CSV output and includes comprehensive logging.

## Features

- **Powerful Browser Automation**: Uses Playwright for full browser rendering support
- **Pagination Handling**: Automatically detects and navigates through multiple pages
- **Anti-Detection Measures**: Custom user agents and randomized delays
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Data Preservation**: Incremental saving to prevent data loss
- **Flexible Configuration**: Customizable scraping parameters
- **Concurrent or Sequential Scraping**: Choose based on target site requirements

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/playwright-web-scraper.git
cd playwright-web-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

### Basic Usage

```python
from scraper import ScraperManager

# Create a scraper manager
manager = ScraperManager()

# Add a website to scrape
manager.add_scraper(
    "https://example.com/directory",
    "output_data.csv",
    delay_range=(2, 5)
)

# Run the scraper (sequential mode)
manager.run(concurrent=False)
```

### Advanced Configuration

```python
# Create multiple scrapers
manager = ScraperManager()

# Add multiple targets with different configurations
manager.add_scraper(
    "https://example.com/page1",
    "output1.csv",
    delay_range=(1, 3)
)

manager.add_scraper(
    "https://example.com/page2",
    "output2.csv",
    delay_range=(2, 4)
)

# Run scrapers sequentially (more polite to servers)
manager.run(concurrent=False)

# Or run concurrently if appropriate
# manager.run(concurrent=True)
```

### Customizing the Scraper

To customize the data extraction logic:

1. Modify the `extract_data()` method in the `WebScraper` class to match your target website's structure.
2. Update the selectors (e.g., `.company-item`, `.name`, `.location`) to match the HTML elements on your target website.

## Project Structure

```
playwright-web-scraper/
├── scraper.py           # Main scraper code
├── requirements.txt     # Project dependencies
└── README.md            # This file
```

## Logging

The scraper creates detailed logs in the format:
```
scraping_YYYYMMDD_HHMMSS.log
```

These logs contain information about:
- Navigation success/failure
- Pages discovered and scraped
- Items extracted per page
- Error details
- Data saving operations

## Requirements

- Python 3.7+
- Playwright
- See requirements.txt for complete dependencies

## Best Practices

1. **Be respectful** of the websites you scrape:
   - Use reasonable delays between requests
   - Run in sequential mode when possible
   - Limit concurrent connections

2. **Check Terms of Service** of target websites before scraping

3. **Use for legitimate purposes** only

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their use of this scraper complies with the target website's terms of service and relevant laws and regulations.
