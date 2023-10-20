# Import necessary modules
import requests  # Used for sending HTTP requests
from bs4 import BeautifulSoup  # Used for parsing HTML

def get_wikipedia_titles():
    url = ''  # Enter the URL of the webpage you want to scrape here
    response = requests.get(url)  # Send a GET request to fetch the webpage content

    if response.status_code == 200:  # If the webpage loads successfully
        soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content using BeautifulSoup
        links = []  # Create an empty list to store the extracted links

        for link_elem in soup.select('.mw-parser-output a'):  # Select all links with CSS class 'mw-parser-output'
            href = link_elem.get('href')  # Get the 'href' attribute of the link
            links.append(href)  # Add the link to the list

        return links  # Return the list of links
    else:
        print('Failed to retrieve webpage content')  # If the webpage fails to load, print an error message

if __name__ == '__main__':
    links = get_wikipedia_titles()  # Call the function to fetch links from the Wikipedia page
    for link in links:
        print(link)  # Print the links
