import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, \
    ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import re


def get_urls(driver, urls):
    current_page = 0
    max_pages = len(urls)
    products_urls_final = pd.DataFrame(columns=['url', 'Category'])

    for url in urls:
        link_list = []
        current_page = current_page + 1
        print(f'Pages {current_page}/{max_pages}: {url}')
        driver.get(url)
        time.sleep(5)
        url_bs = BeautifulSoup(driver.page_source, 'lxml')
        article_bs = url_bs.find_all('div', class_='col-md-4 col-lg-3 Products__productsFullWide__1COIK Products__productsColumns4__33EJi col-xs-6')

        for article in article_bs:
            article_url = article.find('a')
            article_url = article_url['href']
            article_url_long = 'https://wearmedicine.com' + article_url
            link_list.append(article_url_long)

        try:
            slider_bs = url_bs.find('div', class_='ProductsPagination__paginationPager__1JlaF')
        except:
            slider_bs = None

        if slider_bs is not None:
            slider_pages = slider_bs.find_all('li')
            last_url_page = slider_pages[-1].text

            for i in range(2, int(last_url_page) + 1):
                new_url = url + '?page=' + str(i)
                print(f'Pages {current_page}/{max_pages} {i}/{last_url_page}: {new_url}')
                driver.get(new_url)
                time.sleep(5)
                url_bs = BeautifulSoup(driver.page_source, 'lxml')
                article_bs = url_bs.find_all('div', class_='col-md-4 col-lg-3 Products__productsFullWide__1COIK Products__productsColumns4__33EJi col-xs-6')

                for article in article_bs:
                    article_url = article.find('a')
                    article_url = article_url['href']
                    article_url_long = 'https://wearmedicine.com' + article_url
                    link_list.append(article_url_long)

        try:
            category = url.split('/')[-1]
            category = category.replace('-', ' ')
            category = category.lower()
            category_sex = url.split('/')[-3]
            if category_sex.find('ona') >= 0:
                category_sex = category_sex.replace('ona', 'D')
            elif category_sex.find('on') >= 0:
                category_sex = category_sex.replace('on', 'M')
            category = category + '_' + category_sex
        except:
            category = None

        print(f'Save to table: {category}')
        products_urls_table = pd.DataFrame(link_list, columns=['url'])
        products_urls_table['Category'] = category
        products_urls_table['Top category'] = category
        products_urls_table['Page url'] = url
        products_urls_final = pd.concat([products_urls_final, products_urls_table])

    products_urls_final = products_urls_final.reset_index(drop=True)

    return products_urls_final


