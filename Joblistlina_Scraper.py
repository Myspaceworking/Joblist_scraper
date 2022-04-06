import json
import requests
import os
import glob
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://www.jobstreet.co.id/id/job-search/computer-information-technology-jobs/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}


def get_total_pages():
    pages = []
    r = requests.get(url, headers=headers)

    # temp file
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    f = open('temp/pages.html', 'w+', encoding="utf-8")
    f.write(r.text)
    f.close()

    soup = BeautifulSoup(r.text, 'html.parser')

    pagination = soup.find('select', attrs={'id': 'pagination'}).find_all('option')
    for num in pagination:
        if num.text.isnumeric():
            pages.append(int(num.text))

    total_pages = max(pages)
    print(f"Total Page found {total_pages}")
    return total_pages


def get_all_items(num):
    url = f'https://www.jobstreet.co.id/id/job-search/computer-information-technology-jobs/{num}'
    base_url = 'https://www.jobstreet.co.id'
    joblist = []
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    contents = soup.find_all('div', attrs={
        'class': 'sx2jih0 zcydq876 zcydq866 zcydq896 zcydq886 zcydq8n zcydq856 zcydq8f6 zcydq8eu'})
    print("Total Item: {}".format(len(contents)))

    # proses data
    for content in contents:
        title = content.find('div', attrs={'class': 'sx2jih0 l3gun70 l3gun74 l3gun72'}).text
        link = content.find('a')['href']

        data_dict = {
            'title': title,
            'link': base_url + link
        }
        joblist.append(data_dict)

    # data append
    print("Total Data: {}".format(len(joblist)))
    return joblist


def get_detail( url):
    qualified_list = []
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # temp file
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass

    f = open('temp/detail_page.html', 'w+', encoding="utf-8")
    f.write(r.text)
    f.close()


    try:
        contents = soup.find("div", attrs={'class': 'sx2jih0'}).find('ul').find_all('li')
    except:
        contents = soup.find_all('div', attrs={'style': 'text-align:justify'})

    # process the data
    for content in contents:
        qualified = content.text
        qualified_list.append(qualified)

    return qualified_list


def extract_data(num):
    results = []
    items = get_all_items(num)
    for index, item in enumerate(items, start=1):
        print("getting data {} of {} URL {}".format(index, len(items), item['link']))
        qualified = get_detail(item['link'])
        item['qualified'] = qualified
        results.append(item)

    try:
        os.mkdir("json_data")
    except FileExistsError:
        pass
    with open("json_data/jobs_page_{}.json".format(num), 'w+') as json_file:
        json.dump(results, json_file)

    print("Json Data for page {} writted".format(num))

    return results

# extract json
def extract_json():
   files = sorted(glob.glob("json_data/*.json"))
   for file in files:
       print(file)


def generate_data(results_list):
    df = pd.DataFrame(results_list)
    df.to_csv('results.csv', index=False)

def run():
    results = []
    total_pages = get_total_pages()
    for page in range(total_pages):
        page += 1
        print(f"Extract data from page: {page}")
        extract = extract_data(num=page)
        results += extract

    # creating report
    generate_data(results)


if __name__ == '__main__':
  extract_json()
