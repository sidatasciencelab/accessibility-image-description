import requests

import csv

with open("nh_museum.csv") as csvfile, open("demo.csv", "w") as writeFile:
    csv_reader = csv.reader(csvfile)
    csv_writer = csv.writer(writeFile)
    csv_writer.writerow(next(csv_reader) + ['img_address'])

    for i in range(100):
        row = next(csv_reader)
        src = row[3]

        response = requests.get(src)

        path = "images/image_" + str(i) + ".png"

        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)

        
        new_row = row + [path]
        csv_writer.writerow(new_row)
