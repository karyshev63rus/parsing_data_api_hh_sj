import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def form_dict_of_search_options_hh(language):
    '''This function creates dict of options for request through API hh.ru
    '''
    search_options = 'программист москва {}'.format(language)
    dict_of_options={'text':search_options, 'area':'113'}
    return dict_of_options

def collect_list_of_it_vacancies_hh(language):
    '''This function collect vacancies across programming languages through API hh.ru
    '''
    json_format_answer = []
    page = pages_number = 1
    # print(language)
    while page <= pages_number:
        dict_of_options = form_dict_of_search_options_hh(language)
        url = 'https://api.hh.ru/vacancies'
        response = requests.get(url, params=dict_of_options).json()
        pages_number = response['pages']
        page += 1
        json_format_answer.append(response)
        # if page%10==0:
    #         print(page)
    # print('____')
    return json_format_answer

def count_it_vacancies_hh(language):
    '''This function calcalates count of it vacancies through API hh.ru
    '''
    dict_of_options = form_dict_of_search_options_hh(language)
    url = 'https://api.hh.ru/vacancies'
    response = requests.get(url, params=dict_of_options).json()
    return response['found']

def get_spreads_of_salary_for_language_hh(language):
    '''This function gives spreads of salary 
    '''
    list_of_salary_spreads = []
    for item_of_list in collect_list_of_it_vacancies_hh(language):
        for item in item_of_list['items']:
            list_of_salary_spreads.append(item['salary'])
    return list_of_salary_spreads

def predict_rub_salary_hh(language):
    '''This function computes average salary through API hh.ru
    '''
    list_of_salary_spreads = get_spreads_of_salary_for_language_hh(language)
    list_of_salary_without_nonetype = []
    for salary in list_of_salary_spreads:
        try:
            if salary['currency'] != 'RUR':
                    continue
            else:
                if None:
                    continue
                elif salary['from'] and salary['to']:
                    list_of_salary_without_nonetype.append((salary['from'] + salary['to'])*0.5)
                elif salary['from'] is None:
                    list_of_salary_without_nonetype.append(salary['to']*0.8)
                elif salary['to'] is None:
                    list_of_salary_without_nonetype.append(salary['from']*1.2)
        except TypeError:
            continue
    tupple_of_salary = (list_of_salary_without_nonetype, len(list_of_salary_without_nonetype))
    return tupple_of_salary

def create_dict_for_one_language_hh(language):
    '''This function creates a dict of vacancies and avegare salary through API hh.ru
    '''
    data_salary, len_salary = predict_rub_salary_hh(language)
    salary_count_list = [salary for salary in data_salary]
    if len_salary > 0:
        average_rub_salary = int(sum(salary_count_list)/len_salary)
    dict_vacancies_salary_by_language = {}
    dict_vacancies_salary_by_language['vacancies_found'] = count_it_vacancies_hh(language)
    dict_vacancies_salary_by_language['vacancies_processed'] = len_salary
    dict_vacancies_salary_by_language['average_salary'] = average_rub_salary
    return dict_vacancies_salary_by_language

def create_dict_for_all_languages_hh(list_of_languages):
    '''This function creates a dict for all languages through API hh.ru
    '''
    dict_for_all_languages = {}
    for language in list_of_languages:
        dict_for_all_languages[language] = create_dict_for_one_language_hh(language)
    return dict_for_all_languages

def build_table_of_data_hh(list_of_languages):
    '''This function builds a data table from sj.ru data 
    '''
    title = 'HeadHunter Moscow'
    data_dict = create_dict_for_all_languages_hh(list_of_languages)
    big_list = []
    big_list.append(['language', 'average_salary', 'vacancies_found', 'vacancies_processed'])
    for language, data in data_dict.items():
        small_list = []
        small_list.append(language)
        for key, value in data.items():
            small_list.append(value)
        big_list.append(small_list)
    print(AsciiTable(big_list, title).table)

