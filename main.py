from datetime import datetime
import time
import pandas as pd
import File_Manager
import Driver_Manager
import Reserved
import HnM
import Medicine
import House

invalid_check = True
option_chosen = 0
domain = ''
urls_df = pd.DataFrame()

print('2. H&M')
print('3. Medicine')
print('4. Reserved')
print('5. Sinsay')
print('6. House')

while invalid_check is True:
    try:
        option_chosen = int(input('What to scrape: '))
        if option_chosen > 6:
            invalid_check = True
            print('Invalid input.')
        elif option_chosen != 0:
            invalid_check = False
    except:
        print('Invalid input.')
        invalid_check = True

date_file = datetime.now().strftime("%d-%m-%Y")
driver = Driver_Manager.set_driver()

if option_chosen == 2:
    domain = 'HnM'
    urls = File_Manager.read_urls(domain)
    urls_df = HnM.get_urls(driver, urls)
elif option_chosen == 3:
    domain = 'Medicine'
    urls = File_Manager.read_urls(domain)
    urls_df = Medicine.get_urls(driver, urls)
elif (option_chosen == 4) or (option_chosen == 5):
    if option_chosen == 4:
        domain = 'Reserved'
    elif option_chosen == 5:
        domain = 'Sinsay'
    print('Domain')
    urls = File_Manager.read_urls(domain)
    urls_df = Reserved.get_urls(driver, urls)
elif option_chosen == 6:
    domain = 'House'
    urls = File_Manager.read_urls(domain)
    urls_df = House.get_urls(driver, urls)


File_Manager.create_file(domain, date_file)

for i, df_row in urls_df.iterrows():
    error_check = True
    error_count = 0
    product_data = []
    while error_check is True:
        time_today = datetime.now().strftime("%H:%M:%S")
        date_today = datetime.now().strftime("%d-%m-%Y")
        print(f"{time_today} {i + 1}/{len(urls_df)} {df_row['Top category']} {df_row['url']}", end='')
        if domain == 'Diverse':
            product_data, error_check = Diverse.scrape_data(driver, df_row, i, domain)
        elif domain == 'HnM':
            product_data, error_check = HnM.scrape_data(driver, df_row, i, domain)
        elif domain == 'Medicine':
            product_data, error_check = Medicine.scrape_data(driver, df_row, i, domain, date_today, time_today)
        elif (domain == 'Reserved') or (domain == 'Sinsay'):
            product_data, error_check = Reserved.scrape_data(driver, df_row, i, domain)
        elif domain == 'House':
            product_data, error_check = House.scrape_data(driver, df_row, i, domain)

        if error_check is False:
            save_error = True
            save_error_count = 0
            while save_error is True:
                try:
                    File_Manager.save_to_file(domain, product_data, date_file)
                    print(' Done')
                    save_error = False
                except:
                    print(' Save error')
                    save_error = True
                    save_error_count = save_error_count +1
                if save_error_count >= 5:
                    save_error = False
                    error_check = True
                    product_data[15] = 'Save error'
        if error_check is True:
            product_data[6] = product_data[7] = product_data[9] = product_data[10] = \
                product_data[11] = product_data[12] = product_data[13] = product_data[14] = \
                product_data[16] = product_data[17] = None
            product_data[8] = 'Error occurred'
            File_Manager.save_to_file(domain, product_data, date_file)
            driver.quit()
            driver = Driver_Manager.set_driver()
            error_count = error_count + 1
            print(f' {error_count}')

        if error_count >= 5:
            error_check = False
            print(" Didn't scrape")

driver.quit()
