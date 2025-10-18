import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

companies = {
    'sber': '3043',
    'gazprom': '934',
    'lukoil': '17',
    'magnit': '7671',
    'positive_technologies': '38196'
}

years = ['"2024"', '"2023"', '"2022"', '"2021"', '"2020"', '"2019"', '"2018"']

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

for company in companies:
    driver.get(f"https://www.e-disclosure.ru/portal/company.aspx?id={companies[company]}")
    full = []

    for year in years:
        a = f'a[data-event-year={year}]'
        if year == '"2024"':
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, a))).click()
            continue
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, a))).click()
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="tabs"]//tr')))
        rows = driver.find_elements(By.XPATH, '//div[@class="tabs"]//tr')
        
        for row in rows[1:]:
            date_event = row.find_element(By.XPATH, './td[1]').text
            news_released = row.find_element(By.XPATH, './td[2]').text
            news_header = row.find_element(By.XPATH, './td[3]').text
            news_link = row.find_element(By.XPATH, './td[3]/a').get_attribute('href')

            # Открываем ссылку на новость в новой вкладке и извлекаем полный текст
            driver.execute_script("window.open(arguments[0]);", news_link)
            driver.switch_to.window(driver.window_handles[1])
            
            # Ожидаем появления полного текста новости
            news_full_text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@style="word-break: break-word; word-wrap: break-word; white-space: pre-wrap;"]'))
            ).text
            
            # Сохраняем данные
            exact_article = [date_event, news_released, news_header, news_link, news_full_text]
            full.append(exact_article)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Создаем DataFrame и сохраняем его в Excel
    df = pd.DataFrame(full, columns=['Event_occured', 'News_released', 'Header', 'Link', 'Full_news'])
    df.to_excel(f'{company}_news_last.xlsx', index=False)