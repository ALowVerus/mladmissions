from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import json
from time import sleep
import os


def import_secrets(prefix):
    with open(prefix + "secrets.json", "r") as file:
        keys = json.load(file)
        file.close()
    naviance_username = keys["naviance"]["username"]
    naviance_password = keys["naviance"]["password"]
    return naviance_username, naviance_password


def get_elem(browser, attribute, my_attr, delay=5):
    if attribute == "CLASS_NAME":
        target = By.CLASS_NAME
    elif attribute == "ID":
        target = By.ID
    elif attribute == "TAG_NAME":
        target = By.TAG_NAME
    elif attribute == "NAME":
        target = By.NAME
    else:
        target = By.XPATH
    my_elem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((target, my_attr)))
    return my_elem


def login(browser, prefix):
    naviance_username, naviance_password = import_secrets(prefix)
    browser.get("https://student.naviance.com/sww")
    elem = get_elem(browser, "TAG_NAME", "form")
    username_input = elem.find_element_by_id("username")
    password_input = elem.find_element_by_id("password")
    submit_input = elem.find_element_by_class_name("_2qIuE8s2")
    username_input.send_keys(naviance_username)
    password_input.send_keys(naviance_password)
    submit_input.click()
    sleep(1)


def main_pull_naviance():
    prefix = os.path.dirname(os.path.realpath(__file__)) + "/"

    # Make your driver
    driver = webdriver.Chrome()

    # Log into UBS
    login(driver, prefix)

    # Get data
    college_list = [
        "Dartmouth College",
        "Colby College",
        "Northeastern University",
        "Harvard College",
        "Columbia University",
        "Princeton University",
        "Brown University"
    ]

    # Get college links in Naviance
    college_link_dict = {}
    for college in college_list:
        done = False
        while not done:
            driver.get("https://student.naviance.com/main")
            search_form = get_elem(driver, "CLASS_NAME", "_2PJKifxu")
            search_form = search_form.find_element_by_tag_name("form")
            search_bar = search_form.find_element_by_class_name("hVydLG8s")
            search_bar = search_bar.find_element_by_tag_name("input")
            search_bar.send_keys(college)
            search_button = search_form.find_element_by_class_name("fUerpKNk")
            search_button.click()
            # Swaps over to possible search results
            try:
                results_table = get_elem(driver, "CLASS_NAME", "_1i56oIA3")
                top_result = results_table.find_elements_by_tag_name("tr")[1]
                college_link = top_result.find_element_by_tag_name("a").get_attribute("href")
                college_link_dict[college] = college_link
                done = True
            except WebDriverException:
                pass
    # Save data for later
    with open(prefix + "college_link_dict.json", "w") as fp:
        json.dump(college_link_dict, fp, indent=2)
        fp.close()

    # Grab data
    admissions_info_dict = {}
    for college, college_link in college_link_dict.items():
        college_identifier = college_link[33:]
        json_link = "https://fc-hubs-app.naviance.com/schools/scattergrams?collegeId=" + college_identifier
        driver.get(json_link)
        json_content = get_elem(driver, "TAG_NAME", "pre").get_attribute("innerHTML")
        json_stuff = json.loads(json_content)["scores"]
        admissions_info_dict[college] = json_stuff

    # Pre-process data
    for college, scores in admissions_info_dict.items():
        for score in scores:
            del score["sat1600"]
            del score["legacyStudentId"]
            if score["waitlisted"] == 1:
                score["resultCode"] = 2
            del score["waitlisted"]
            if score["deferred"] == 1:
                score["resultCode"] = 2
            del score["deferred"]
            if score["satConcorded"] == score["sat2400"] == score["act"] == 0:
                score["resultCode"] = 3
        newScores = []
        for score in scores:
            if score["resultCode"] == 1 or score["resultCode"] == 2:
                newScores.append(score)
        admissions_info_dict[college] = newScores

    # Save data for later
    with open(prefix + "admissions_info_dict.json", "w") as fp:
        json.dump(admissions_info_dict, fp, indent=2)
        fp.close()

    # Exit
    driver.close()


if __name__ == '__main__':
    main_pull_naviance()
