import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_urls(driver, urls):
    current_page = max_articles = 0
    max_pages = len(urls)
    urls_list = []
    url_duplicates = []
    urls_df_final = pd.DataFrame()

    for url in urls:
        if url.find('Category') >= 0:
            max_pages = max_pages - 1

    for url in urls:
        if url.find('Category') >= 0:
            print(url)
            category = url.replace('Category: ', '')
        else:
            current_page = current_page + 1
            print(f'Pages {current_page}/{max_pages}: {url}')
            driver.get(url)
            time.sleep(5)

            product_page_bs = BeautifulSoup(driver.page_source, 'lxml')
            products_number_text = product_page_bs.find('div', class_='filter-pagination').text
            products_number_text = products_number_text.split(' ')
            products_number = products_number_text[0]
            products_number = products_number.strip()
            page_url = url + '?sort=stock&image-size=small&image=model&offset=0&page-size=' + str(products_number)
            driver.get(page_url)
            time.sleep(10)
            product_page_bs = BeautifulSoup(driver.page_source, 'lxml')
            articles_list = product_page_bs.find_all('li', class_='product-item')
            for article in articles_list:
                try:
                    url_to_download = 'https://www2.hm.com' + article.find('a')['href']
                    if url_to_download not in url_duplicates:
                        urls_list.append('https://www2.hm.com' + article.find('a')['href'])
                except:
                    pass
            urls_df = pd.DataFrame(urls_list, columns=['url'])
            urls_df['Top category'] = category
            urls_df['Page url'] = url
            urls_df_final = pd.concat([urls_df_final, urls_df])
            urls_list.clear()

    urls_df_final = urls_df_final.drop_duplicates(subset=['Top category', 'url'])
    urls_df_final = urls_df_final.reset_index(drop=True)

    return urls_df_final


def scrape_data(driver, df_row, row_id, domain):
    date_today = datetime.now().strftime("%d-%m-%Y")
    time_today = datetime.now().strftime("%H:%M:%S")
    errors_list = []
    error = False

    sizes_list = []

    category = name = price = discount = color = composition = code = product_bs = None

    try:
        driver.get(df_row['url'])
        time.sleep(5)
        bs = BeautifulSoup(driver.page_source, 'lxml')
        product_bs = bs.find('div', class_='product parbase')
    except:
        print(' Recive URL error', end='')
        errors_list.append('Recive URL error')
        error = True

    if product_bs is not None:
        try:
            name = product_bs.find('h1', class_='Heading-module--general__3HQET ProductName-module--productTitle__1T9f0 Heading-module--small__SFfSh').text
            name = name.strip()
        except:
            name = None
            print(' Name error', end='')
            errors_list.append('Name error')
            error = True

        try:
            color = product_bs.find('h3', class_='product-input-label').text
            color = color.strip()
        except:
            color = None
            print(' Color error', end='')
            errors_list.append('Color error')
            error = True

        try:
            price_check = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "product-price")))
        except:
            price_check = None
            print(' Price 1 error', end='')
            errors_list.append('Price 1 error')
            error = True

        if price_check is not None:
            try:
                discount = product_bs.find('span', class_='ProductPrice-module--priceDiscount__1tgGX').text
                discount = discount.replace('PLN', '')
                discount = discount.strip()
                discount = re.sub(r"[\n\t\s]*", "", discount)
            except:
                discount = None

            if discount is None:
                try:
                    price = product_bs.find('div', class_='ProductPrice-module--productItemPrice__2i2Hc').text
                    price = price.replace('PLN', '')
                    price = price.strip()
                    price_split = price.split(' ')
                    price = price_split[0]
                    price = re.sub(r"[\n\t\s]*", "", price)
                except:
                    price = 'Error'
                    print(' Price 2 error', end='')
                    errors_list.append('Price 2 error')
                    error = True
            else:
                try:
                    price = product_bs.find('span',
                                            class_='Price-module--original-large__kSIv7 ProductPrice-module--priceValueOriginal__3U3Cz').text
                    price = price.replace('PLN', '')
                    price = price.strip()
                    price_split = price.split(' ')
                    price = price_split[0]
                    price = re.sub(r"[\n\t\s]*", "", price)
                except:
                    price = 'Error'
                    print(' Price 3 error', end='')
                    errors_list.append('Price 3 error')
                    error = True
        else:
            price = 'Error'
            print(' Price 4 error', end='')
            errors_list.append('Price 4 error')
            error = True
        try:
            breadcrumb_bs = bs.find('ul', class_='breadcrumbs-list')
            if breadcrumb_bs is None:
                breadcrumb_bs = bs.find('ol', class_='Breadcrumbs-module--list__18u6o')

            breadcrumb_items = breadcrumb_bs.find_all('li')
            if len(breadcrumb_items) >= 3:
                sex = breadcrumb_items[-4].text.replace('\n', '')
                category = breadcrumb_items[-2].text.replace('\n', '')
                category = category + '_' + sex
            else:
                category = breadcrumb_items[-1].text.replace('\n', '')
        except:
            category = None
            print(' Category error', end='')
            errors_list.append('Category error')
            error = True

        try:
            url_splitted = df_row['url'].split('.')
            code = url_splitted[-2]
        except:
            code = None
            print(' Code error', end='')
            errors_list.append('Code error')
            error = True

        try:
            product_bs = bs.find('div', class_='product parbase')
            attributes_bs = product_bs.find('div', class_='details parbase')
            attributes = attributes_bs.find_all('div', class_='ProductAttributesList-module--descriptionListItem__3vUL2')
            for x in reversed(attributes):
                if x.text.find('Skład') >= 0:
                    composition = x.text
                    composition = composition.replace('Skład', 'Skład: ')
                    composition = composition.replace('%', '% ')
                    composition = composition.replace('  ', ' ')
                    composition = composition.replace('% ,', '%,')
                    composition = composition.strip()
        except:
            composition = None

        try:
            sizes_list_bs = product_bs.find('ul', class_='picker-list')
            for s in sizes_list_bs:
                if str(s).find('out-of-stock') >= 0:
                    sizes = s.text
                    sizes = sizes.replace('Powiadom mnie', ': unavailable')
                    sizes_list.append((sizes))
                else:
                    sizes = s.text
                    sizes = sizes.replace('Zostało tylko kilka sztuk!', '')
                    sizes = str(sizes) + ': available'
                    sizes_list.append((sizes))
            del sizes_list[0]
        except:
            sizes_list.clear()

        '''try:
            product_image = product_bs.find('div', class_='product-detail-main-image-container')
            product_image = product_image.find('img')['src']
            if product_image == None:
                product_image = "Image error"
        except:
            product_image = "Image error"'''

    else:
        print(' Product BS error', end='')
        errors_list.append('Product BS error')
        error = True


    if error is True:
        sizes_list = errors_list
        category = code = name = price = discount = color = composition = None

    completed_data = [row_id, date_today, time_today, df_row['Page url'], df_row['url'], domain,
                      df_row['Top category'], category, code, name, price, discount,
                      color, 'N/A', composition, sizes_list, None, code, None]

    return completed_data, error
