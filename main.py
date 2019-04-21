import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable

load_dotenv()

token = os.getenv('token')
api_headers = {
    'X-Api-App-Id':str(token)
}

languages=[
    'typescript', 'swift', 'scala', 'objective-c', 'shell', 'go', 
    'c#', 'c++', 'php', 'ruby', 'python', 'java', 'javascript'
]


def form_search_options_hh(language):
    """This function creates dict of options for request through API hh.ru. """
    search_options = 'программист москва {}'.format(language)
    options={'text':search_options, 'area':'113'}
    return options

def collect_it_vacancies_hh(language):
    """This function collect vacancies across programming languages through API hh.ru."""
    json_format_answer = []
    page = pages_number = 1
    while page <= pages_number:
        options = form_search_options_hh(language)
        url = 'https://api.hh.ru/vacancies'
        response = requests.get(url, params=options).json()
        pages_number = response['pages']
        page += 1
        json_format_answer.append(response)
    return json_format_answer

def count_it_vacancies_hh(language):
    """This function calcalates count of it vacancies through API hh.ru."""
    options = form_search_options_hh(language)
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=options).json()
    return response['found']

def get_spreads_of_salary_for_language_hh(language):
    """This function gives spreads of salary.""" 
    for item_of_list in collect_it_vacancies_hh(language):
        salary_spreads = [item['salary'] for item in item_of_list['items']]
    return salary_spreads

def predict_rub_salary_hh(language):
    """This function computes average salary through API hh.ru."""
    salary_spreads = get_spreads_of_salary_for_language_hh(language)
    salary_estimates = []
    for salary in salary_spreads:
        try:
            if salary['currency'] != 'RUR':
                    continue
            else:
                if None:
                    continue
                elif salary['from'] and salary['to']:
                    salary_estimates.append((salary['from'] + salary['to'])*0.5)
                elif salary['from'] is None:
                    salary_estimates.append(salary['to']*0.8)
                elif salary['to'] is None:
                    salary_estimates.append(salary['from']*1.2)
        except TypeError:
            continue
    estimates_and_len_of_salary = (salary_estimates, len(salary_estimates))
    return estimates_and_len_of_salary

def create_dataset_for_one_language_hh(language):
    """This function creates a dict of vacancies and avegare salary through API hh.ru."""
    data_salary, len_salary = predict_rub_salary_hh(language)
    salary_count_list = [salary for salary in data_salary]
    if len_salary > 0:
        average_rub_salary = int(sum(salary_count_list)/len_salary)
    vacancies_salary_by_language = {}
    vacancies_salary_by_language['vacancies_found'] = count_it_vacancies_hh(language)
    vacancies_salary_by_language['vacancies_processed'] = len_salary
    vacancies_salary_by_language['average_salary'] = average_rub_salary
    return vacancies_salary_by_language

def create_dataset_for_all_languages_hh(languages):
    """This function creates a dict for all languages through API hh.ru."""
    dataset_for_all_languages = {}
    for language in languages:
        dataset_for_all_languages[language] = create_dataset_for_one_language_hh(language)
    return dataset_for_all_languages

def build_and_print_table_of_data_hh(languages):
    """This function builds a data table from sj.ru data."""
    title = 'HeadHunter Moscow'
    dataset = create_dataset_for_all_languages_hh(languages)
    table_content = []
    table_content.append(['language', 'average_salary', 'vacancies_found', 'vacancies_processed'])
    for language, data in dataset.items():
        table_data = [language]
        data = [value for key, value in data.items()]
        table_data.extend(data)
        table_content.append(table_data)
    print(AsciiTable(table_content, title).table)

def count_it_vacancies_sj(language, api_headers):
    """This function calcalates count of it vacancies through API sj.ru."""
    search_language = '{}'.format(language)
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers=api_headers
    list_of_it_vacancies = []
    total_vacancies = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4}, 
        headers=api_headers).json()['total']
    return total_vacancies

def collect_it_vacancies_sj(language, api_headers):
    """This function collect all vacancies across programming languages through API sj.ru."""
    search_language = '{}'.format(language)
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers=api_headers
    list_of_it_vacancies = []
    total_vacancies = count_it_vacancies_sj(language, api_headers)
    total_pages = total_vacancies//20 + 1
    for page in range(total_pages):
        response = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4, 'page':page}, 
            headers=api_headers).json()
        for item in response['objects']:
            list_of_it_vacancies.append(item)
    return list_of_it_vacancies

def get_spreads_of_salary_for_language_sj(language, api_headers):
    """This function gives spreads of salary through API sj.ru."""
    list_of_it_vacancies = collect_it_vacancies_sj(language, api_headers)
    salary_spreads = [(item['payment_from'], item['payment_to']) 
    for item in list_of_it_vacancies]
    return salary_spreads

def predict_rub_salary_sj(language, api_headers):
    """This function computes average salary for language through API sj.ru."""
    salary_spreads = get_spreads_of_salary_for_language_sj(language, api_headers)
    salary_estimates = []
    for salary in salary_spreads:
        salary_from, salary_to = salary
        if salary_from != 0 and salary_to != 0:
            salary_estimates.append((salary_from + salary_to)*0.5)
        elif salary_from != 0:
            salary_estimates.append(salary_from*1.2 )
        elif salary_to != 0:
            salary_estimates.append(salary_to*0.8)
    estimates_and_len_of_salary = (salary_estimates, len(salary_estimates))
    return estimates_and_len_of_salary
        
def create_dataset_for_one_language_sj(language, api_headers):
    """This function creates a dict of vacancies and avegare salary through API sj.ru."""
    data_salary, len_salary = predict_rub_salary_sj(language, api_headers)
    salary_count_list = [salary for salary in data_salary]
    if len_salary > 0:
        average_rub_salary = int(sum(salary_count_list)/len_salary)
    else:
        average_rub_salary = 0
    dict_vacancies_salary_by_language = {}
    dict_vacancies_salary_by_language['vacancies_found'] = count_it_vacancies_sj(language, 
        api_headers)
    dict_vacancies_salary_by_language['vacancies_processed'] = len_salary
    dict_vacancies_salary_by_language['average_salary'] = average_rub_salary
    return dict_vacancies_salary_by_language

def create_dataset_for_all_languages_sj(languages, api_headers):
    """This function creates a dict for all languages through API sj.ru."""
    dict_for_all_languages = {}
    for language in languages:
        dict_for_all_languages[language] = create_dataset_for_one_language_sj(language, api_headers)
    return dict_for_all_languages

def build_and_print_table_of_data_sj(languages, api_headers):
    """This function builds a data table from sj.ru data."""
    title = 'SuperJob Moscow'
    dataset = create_dataset_for_all_languages_sj(languages, api_headers)
    table_content = []
    table_content.append(['language', 'average_salary', 'vacancies_found', 'vacancies_processed'])
    for language, data in dataset.items():
        table_data = [language]
        data = [value for key, value in data.items()]
        table_data.extend(data)
        table_content.append(table_data)
    print(AsciiTable(table_content, title).table)

def show_tables_of_all_sources(
    languages, api_headers):
    """This function print two data tables from hh.ru and sj.ru data."""
    table_hh = build_and_print_table_of_data_hh(languages)
    table_sj = build_and_print_table_of_data_sj(languages, api_headers)
    search_vacancies_sources = [table_hh, table_sj]
    for search in search_vacancies_sources:
        return search


if __name__ == '__main__':
    
    show_tables_of_all_sources(languages, api_headers)
    