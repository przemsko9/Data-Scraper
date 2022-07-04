from pathlib import Path
from datetime import datetime
import time
import csv


def create_file(domain, date):
    file_name = str(date) + ' ' + str(domain) + '.csv'
    my_file = Path(file_name)
    if my_file.is_file():
        print('File exists')
    else:
        print("File don't exists")
        file_header = ["id", "Date", "Time", "Page URL", "Product URL", "Domain", "Top category",
                       "Category", "Product code", "Product name", "Price", "Discount price",
                       "Color", "Season", "Composition", "Sizes", "Product ID", "Unique value", "Image"]
        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(file_header)


def read_urls(domain):
    file_name = domain + ' links.txt'
    with open(file_name) as file:
        urls = file.readlines()
        urls = [line.rstrip() for line in urls]

    return urls


def save_to_file(domain, data, date_today):
    file_name = str(date_today) + ' ' + str(domain) + '.csv'
    with open(file_name, 'a', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(data)
