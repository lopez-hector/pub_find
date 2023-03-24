import requests
from bs4 import BeautifulSoup
import os
import tqdm

url = 'http://www.supramolecularbiomaterials.com/pubs'
# create a directory to store the downloaded files
if not os.path.exists('pdfs'):
    os.makedirs('pdfs')

# send a GET request to the URL
response = requests.get(url)

# parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# find all links to PDF files
pdf_links = soup.find_all('a', href=lambda href: href.endswith('.pdf'))
pdf_paths = set(os.path.join('pdfs', pdf_link['href'].split('/')[-1]) for pdf_link in pdf_links)

# compare to existing directory
existing_pdfs = set(os.path.join('pdfs', f) for f in os.listdir('pdfs'))
remaining_files_to_download = pdf_paths.difference(existing_pdfs)
print(f'Remaining files: {pdf_paths.difference(existing_pdfs)}')


# http://www.supramolecularbiomaterials.com/s/Chan_JBMRA_2023.pdf
# download each PDF file
for pdf_path in remaining_files_to_download:
    # print(link)
    pdf_url = '/'.join(url.split('/')[:-1]) + '/s/' + pdf_path.split('/')[-1]
    print(pdf_url)
# try:
    response = requests.get(pdf_url)
    with open(pdf_path, 'wb') as f:
        f.write(response.content)
    print(f'Downloaded {pdf_path}. ({pdf_url})')
# except: