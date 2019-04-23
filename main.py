import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


LANGUAGES = [
    'typescript' 'swift', 'scala', 'objective-c', 'shell', 'go', 
    'c#', 'c++', 'php', 'ruby', 'python', 'java'
]
RUSSIA = '113'
url_hh = 'https://api.hh.ru/vacancies'
url_sj = 'https://api.superjob.ru/2.0/vacancies'


def form_search_query_hh(language):
    """This function creates dict of options for request through API hh.ru. """
    search_query = 'программист москва {}'.format(language)
    query={'text':search_query, 'area':RUSSIA}
    return query

def collect_it_vacancies_hh(language):
    """This function collect vacancies across programming languages through API hh.ru."""
    answer = []
    page = pages_number = 0
    query = form_search_query_hh(language)
    url = url_hh
    while page <= pages_number:
        query['page'] = page
        response = requests.get(url, params=query)
        try:
            response.raise_for_status()
            pages_number = response.json()['pages']
            answer.append(response.json())
            page += 1
        except requests.RequestException as err:
            print(err.response)
    return answer

def count_it_vacancies_hh(language):
    """This function calcalates count of it vacancies through API hh.ru."""
    query = form_search_query_hh(language)
    url = url_hh
    response = requests.get(url, params=query)
    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err.response)
    return response.json()['found']

def get_spreads_of_salary_for_language_hh(language):
    """This function gives spreads of salary.""" 
    salary_spreads = []
    for vacancy in collect_it_vacancies_hh(language):
        for salary in vacancy['items']:
            salary_spreads.append(salary['salary'])
    salary_estimates = []
    for salary in salary_spreads:
        try:
            if salary['currency'] != 'RUR':
                    continue
            else:
                if None:
                    continue
                elif salary['from'] and salary['to']:
                    salary_estimates.append((salary['from'], salary['to']))
                elif salary['from'] is None:
                    salary_estimates.append((0, salary['to']))
                elif salary['to'] is None:
                    salary_estimates.append((salary['from'], 0))
        except TypeError:
            continue
    return salary_estimates

def predict_salary(salary_from, salary_to):
    """This function computes average salary through API hh.ru or sj.ru."""
    if salary_from != 0 and salary_to != 0:
        salary_semisum = (salary_from + salary_to)*0.5
    elif salary_from == 0:
        salary_semisum = salary_to*0.8
    elif salary_to == 0:
        salary_semisum = salary_from*1.2
    return salary_semisum

def predict_rub_salary_hh(language):
    """This function calculates selisums of salary by vacancies."""    
    salary_spreads = get_spreads_of_salary_for_language_hh(language)
    salary_predicts = []
    for salary_from, salary_to in salary_spreads:
        salary_predicts.append(predict_salary(salary_from, salary_to))
    return (salary_predicts, len(salary_predicts))

def create_dataset_hh(language):
    """This function creates a dict of vacancies and avegare salary through API hh.ru."""
    salary, salary_length = predict_rub_salary_hh(language)
    salary_count = [salary_value for salary_value in salary]
    if salary_length > 0:
        average_rub_salary = int(sum(salary_count)/salary_length)
    vacancies_salary_by_language = {}
    vacancies_salary_by_language['vacancies_found'] = count_it_vacancies_hh(language)
    vacancies_salary_by_language['vacancies_processed'] = salary_length
    vacancies_salary_by_language['average_salary'] = average_rub_salary
    return vacancies_salary_by_language

def build_and_print_table_hh(LANGUAGES):
    """This function builds a data table from sj.ru data."""
    title = 'HeadHunter Moscow'
    dataset_for_all_languages = {language:create_dataset_hh(language) 
        for language in LANGUAGES}
    table_content = []
    table_content.append(['language', 'vacancies_found', 'vacancies_processed', 'average_salary'])
    for language, data in dataset_for_all_languages.items():
        table_data = [language]
        data = [value for value in data.values()]
        table_data.extend(data)
        table_content.append(table_data)
    print(AsciiTable(table_content, title).table)

def count_it_vacancies_sj(language, api_headers):
    """This function calcalates count of it vacancies through API sj.ru."""
    search_language = '{}'.format(language)
    url = url_sj
    headers=api_headers
    response = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4}, 
        headers=api_headers)
    try:
        response.raise_for_status()
    except requests.RequestException as err:
        print(err.response)
    return response.json()['total']

def collect_it_vacancies_sj(language, api_headers):
    """This function collect all vacancies across programming languages through API sj.ru."""
    search_language = '{}'.format(language)
    url = url_sj
    headers=api_headers
    it_vacancies = []
    total_vacancies = count_it_vacancies_sj(language, api_headers)
    total_pages = total_vacancies//20 + 1
    for page in range(total_pages):
        response = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4, 'page':page}, 
            headers=api_headers)
        try:
            response.raise_for_status()
            for item in response.json()['objects']:
                it_vacancies.append(item)
        except requests.RequestException as err:
            print(err.response)
    return it_vacancies

def get_spreads_of_salary_for_language_sj(language, api_headers):
    """This function gives spreads of salary through API sj.ru."""
    list_of_it_vacancies = collect_it_vacancies_sj(language, api_headers)
    salary_spreads = [(item['payment_from'], item['payment_to']) 
    for item in list_of_it_vacancies]
    return salary_spreads

def predict_rub_salary_sj(language, api_headers):
    """This function computes average salary for language through API sj.ru."""
    salary_spreads = get_spreads_of_salary_for_language_sj(language, api_headers)
    salary_predicts = []
    for salary_from, salary_to in salary_spreads:
        salary_predicts.append(predict_salary(salary_from, salary_to))
    return (salary_predicts, len(salary_predicts))
        
def create_dataset_sj(language, api_headers):
    """This function creates a dict of vacancies and avegare salary through API sj.ru."""
    data_salary, len_salary = predict_rub_salary_sj(language, api_headers)
    salary_count_list = [salary for salary in data_salary]
    if len_salary > 0:
        average_rub_salary = int(sum(salary_count_list)/len_salary)
    else:
        average_rub_salary = 0
    vacancies_salary_by_language = {}
    vacancies_salary_by_language['vacancies_found'] = count_it_vacancies_sj(language, 
        api_headers)
    vacancies_salary_by_language['vacancies_processed'] = len_salary
    vacancies_salary_by_language['average_salary'] = average_rub_salary
    return vacancies_salary_by_language

def build_and_print_table_sj(LANGUAGES, api_headers):
    """This function builds a data table from sj.ru data."""
    title = 'SuperJob Moscow'
    dataset_for_all_languages = {language:create_dataset_sj(language, api_headers) 
        for language in LANGUAGES}
    table_content = []
    table_content.append(['language', 'vacancies_found', 'vacancies_processed', 'average_salary'])
    for language, data in dataset_for_all_languages.items():
        table_data = [language]
        data = [value for key, value in data.items()]
        table_data.extend(data)
        table_content.append(table_data)
    print(AsciiTable(table_content, title).table)

def show_tables_of_all_sources(LANGUAGES, api_headers):
    """This function print two data tables from hh.ru and sj.ru data."""
    build_and_print_table_hh(LANGUAGES)
    build_and_print_table_sj(LANGUAGES, api_headers)
    

if __name__ == '__main__':
    
    load_dotenv()

    token = os.getenv('token')
    api_headers = {
        'X-Api-App-Id':str(token)
    }
 
    
    show_tables_of_all_sources(LANGUAGES, api_headers)
    