import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


LANGUAGES = [
    'typescript', 'swift', 'scala' #, 'objective-c', 'shell', 'go', 
    # 'c#', 'c++', 'php', 'ruby', 'python', 'java', 'javascript'
]
RUSSIA = '113'
url_hh = 'https://api.hh.ru/vacancies'
url_sj = 'https://api.superjob.ru/2.0/vacancies'


def form_search_query_hh(language):
    """This function creates dict of options for request through API hh.ru. """
    search_query = 'программист москва {}'.format(language)
    query={'text':search_query, 'area':RUSSIA}
    return query

def count_it_vacancies_hh(language):
    """This function calculates count of it vacancies through API hh.ru."""
    query = form_search_query_hh(language)
    response = requests.get(url_hh, params=query)
    response.raise_for_status()
    return ((response.json()['pages'], response.json()['found']))
    
def collect_it_vacancies_hh(language):
    """This function collects vacancies across programming languages through API hh.ru."""
    query = form_search_query_hh(language)
    vacancies = []
    page = 0
    total_pages = count_it_vacancies_hh(language)[0]
    if total_pages:
        while  page < total_pages:
            query['page'] = page
            response = requests.get(url_hh, params=query)
            response.raise_for_status()
            vacancies.extend(response.json()['items'])
            page += 1
    else:
        None
    return vacancies

def get_spreads_of_salary_for_language_hh(language):
    """This function gives spreads of salary.""" 
    vacancies = collect_it_vacancies_hh(language)
    salaries = [salary['salary'] for salary in vacancies]
    salaries_rur = []
    for salary in salaries:
        try:
            if salary['currency'] != 'RUR':
                    continue
            salaries_rur.append((salary['from'], salary['to']))
        except TypeError:
            continue
    return salaries_rur
    
def predict_salary(salary_from, salary_to):
    """This function computes average salary through API hh.ru or sj.ru."""
    if salary_from is not None and salary_to is not None:
        salary_semisum = (salary_from + salary_to)*0.5
    elif salary_from is None:
        salary_semisum = salary_to*0.8
    elif salary_to is None:
        salary_semisum = salary_from*1.2
    return salary_semisum

def create_dataset_hh(language):
    """This function creates a dict of vacancies and avegare salary through API hh.ru."""
    salary_spreads = get_spreads_of_salary_for_language_hh(language)
    salary_count = [predict_salary(salary_from, salary_to) for 
        salary_from, salary_to in salary_spreads]
    if len(salary_count) > 0:
        average_rub_salary = int(sum(salary_count)/len(salary_count))
    else:
        average_rub_salary = 0
    vacancies_salary_by_language = {
        'vacancies_found':count_it_vacancies_hh(language)[1], 
        'vacancies_processed':len(salary_count),
        'average_salary':average_rub_salary
    }
    return vacancies_salary_by_language

def build_table_hh(LANGUAGES):
    """This function builds a data table from sj.ru data."""
    title = 'HeadHunter Moscow'
    dataset_for_all_languages = {language:create_dataset_hh(language) for 
        language in LANGUAGES}
    table_content = [['language', 'vacancies_found', 'vacancies_processed', 
        'average_salary']]
    for language, data in dataset_for_all_languages.items():
        table_row = [language]
        table_row.extend(data.values())
        table_content.append(table_row)
    return AsciiTable(table_content, title).table
     
def count_it_vacancies_sj(language, api_headers):
    """This function calculates count of it vacancies through API sj.ru."""
    search_language = '{}'.format(language)
    headers=api_headers
    response = requests.get(url_sj, params={'keywords':['программист', 
        search_language], 'catalogues':'Разработка, программирование', 
        'period':30, 'town':4}, headers=api_headers)
    response.raise_for_status()
    return response.json()['total']
    
def collect_it_vacancies_sj(language, api_headers):
    """This function collects all vacancies across programming languages through API sj.ru."""
    search_language = '{}'.format(language)
    headers=api_headers
    vacancies = []
    total_vacancies = count_it_vacancies_sj(language, api_headers)
    if total_vacancies:
        total_pages = total_vacancies//20 + 1
    else: 
        total_pages = 0
    for page in range(total_pages):
        response = requests.get(url_sj, params={'keywords':['программист', 
            search_language], 'catalogues':'Разработка, программирование', 
            'period':30, 'town':4, 'page':page}, headers=api_headers)
        response.raise_for_status()
        for item in response.json()['objects']:
            vacancies.append(item)
    return vacancies

def get_spreads_of_salary_for_language_sj(language, api_headers):
    """This function gives spreads of salary through API sj.ru."""
    list_of_it_vacancies = collect_it_vacancies_sj(language, api_headers)
    salary_spreads = [(item['payment_from'], item['payment_to']) for item 
        in list_of_it_vacancies]
    return salary_spreads

def create_dataset_sj(language, api_headers):
    """This function creates a dict of vacancies and avegare salary through API sj.ru."""
    salary_spreads = get_spreads_of_salary_for_language_sj(language, api_headers)
    salary_count = [predict_salary(salary_from, salary_to) for (salary_from, 
        salary_to) in salary_spreads if all((salary_from, salary_to)) != 0]
    if len(salary_count) > 0:
        average_rub_salary = int(sum(salary_count)/len(salary_count))
    else:
        average_rub_salary = 0
    vacancies_salary_by_language = {
        'vacancies_found':count_it_vacancies_sj(language, api_headers),
        'vacancies_processed':len(salary_count),
        'average_salary':average_rub_salary
    }
    return vacancies_salary_by_language

def build_table_sj(LANGUAGES, api_headers):
    """This function builds a data table from sj.ru data."""
    title = 'SuperJob Moscow'
    dataset_for_all_languages = {language:create_dataset_sj(language, 
        api_headers) for language in LANGUAGES}
    table_content = [['language', 'vacancies_found', 'vacancies_processed', 
        'average_salary']]
    for language, data in dataset_for_all_languages.items():
        table_row = [language]
        table_row.extend(data.values())
        table_content.append(table_row)
    return AsciiTable(table_content, title).table

def main(): 
    """This function prints two data tables from hh.ru and sj.ru data."""
    try:
        print(build_table_hh(LANGUAGES))
        print(build_table_sj(LANGUAGES, api_headers))
    except requests.RequestException as err:
        print(err.response)


if __name__ == '__main__':
    
    load_dotenv()

    token = os.getenv('token')
    api_headers = {
        'X-Api-App-Id':str(token)
    }
 
    main()