def scrape_data(driver, df_row, row_id, domain, date_today, time_today):
    errors_list = []
    completed_data = []
    error = False
    sizes = []
    top_category = code = name = first_price = discount_price = color = season \
        = composition = product_id = bs = None

    try:
        driver.get(df_row['url'])
        time.sleep(5)
        bs = BeautifulSoup(driver.page_source, 'lxml')
    except:
        print(' Recive URL error', end='')
        errors_list.append('Recive URL error')
        error = True

    if bs is not None:
        try:
            product_main_bs = bs.find('div', class_='col-xs-12 col-md-6 col-lg-5 ProductCard__rightColumn__sxZvD')
        except:
            product_main_bs = None
            print(' Main BS error', end='')
            errors_list.append('Main BS error')
            error = True

        if product_main_bs is None:
            error = True
        elif product_main_bs is not None:
            try:
                name = product_main_bs.find('div', class_='ProductCard__productNameAndLogo__2qh_q').text.strip()
            except:
                name = None
                print(' Name error', end='')
                errors_list.append('Name error')
                error = True

            try:
                color = product_main_bs.find('div', class_='ProductCard__colorPickerWrapperName__3vS4j').text
            except:
                color = None
                print(' Color error', end='')
                errors_list.append('Color error')
                error = True

            try:
                first_price = product_main_bs.find('div', class_='Price__price__3uiSQ Price__priceWithSale__3qOel ProductCard__priceRegularWithSale__1ueWX') \
                    .text.replace('zł', '')
            except:
                first_price = None

            if first_price is not None:
                discount_price = product_main_bs.find('div', class_='Price__salePrice__tkBzg ProductCard__priceSale__2pzav').text
            else:
                first_price = product_main_bs.find('div', class_='Price__price__3uiSQ ProductCard__priceRegular__23hpe').text
                discount_price = None

            if first_price is not None:
                first_price = first_price.replace('zł', '').strip()
                first_price = first_price.replace('.', ',')
            if discount_price is not None:
                discount_price = discount_price.replace('zł', '').strip()
                discount_price = discount_price.replace('.', ',')

            try:
                top_category = df_row['Category']

                if top_category.find('szorty') >= 0:
                    top_category = top_category.replace('szorty', 'Spodenki')
                elif top_category.find('kurtki i plaszcze') >= 0:
                    top_category = top_category.replace('kurtki i plaszcze', 'kurtki')
                elif top_category.find('zakiety i kamizelki') >= 0:
                    top_category = top_category.replace('zakiety i kamizelki', 'Kurtki')
                elif top_category.find('marynarki i kamizelki') >= 0:
                    top_category = top_category.replace('marynarki i kamizelki', 'Kurtki')
                elif top_category.find('koszule i bluzki') >= 0:
                    top_category = top_category.replace('koszule i bluzki', 'Bluzki')
                elif top_category.find('t shirty i topy') >= 0:
                    top_category = top_category.replace('t shirty i topy', 'Koszulki')
                elif top_category.find('t shirty') >= 0:
                    top_category = top_category.replace('t shirty', 'Koszulki')
                elif top_category.find('kombinezony') >= 0:
                    top_category = top_category.replace('kombinezony', 'Sukienki')

                top_category = top_category.capitalize()

            except:
                top_category = None
                print(' Top category error', end='')
                errors_list.append('Top category error')
                error = True

            try:
                description_bs = bs.find('div', class_='col-xs-12 col-md-6 col-lg-7, ProductDetailsInfoTabs__productDetailsInfoTabsContentContainer__R4AyY')
            except:
                description_bs = None

            try:
                p_list = description_bs.find_all('p')
                code = p_list[-1].text
                p_list = description_bs.find_all('span')
                composition = p_list[-1].text.replace('\n', ' ').strip()
                if len(composition) < 2:
                    composition = p_list[-2].text.replace('\n', ' ').strip()
            except:
                code = composition = unique = None
                print(' Code/composition error', end='')
                errors_list.append('Code/composition error')
                error = True

            try:
                code_split = code.split('-')
                season = code_split[0]
                season = season.replace('RS', 'SS 20')
                season = season.replace('RW', 'AW 20')
            except:
                season = None
                print(' Season error', end='')
                errors_list.append('Season error')
                error = True

            try:
                url_list = df_row['url'].split('-')
                product_id = url_list[-1]
            except:
                product_id = None

            try:
                cookies_window = bs.find('div', class_='CookiesInfo__cookiesInfo__3uVY0')
                if cookies_window is not None:
                    cookies_window = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/div/div[3]/button")
                    cookies_window.click()
            except:
                print(' Cookies window error')

            try:
                scroll_button = driver.find_element(By.XPATH,
                                                    '//*[@id="root"]/main/div[2]/div[1]/div/div[2]/div[3]/div[2]/div[1]')
                if scroll_button is not None:
                    scroll_button.click()

                else:
                    time.sleep(5)
                    scroll_button = driver.find_element(By.XPATH,
                                                        "/html/body/div/main/div[2]/div[1]/div/div[2]/div[3]/div[2]/div[1]/i")
                    if scroll_button is not None:
                        scroll_button.click()
                    else:
                        print(' Scroll button error', end='')
                        errors_list.append('Scroll button (timeout) error')
                        error = True
            except:
                print(' Scroll button error', end='')
                errors_list.append('Scroll button error')
                error = True

            try:
                new_bs = BeautifulSoup(driver.page_source, 'lxml')
                sizes_bs = new_bs.find('ul', class_='BaseSelectDropdown__selectList__1vd4p BaseSelectDropdown__selectList__1oYIp')

                for s in sizes_bs.find_all('li'):
                    if 'BaseSelectItem__listItemUnavailable__3rLI0' in set(s["class"]):
                        sizes_text = s.text.replace('Powiadom o dostępności', ': not available')
                        sizes.append(sizes_text)
                    elif 'BaseSelectItem__listItem__1O_G7' in set(s["class"]):
                        sizes_text = str(s.text)
                        sizes_text = sizes_text + ': available'
                        if sizes_text.find('Ostatnia sztuka!') >= 0:
                            sizes_text = sizes_text.replace('Ostatnia sztuka!', '')
                        sizes.append(sizes_text)
                    else:
                        sizes_text = str(s.text)
                        sizes_text = sizes_text + ': OTHER'
                        sizes.append(sizes_text)
            except:
                print(' Sizes error', end='')

            try:
                product_image = bs.find('div', class_='ProductCard__slickArrowTheme__E06H4 Gallery__galleryWrapper__uSaCl')
                product_image = product_image.find('div', class_='Image__media__2XtKT')
                product_image = product_image.find('img')['src']
            except:
                product_image = None

    else:
        print(' Product BS error', end='')
        errors_list.append('Product BS error')
        error = True

    if error is True:
        sizes = errors_list
        top_category = code = name = first_price = discount_price = color = season = \
            composition = product_id = product_image = None

    completed_data = [row_id, date_today, time_today, df_row['Page url'], df_row['url'], domain,
                      top_category, df_row['Category'], code, name,
                      first_price, discount_price, color, season, composition,
                      sizes, product_id, code, product_image]

    return completed_data, error
