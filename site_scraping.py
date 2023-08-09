from bs4 import BeautifulSoup
import requests
import concurrent.futures
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import csv
from cs50 import SQL

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--url", default=None, help="URL to scrape")

args = vars(parser.parse_args())

url = args["url"]
sitemap_url = url + "/page-sitemap.xml"


db = SQL("sqlite:///nh_imgs.db")

db.execute("CREATE TABLE IF NOT EXISTS imgs (img_no NUMBER, site_url STRING, page_url STRING, src STRING, alt STRING, model_alts STRING, approved_alt STRING)")

# get list of all the URLS represented in the database

curr_urls = db.execute("SELECT DISTINCT site_url FROM imgs")

if url in [item["site_url"] for item in curr_urls]:
    raise Exception("Site has already been scraped")

result = requests.get(sitemap_url)

# get and parse html of page into tree data structure

doc = BeautifulSoup(result.text, "html.parser")

urls = doc.find("urlset")

links = [a.text for a in urls.find_all("loc")]

HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


def scrape_page(page_url):
    
    try:
        page = requests.get(page_url, headers=HEADERS)
    except:
        print("Could not access " + page_url)
        return None
    
    doc = BeautifulSoup(page.text, "html.parser")
    imgs = doc.find_all("img")
    scrape_data = []
    
    for img in imgs:
        
        img_data = {}
        
        src = img.get('src')
    
        if src.startswith("//") or src.startswith("http"):
            src_url = src
        else:
            src_url = url + src

        alt = img.get('alt')
        
        img_data['site_url'] = url
        img_data['page_url'] = page_url
        img_data['src'] = src_url        
        img_data['alt'] = alt
        
        scrape_data.append(img_data)

    return scrape_data

if __name__ == '__main__':


    with concurrent.futures.ProcessPoolExecutor() as executor:
        data = executor.map(scrape_page, links)

    img_data = []

    for datum in data:
        for row in datum:
            img_data.append(row)

    for row in img_data:
        max_value = db.execute("SELECT MAX(img_no) FROM imgs;")[0]['MAX(img_no)']
        db.execute("INSERT INTO imgs (img_no, site_url, page_url, src, alt, model_alts, approved_alt) VALUES(?, ?, ?, ?, ?, ?, ?)", max_value + 1, row['site_url'], row['page_url'], row['src'], row['alt'], None, None)

