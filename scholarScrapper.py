import requests
from bs4 import BeautifulSoup
import csv

def classify_publication(title):
    if 'conference' in title.lower():
        return 'Conference'
    elif 'arxiv' in title.lower():
        return 'arXiv'
    elif 'patent' in title.lower():
        return 'Patent'
    else:
        return 'Journal'

def scrape_google_scholar(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    publications = []
    page = 1
    unique_titles = set()  # Keep track of unique titles

    abFlag = True
    while abFlag:
        response = requests.get(url + f'&cstart={page}', headers=headers)    
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
        
            items = soup.find_all('tr', class_='gsc_a_tr')
            if not items:
                break


            for item in items:
                #title = item.find('a', class_='gsc_a_at').text.strip()
                title_elem = item.find('a', class_='gsc_a_at')
                if title_elem is None:  # Check if title element is not found
                    abFlag = False
                    break
                
                title = title_elem.text.strip()
                if title not in unique_titles:

                    #title = item.find('h3', class_='gs_rt').text.strip()
                    itemList = item.findAll('div', class_='gs_gray')
                    
                    #authors = item.find('div', class_='gs_gray').text.strip()
                    #venue = item.find('div', class_='gs_gray').text.strip()
                    authors = itemList[0].text.strip()
                    venue = itemList[1].text.strip()
                    
                    #link = item.find('a', class_='gs_a_t').find('a')['href']
                    #year = item.find('span', class_='gsc_a_h gsc_a_hc gs_ibl').text.split('-')[-1].strip()
                    year_elem = item.find('span', class_='gsc_a_h gsc_a_hc gs_ibl')
                    if not year_elem:
                        abc = 0
                    year = year_elem.text.split('-')[-1].strip() if year_elem else '0'
                    #year = item.find('div', class_='gs_a').text.split('-')[-1].strip()  
                    print(year) 
                    if len(year) == 0:
                        year = '0'
                    publication_type = classify_publication(venue)
                        
                    publication = { 
                        'Title': title,
                        'Authors': authors,
                        'Year': year,
                        #'Link': link,
                        'Venue' : venue,
                        'Publication Type': publication_type
                    }
                    publications.append(publication)
                    unique_titles.add(title)  # Add title to the set

            print(page)
            page += 10  # Go to the next page
        else:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            break
        
        # Sort the list of publications based on the 'Year' key
    
    sorted_publications = sorted(publications, key=lambda x: int(x['Year']), reverse=True)    
    return sorted_publications

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# Replace this with the Google Scholar URL you want to scrape
google_scholar_url = 'https://scholar.google.com.pk/citations?user=59ISSCEAAAAJ'

publications = scrape_google_scholar(google_scholar_url)

if publications:
    csv_filename = 'publications.csv'
    save_to_csv(publications, csv_filename)

    print(f"Data saved to {csv_filename}")
else:
    print("No publications found.")
