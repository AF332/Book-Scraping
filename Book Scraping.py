## Import our libraries

from bs4 import BeautifulSoup  ## the BeautifulSoup library for scraping from the bs4 package
import requests ## Establish website connection using the requests library
import pandas as pd
import numpy as np
import re ## RegEx for pattern matching

# Base URL
base_url = "https://books.toscrape.com/"

# List to store all the book data
book_data = []

# Function to scrape book details
def scrape_book_details(book_url, category_name, category_url):
  response = requests.get(book_url)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract required book details
  try:
    book_name = soup.find('h1').text.strip()
    book_price = soup.find('p', class_='price_color').text.strip().removeprefix('Â')
    book_availability = soup.find('p', class_='instock availability').text.strip()

    # Safe access for UPC
    upc_element = soup.find('th', string='UPC')
    book_upc = upc_element.find_next('td').text.strip() if upc_element else "N/A"

    # Safe access for Tax
    tax_element = soup.find('th', string='Tax')
    book_tax = tax_element.find_next('td').text.strip().removeprefix('Â') if tax_element else "N/A"

    # Safe access for Number of Reviews
    reviews_element = soup.find('th', string='Number of reviews')
    book_number_of_reviews = reviews_element.find_next('td').text.strip() if reviews_element else "N/A"

    # Safe access for Description
    description_div = soup.find('div', id='product_description')
    book_description = description_div.find_next('p').text.strip() if description_div else "No description available"

    # Append the data extracted to the list
    book_data.append({
        "Book Name": book_name,
        "Book Link": book_url,
        "Category": category_name,
        "Category Link": category_url,
        "Availibility": book_availability,
        "Book Price": book_price,
        "Book UPC": book_upc,
        "Book Tax": book_tax,
        "Number Of Reviews": book_number_of_reviews,
        "Description": book_description
    })
  except Exception as e:
    print(f"Error while scrapping book details: {e}")

# Function to scrape a category page
def scrape_category_page(category_url, category_name):
  response = requests.get(category_url)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Get all the books from the page
  books = soup.find_all('h3')
  for book in books:
    book_url = base_url + "catalogue/" + book.a.get('href')[9:] # might need books/ as well in the catalogue part
    scrape_book_details(book_url, category_name, category_url)

  # Check for the next page
  next_page = soup.find('li', class_='next')
  if next_page:
    next_url = category_url.rsplit('/', 1)[0] + '/' + next_page.a.get('href')
    scrape_category_page(next_url, category_name)

# Function to scrape all categories
def scrape_all_categories():
  response = requests.get(base_url + "index.html")
  soup = BeautifulSoup(response.text, 'html.parser')

  # Find all category links
  categories = soup.select('.side_categories ul li ul li a')
  for category in categories:
    category_name = category.text.strip()
    category_url = base_url + category['href']
    print(f"Scraping category: {category_name}")

    # Scrape all pages of this category
    scrape_category_page(category_url, category_name)

# Start scraping all categories
scrape_all_categories()

# Create a DataFrame from the scraped data
df = pd.DataFrame(book_data)

# Print the df
print(df)

# Save the dataframe into csv
df.to_csv('book_data.csv', index=False)