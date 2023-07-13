from cs50 import SQL
import csv
import pandas as pd

db = SQL("sqlite:///nh_imgs.db")

#db.execute("DROP TABLE IF EXISTS imgs")
#db.execute("CREATE TABLE IF NOT EXISTS imgs (img_no NUMBER, site_url STRING, page_url STRING, src STRING, alt STRING, model_alts STRING, approved_alt STRING)")

csv_path = 'nh_imgs.csv'

#with open(csv_path, encoding='utf-8') as csv_file:
#    csv_reader = csv.reader(csv_file)
#    next(csv_reader)

#    for row in csv_reader:
#        db.execute("INSERT INTO imgs (img_no, site_url, page_url, src, alt, model_alts, approved_alt) VALUES(?, ?, ?, ?, ?, ?, ?)", row[0], row[1], row[2], row[3], row[4], row[5], None)



data = db.execute("SELECT * FROM imgs WHERE approved_alt IS NOT NULL LIMIT 10")

print(data)

