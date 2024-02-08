import json
import re

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

def wait_element(browser, delay_seconds=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


browser = Chrome()

parsed_data = []

def get_vacancy_informaition(vacancies_link, browser):
    browser.get(vacancies_link)
    serp_content = wait_element(
        browser, 1, By.CLASS_NAME, "vacancy-serp-content"
    )
    vacancy_list = serp_content.find_elements(By.CLASS_NAME, "serp-item")
    for vacancy_tag in vacancy_list:
        h3_tag = wait_element(vacancy_tag, 1, By.TAG_NAME, "h3")
        a_tag = h3_tag.find_element(By.TAG_NAME, "a")
        vacancy_name_tag = a_tag.find_element(By.TAG_NAME, "span")
        employer_tag = vacancy_tag.find_element(By.CLASS_NAME, "bloko-link")
        address_tag = vacancy_tag.find_elements(By.CLASS_NAME, "bloko-text")[1]
        try:
            compensation_tag = vacancy_tag.find_element(By.CLASS_NAME, "bloko-header-section-2")
            vacancy_compensation = compensation_tag.text
        except NoSuchElementException:
            vacancy_compensation = "Не указано"

        vacancy_employer = employer_tag.text
        vacancy_address = address_tag.text
        link_absolute = a_tag.get_attribute("href")
        vacancy_name = vacancy_name_tag.text

        if (re.findall(r"django", vacancy_name, re.I | re.M)
                or re.findall(r"flask", vacancy_name, re.I | re.M)):
            parsed_data.append(
                {
                    "employer": vacancy_employer,
                    "address": vacancy_address,
                    "compensation": vacancy_compensation,
                    "link": link_absolute,
                }
            )

    print('Парсинг завершен')

vacancies_link = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
get_vacancy_informaition(vacancies_link, browser)

with open("vacancies_file.json", "w", encoding="utf-8") as f:
    json.dump(parsed_data, f, ensure_ascii=False, indent=2)
