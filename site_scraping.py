from bs4 import BeautifulSoup
import requests
import concurrent.futures
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import csv
from cs50 import SQL

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--url", default=None, help="URL to scrape")
parser.add_argument("-o", "--output", default=None, help="output file name (must be CSV)")


args = vars(parser.parse_args())

url = args["url"]
sitemap_url = url + "/sitemap.xml"


db = SQL("sqlite:///si_imgs.db")

db.execute("CREATE TABLE IF NOT EXISTS imgs (site_url STRING, page_url STRING, src STRING, alt STRING, model_alts STRING, approved_alt STRING)")

# get list of all the URLS represented in the database

curr_urls = db.execute("SELECT DISTINCT site_url FROM imgs")

if url in [item["site_url"] for item in curr_urls]:
    raise Exception("Site has already been scraped")

if not args["output"][-4:0] == ".csv":
    raise Exception("Output file must be a CSV")

result = requests.get(sitemap_url)

# get and parse html of page into tree data structure

doc = BeautifulSoup(result.text, "html.parser")

urls = doc.find("urlset")

links = [a.text for a in urls.find_all("loc")]

scrape_data = []

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


def scrape_page(page_url):
    
    try:
        page = requests.get(page_url, headers=HEADERS)
    except:
        print("Could not access " + page_url)
        return None
    
    doc = BeautifulSoup(page.text, "html.parser")
    imgs = doc.find_all("img")
    
    for img in imgs:
        
        img_data = {}
        
        src = img.get('src')
    
        if src.startswith("//") or src.startswith("http"):
            src_url = src
        else:
            src_url = 'https://naturalhistory.si.edu' + src
            alt = img.get('alt')
        
        img_data['site_url'] = url
        img_data['page_url'] = page_url
        img_data['src'] = src_url        
        img_data['alt'] = alt
        
        scrape_data.append(img_data)
    

with concurrent.futures.ProcessPoolExecutor() as executor:
    executor.map(scrape_page, links)

csv_columns = ['site_url', 'page_url', 'src', 'alt']

for row in scrape_data:
    db.execute("INSERT INTO imgs (site_url, page_url, src, alt, model_alts, approved_alt) VALUES(?, ?, ?, ?, ?, ?)", row[0], row[1], row[2], row[3], None, None)