def count_it_vacancies_sj(language, api_headers):
    '''This function calcalates count of it vacancies through API sj.ru
    '''
    search_language = '{}'.format(language)
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers=api_headers
    list_of_it_vacancies = []
    total_vacancies = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4}, 
        headers=api_headers).json()['total']
    return total_vacancies

def collect_list_of_it_vacancies_sj(language, api_headers):
    '''This function collect all vacancies across programming languages through API sj.ru
    '''
    search_language = '{}'.format(language)
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers=api_headers
    list_of_it_vacancies = []
    total_vacancies = count_it_vacancies_sj(language, api_headers)
    total_pages = total_vacancies//20 + 1
    # print(language)
    for page in range(total_pages):
        response = requests.get(url, params={'keywords':['программист', search_language], 
            'catalogues':'Разработка, программирование', 'period':30, 'town':4, 'page':page}, 
            headers=api_headers).json()
        # print(page)
        for item in response['objects']:
            list_of_it_vacancies.append(item)
    # print('____')
    return list_of_it_vacancies

def get_spreads_of_salary_for_language_sj(language, api_headers):
    '''This function gives spreads of salary through API sj.ru
    '''
    list_of_salary_spreads = []
    list_of_it_vacancies = collect_list_of_it_vacancies_sj(language, api_headers)
    for item in list_of_it_vacancies:
        list_of_salary_spreads.append((item['payment_from'], item['payment_to']))
    return list_of_salary_spreads

def predict_rub_salary_sj(language, api_headers):
    '''This function computes average salary for language through API sj.ru
    '''
    list_of_salary_spreads = get_spreads_of_salary_for_language_sj(language, api_headers)
    list_of_salary_without_nonetype = []
    for salary in list_of_salary_spreads:
        salary_from, salary_to = salary
        if salary_from != 0 and salary_to != 0:
            list_of_salary_without_nonetype.append((salary_from + salary_to)*0.5)
        elif salary_from != 0:
            list_of_salary_without_nonetype.append(salary_from*1.2 )
        elif salary_to != 0:
            list_of_salary_without_nonetype.append(salary_to*0.8)
    tupple_of_salary = (list_of_salary_without_nonetype, len(list_of_salary_without_nonetype))
    return tupple_of_salary
        
def create_dict_for_one_language_sj(language, api_headers):
    '''This function creates a dict of vacancies and avegare salary through API sj.ru
    '''
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

def create_dict_for_all_languages_sj(list_of_languages, api_headers):
    '''This function creates a dict for all languages through API sj.ru
    '''
    dict_for_all_languages = {}
    for language in list_of_languages:
        dict_for_all_languages[language] = create_dict_for_one_language_sj(language, api_headers)
    return dict_for_all_languages

def build_table_of_data_sj(list_of_languages, api_headers):
    '''This function builds a data table from sj.ru data 
    '''
    title = 'SuperJob Moscow'
    data_dict = create_dict_for_all_languages_sj(list_of_languages, api_headers)
    big_list = []
    big_list.append(['language', 'average_salary', 'vacancies_found', 'vacancies_processed'])
    for language, data in data_dict.items():
        small_list = []
        small_list.append(language)
        for key, value in data.items():
            small_list.append(value)
        big_list.append(small_list)
    print(AsciiTable(big_list, title).table)

def main(list_of_languages, api_headers):
    '''This function print two data tables from hh.ru and sj.ru data 
    '''
    search_vacanciones_list = [build_table_of_data_hh(list_of_languages),
    build_table_of_data_sj(list_of_languages, api_headers)]
    for search in search_vacanciones_list:
        return search

list_of_languages=['typescript', 'swift', 'scala', 'objective-c', 
'shell', 'go', 'c#', 'c++', 'php', 'ruby', 'python', 'java', 'javascript']


if __name__ == '__main__':
    
    load_dotenv()

    TOKEN = os.getenv('TOKEN')
    api_headers = {
                    'X-Api-App-Id':str(TOKEN)
    }

    main(list_of_languages, api_headers)
