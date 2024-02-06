import json
import re
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def wait_element(browser, delay_seconds=1, by=By.TAG_NAME, value=None):
    return WebDriverWait(browser, delay_seconds).until(
        expected_conditions.presence_of_element_located((by, value))
    )


path = ChromeDriverManager().install()
browser_service = Service(executable_path=path)
browser = Chrome(service=browser_service)

parsed_data = []

def get_vacancy_informaition(vacancies_link, browser):
    browser.get(vacancies_link)
    main_serp_content = wait_element(browser, 1, By.CLASS_NAME, "vacancy-serp-content")
    vacancy_list = main_serp_content.find_element(By.ID, "a11y-main-content")
    for vacancy_tag in vacancy_list.find_elements(By.CLASS_NAME, "serp-item"):
        h3_tag = wait_element(vacancy_tag, 1, By.TAG_NAME, "h3")
        a_tag = h3_tag.find_element(By.TAG_NAME, "a")
        vacancy_name_tag = a_tag.find_element(By.TAG_NAME, "span")
        employer_tag = vacancy_tag.find_element(By.CLASS_NAME, "bloko-link bloko-link_kind-tertiary")
        address_tag = vacancy_tag.find_element(By.CLASS_NAME, "vacancy-serp__vacancy-address")
        compensation_tag = vacancy_tag.find_element(By.CLASS_NAME, "bloko-header-section-2")

        vacancy_employer = employer_tag.text
        vacancy_address = address_tag.text
        link_absolute = a_tag.get_attribute("href")
        vacancy_name = vacancy_name_tag.text

        if compensation_tag is not None:
            vacancy_compensation = compensation_tag.text
        else:
            vacancy_compensation = "Не указано"

        if (re.findall(r"$", vacancy_compensation) and
            (re.findall(r"django", vacancy_name, re.I|re.M) or re.findall(r"flask", vacancy_name, re.I|re.M))):
            parsed_data.append(
                {
                    "employer": vacancy_employer,
                    "address": vacancy_address,
                    "compensation": vacancy_compensation,
                    "link": link_absolute,
                }
            )

    pager_tag = main_serp_content.find_element(By.CLASS_NAME, "pager")
    next_page_button_tag = pager_tag.find_element(By.TAG_NAME, "a")
    next_page_link = next_page_button_tag.get_attribute("href")

    return next_page_link

vacancies_link = "https://spb.hh.ru/search/vacancy?text=python&area=1&area=2"
next_page = get_vacancy_informaition(vacancies_link, browser)

flag = True
while flag:
    next_page = get_vacancy_informaition(next_page, browser)
    if next_page is None:
        flag = False

with open('vacancies_file.json', 'w') as f:
    json.dump(parsed_data, f, indent=2)
