import requests
from bs4 import BeautifulSoup

def get_wikipedia_titles():
    url = ''
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        for link_elem in soup.select('.mw-parser-output a'):
            href = link_elem.get('href')
            links.append(href)

        return links
    else:
        print('無法獲取網頁內容')

if __name__ == '__main__':
    links = get_wikipedia_titles()
    for link in links:
        print(link)
