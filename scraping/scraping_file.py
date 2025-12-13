import requests
from bs4 import BeautifulSoup
import logging
import json
import os
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

"""
    Libraries: requests, BeautifulSoup, scrapy (if needed), selenium (if needed)
    api call: requests library to fetch web pages
    parsing: BeautifulSoup to parse HTML content
    robots.txt compliance: manual check or use of 'robotparser' module

    Blocking Strategies and prevention mechanisms:
    - Use of User-Agent headers to mimic browser requests
    - Implement delays between requests to avoid rate limiting
    - Use of proxies if necessary to distribute requests
    - Rotate IP addresses if scraping at scale
    - Handle CAPTCHAs using services or manual intervention
    - Monitor HTTP response codes to detect blocking (like 403 Forbidden, 504 Server Error)
    - Use of headless browsers (like Selenium) for dynamic content if necessary
    - Respect website's terms of service regarding scraping
    - Implement error handling and retries for failed requests
    
    This module provides modularized web scraping for Amazon products including:
    - Product descriptions and details
    - Specifications
    - Product images
    - Promo videos
    - Customer reviews
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AmazonProductScraper:
    """
    A modularized scraper for Amazon products.
    Handles scraping of product information, images, videos, and reviews.
    """
    
    def __init__(self, base_headers: Optional[Dict] = None, timeout: int = 10):
        """
        Initialize the scraper with HTTP headers and timeout.
        
        Args:
            base_headers: Custom HTTP headers for requests
            timeout: Request timeout in seconds
        """
        self.base_headers = base_headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.base_headers)
    
    

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Successfully fetched: {url}")
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_product_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product title."""
        try:
            title = soup.find('body', {'class': 'a-size-large'})
            if title:
                return title.get_text(strip=True)
            return None
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return None
    
    def extract_product_price(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product price information."""
        try:
            price_dict = {}
            
            # Current price
            current_price = soup.find('span', {'class': 'a-price-whole'})
            if current_price:
                price_dict['current_price'] = current_price.get_text(strip=True)
            
            # Original price (if on discount)
            original_price = soup.find('span', {'class': 'a-price-strike'})
            if original_price:
                price_dict['original_price'] = original_price.get_text(strip=True)
            
            # Discount percentage
            discount = soup.find('span', {'class': 'a-badge-label'})
            if discount:
                price_dict['discount'] = discount.get_text(strip=True)
            
            return price_dict if price_dict else None
        except Exception as e:
            logger.error(f"Error extracting price: {e}")
            return None
    
    def extract_product_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description."""
        try:
            description_div = soup.find('div', {'id': 'feature-bullets'})
            if description_div:
                bullets = description_div.find_all('li')
                description = '\n'.join([bullet.get_text(strip=True) for bullet in bullets])
                return description
            return None
        except Exception as e:
            logger.error(f"Error extracting description: {e}")
            return None
    
    def extract_product_specifications(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product specifications."""
        try:
            specs = {}
            
            # Try to find specifications table
            spec_table = soup.find('table', {'class': 'a-keyvalue'})
            if spec_table:
                rows = spec_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        specs[key] = value
            
            return specs if specs else None
        except Exception as e:
            logger.error(f"Error extracting specifications: {e}")
            return None
    
    def extract_product_images(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract product image URLs."""
        try:
            images = []
            
            # Find image script containing all images
            image_script = soup.find('script', {'type': 'text/javascript'})
            if image_script:
                script_content = image_script.string
                # Extract URLs from the script
                if script_content:
                    url_pattern = r'https://m\.media-amazon\.com/images/[^"]+\.(jpg|jpeg|png)'
                    found_urls = re.findall(url_pattern, script_content)
                    if found_urls:
                        images.extend(found_urls)
            
            # Also try to find images in img tags
            img_tags = soup.find_all('img', {'class': 's-image'})
            for img in img_tags:
                src = img.get('src')
                if src:
                    images.append(src)
            
            return list(set(images)) if images else None
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            return None
    
    def extract_product_video(self, soup: BeautifulSoup) -> Optional[List[str]]:
        """Extract product video URLs."""
        try:
            videos = []
            
            # Look for video elements
            video_tags = soup.find_all('video')
            for video in video_tags:
                source = video.find('source')
                if source and source.get('src'):
                    videos.append(source.get('src'))
            
            # Look for video in iframes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src')
                if src and ('youtube' in src or 'video' in src):
                    videos.append(src)
            
            # Look for promotional content
            promo_divs = soup.find_all('div', {'class': 'av-promo-video'})
            for div in promo_divs:
                video_link = div.find('a')
                if video_link and video_link.get('href'):
                    videos.append(video_link.get('href'))
            
            return videos if videos else None
        except Exception as e:
            logger.error(f"Error extracting videos: {e}")
            return None
    
    def extract_product_rating(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product rating information."""
        try:
            rating_dict = {}
            
            # Overall rating
            rating = soup.find('span', {'class': 'a-icon-star'})
            if rating:
                rating_text = rating.get_text(strip=True)
                rating_dict['overall_rating'] = rating_text.split()[0] if rating_text else None
            
            # Number of ratings
            num_ratings = soup.find('span', {'id': 'acrCustomerReviewText'})
            if num_ratings:
                rating_dict['number_of_ratings'] = num_ratings.get_text(strip=True)
            
            return rating_dict if rating_dict else None
        except Exception as e:
            logger.error(f"Error extracting rating: {e}")
            return None
    
    def extract_reviews(self, soup: BeautifulSoup, max_reviews: int = 10) -> Optional[List[Dict]]:
        """
        Extract product reviews.
        
        Args:
            soup: BeautifulSoup object
            max_reviews: Maximum number of reviews to extract
            
        Returns:
            List of review dictionaries
        """
        try:
            reviews = []
            review_elements = soup.find_all('div', {'class': 'a-section'})
            
            for review_elem in review_elements[:max_reviews]:
                review_dict = {}
                
                # Review author
                author = review_elem.find('a', {'class': 'a-profile-name'})
                if author:
                    review_dict['author'] = author.get_text(strip=True)
                
                # Review rating
                rating = review_elem.find('span', {'class': 'a-icon-star'})
                if rating:
                    rating_text = rating.get_text(strip=True)
                    review_dict['rating'] = rating_text.split()[0] if rating_text else None
                
                # Review title
                title = review_elem.find('a', {'class': 'a-size-base'})
                if title:
                    review_dict['title'] = title.get_text(strip=True)
                
                # Review text
                text = review_elem.find('span', {'class': 'a-size-base'})
                if text:
                    review_dict['review_text'] = text.get_text(strip=True)
                
                # Review date
                date = review_elem.find('span', {'class': 'a-size-base'})
                if date:
                    review_dict['date'] = date.get_text(strip=True)
                
                if review_dict:
                    reviews.append(review_dict)
            
            return reviews if reviews else None
        except Exception as e:
            logger.error(f"Error extracting reviews: {e}")
            return None
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Scrape all product information from a given URL.
        
        Args:
            url: Product URL
            
        Returns:
            Dictionary containing all scraped product information
        """
        logger.info(f"Starting to scrape product from: {url}")
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        product_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': self.extract_product_title(soup),
            'price': self.extract_product_price(soup),
            'description': self.extract_product_description(soup),
            'specifications': self.extract_product_specifications(soup),
            'images': self.extract_product_images(soup),
            'videos': self.extract_product_video(soup),
            'rating': self.extract_product_rating(soup),
            'reviews': self.extract_reviews(soup)
        }
        
        logger.info(f"Successfully scraped product: {product_data.get('title', 'Unknown')}")
        return product_data
    
    def scrape_multiple_products(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple products with delay between requests.
        
        Args:
            urls: List of product URLs
            
        Returns:
            List of dictionaries containing product information
        """
        products = []
        for idx, url in enumerate(urls, 1):
            logger.info(f"Scraping product {idx}/{len(urls)}")
            product_data = self.scrape_product(url)
            if product_data:
                products.append(product_data)
            
            # Add delay to avoid rate limiting
            if idx < len(urls):
                time.sleep(2)
        
        return products
    
    def save_to_json(self, data: List[Dict], filename: str = 'products.json') -> None:
        """
        Save scraped data to JSON file.
        
        Args:
            data: List of product dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_images(self, products: List[Dict], output_dir: str = 'product_images') -> None:
        """
        Download and save product images.
        
        Args:
            products: List of product dictionaries
            output_dir: Output directory for images
        """
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            for idx, product in enumerate(products):
                if product.get('images'):
                    product_name = product.get('title', f'product_{idx}')
                    product_dir = os.path.join(output_dir, product_name[:30])
                    if not os.path.exists(product_dir):
                        os.makedirs(product_dir)
                    
                    for img_idx, img_url in enumerate(product['images']):
                        try:
                            img_response = self.session.get(img_url, timeout=self.timeout)
                            img_filename = f"{product_dir}/image_{img_idx}.jpg"
                            with open(img_filename, 'wb') as f:
                                f.write(img_response.content)
                            logger.info(f"Saved image: {img_filename}")
                        except Exception as e:
                            logger.error(f"Error downloading image: {e}")
            
            logger.info(f"Images saved to {output_dir}")
        except Exception as e:
            logger.error(f"Error saving images: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize scraper
    scraper = AmazonProductScraper()
    
    # Example product URLs
    product_urls = [
        "https://www.amazon.in/Sumeet-Stainless-Induction-Friendly-Cookware/dp/B086T3JZHV/?_encoding=UTF8&pd_rd_w=cefZG&content-id=amzn1.sym.ed223e70-d8c8-4549-9e85-87f039655f35&pf_rd_p=ed223e70-d8c8-4549-9e85-87f039655f35&pf_rd_r=C83MQYFHZHS73GVJFJQM&pd_rd_wg=2fGWr&pd_rd_r=09787769-79a4-48fa-8377-36587782ac2e&ref_=pd_hp_d_atf_dealz_sv&th=1"
        # Add more URLs here for multiple products
    ]
    
    # Scrape products
    products_data = scraper.scrape_multiple_products(product_urls)
    
    # Save results
    scraper.save_to_json(products_data)
    scraper.save_images(products_data)
    
    # Print results
    for product in products_data:
        print(f"\n{'='*60}")
        print(f"Title: {product.get('title')}")
        print(f"Price: {product.get('price')}")
        print(f"Rating: {product.get('rating')}")
        print(f"Images found: {len(product.get('images', [])) if product.get('images') else 0}")
        print(f"Videos found: {len(product.get('videos', [])) if product.get('videos') else 0}")
        print(f"{'='*60}")
