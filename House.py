import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re


def get_urls(driver, urls):
    current_page = max_articles = 0
    max_pages = len(urls)
    urls_list = []
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
            time.sleep(10)
            bs = BeautifulSoup(driver.page_source, 'lxml')
            articles = bs.find_all('article', class_='es-product')

            for article in articles:
                article_url = article.find('a')['href']
                urls_list.append(article_url)

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
    product_composition = []
    product_sizes = []
    errors_list = []
    error = False

    category = product_code = product_name = product_price = \
        product_discount = product_color = product_season = product_bs = product_image = None

    try:
        driver.get(df_row['url'])
        time.sleep(10)
        product_bs = BeautifulSoup(driver.page_source, 'lxml')
    except:
        print(' Recive URL error', end='')
        errors_list.append('Recive URL error')
        error = True

    if product_bs is not None:
        try:
            category = df_row['Page url'].split('/')
            category = category[-1]
            sex_length = df_row['Page url'].find('/pl/pl/')
            category_sex = df_row['Page url'][sex_length + len('/pl/pl/'):]
            category_length = category_sex.find('/')
            category_sex = category_sex[:category_length]
            category = category + '_' + category_sex
        except:
            category = None
            print(' Category error', end='')
            errors_list.append('Category error')
            error = True

        try:
            product_code = df_row['url'].split('/')
            if len(product_code[-2]) >= 3:
                product_code = product_code[-2]
            else:
                product_code = product_code[-1]
            product_code_splited = product_code.split('-')
            product_code = product_code_splited[-2] + '-' + product_code_splited[-1]

        except:
            product_code = None
            print(' Product code error', end='')
            errors_list.append('Product code error')
            error = True

        try:
            product_name = product_bs.find('h1', attrs={'data-testid': 'product-name'}).text
        except:
            product_name = None
            print(' Name error', end='')
            errors_list.append('Name error')
            error = True

        try:
            product_price = product_bs.find('div', class_='basic-pricestyled__StyledBasicPrice-sc-1tz47jj-0 hfTNOq basic-price old-price').text
            product_price = product_price.replace('PLN', '').strip()
            product_discount = product_bs.find('div', class_='wrapperstyled__Wrapper-sc-16b8t6w-0 jFTfEG')
            product_discount = product_discount.find('div', class_='basic-pricestyled__StyledBasicPrice-sc-1tz47jj-0 hfTNOq basic-price promo-price').text
            product_discount = product_discount.replace('PLN', '').strip()
        except:
            product_price = None
            product_discount = None

        if product_price is None:
            try:
                product_price = product_bs.find('div', class_='basic-pricestyled__StyledBasicPrice-sc-1tz47jj-0 hfTNOq basic-price').text
                product_price = product_price.replace('PLN', '').strip()
            except:
                product_price = None
                print(' Price error', end='')
                errors_list.append('Price error')
                error = True



        try:
            product_color = product_bs.find('span', attrs={'data-testid': 'color-picker-color-name'}).text
        except:
            product_color = None
            print(' Color error', end='')
            errors_list.append('Color error')
            error = True

        try:
            product_season = None
            season_string = str(product_bs)
            season_length = [m.start() for m in re.finditer('season', season_string)]
            for i in season_length:
                text_found = season_string[i-50:i+50]
                if text_found.find(product_code) > 0:
                    product_season = season_string[i+8:i+17].replace('"', '')
                    break
        except:
            product_season = None
            print(' Season error', end='')
            errors_list.append('Season error')
            error = True

        try:
            product_composition.clear()
            composition_bs = product_bs.find('ul', class_='compositionstyled__CompositionList-w3kdtf-0 jiWkNt')
            for composition in composition_bs.find_all('span'):
                product_composition.append(composition.text)
        except:
            product_composition.clear()
        if not len(product_composition):
            if product_bs is not None:
                for composition in product_bs.find_all('div', class_='old-wcl'):
                    product_composition.append(composition.text)
            else:
                product_composition = "Composition error"

        try:
            product_sizes.clear()
            size_bs = product_bs.find('div', class_='liststyled__ListWrapper-ohiwhh-1 gVsQTd')
            all_sizes = size_bs.find_all('li')
            for size in all_sizes:
                if 'inactive' in size['class']:
                    product_sizes.append(size.text + ': false')
                else:
                    product_sizes.append(size.text + ': true')
        except:
            product_sizes.clear()


        try:
            product_image = product_bs.find('div', class_='wrapperstyled__Wrapper-sc-16b8t6w-0 jFTfEG')
            product_image = product_image.find('aside', class_='main-photostyled__MainPhoto-zuumwy-0 daGzNJ')
            product_image = product_image.find('img')
            product_image = product_image['src']
        except:
            product_image = "Image error"


    else:
        print(' Product BS error', end='')
        errors_list.append('Product BS error')
        error = True

    if error is True:
        product_sizes = errors_list
        category = product_code = product_name = product_price = product_discount = \
            product_color = product_season = product_composition = product_image = None

    completed_data = [row_id, date_today, time_today, df_row['Page url'], df_row['url'], domain,
                      df_row['Top category'], category, product_code, product_name, product_price,
                      product_discount, product_color, product_season, product_composition,
                      product_sizes, None, product_code, product_image]

    return completed_data, error
