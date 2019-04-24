import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


LANGUAGES = [
    'typescript', 'swift', 'scala', 'objective-c', 'shell', 'go', 
    'c#', 'c++', 'php', 'ruby', 'python', 'java', 'javascript'
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
    try:
        response = requests.get(url_hh, params=query)
        response.raise_for_status()
    except requests.RequestException as err:
        print(err.response)
    try:
        return ((response.json()['pages'], response.json()['found']))
    except KeyError:
        return (0, 0)

def collect_it_vacancies_hh(language):
    """This function collects vacancies across programming languages through API hh.ru."""
    query = form_search_query_hh(language)
    try:
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
    except requests.RequestException as err:
        None
    return vacancies

def get_spreads_of_salary_for_language_hh(language):
    """This function gives spreads of salary.""" 
    try:
        vacancies = collect_it_vacancies_hh(language)
        salaries = [salary['salary'] for salary in vacancies]
        salaries_rur = []
        for salary in salaries:
            try:
                if salary['currency'] != 'RUR':
                        continue
                else:
                    if None:
                        continue
                    else:
                        salaries_rur.append((salary['from'], salary['to']))
            except TypeError:
                continue
    except requests.RequestException as err:
        None
    return salaries_rur
    
def predict_salary(salary_from, salary_to):
    """This function computes average salary through API hh.ru or sj.ru."""
    try:
        if salary_from is not None and salary_to is not None:
            salary_semisum = (salary_from + salary_to)*0.5
        elif salary_from is None:
            salary_semisum = salary_to*0.8
        elif salary_to is None:
            salary_semisum = salary_from*1.2
    except requests.RequestException as err:
        None
    return salary_semisum

def predict_rub_salary_hh(language):
    """This function calculates selisums of salary by vacancies."""    
    try:
        salary_spreads = get_spreads_of_salary_for_language_hh(language)
        salary_predicts = [predict_salary(salary_from, salary_to) for 
            salary_from, salary_to in salary_spreads]
    except requests.RequestException as err:
        None
    return (salary_predicts, len(salary_predicts))

def create_dataset_hh(language):
    """This function creates a dict of vacancies and avegare salary through API hh.ru."""
    try:
        salary_count, salary_length = predict_rub_salary_hh(language)
        if salary_length > 0:
            average_rub_salary = int(sum(salary_count)/salary_length)
        else:
            average_rub_salary = 0
        vacancies_salary_by_language = {
            'vacancies_found':count_it_vacancies_hh(language)[1], 
            'vacancies_processed':salary_length,
            'average_salary':average_rub_salary
        }
    except requests.RequestException as err:
        None
    return vacancies_salary_by_language

def build_and_print_table_hh(LANGUAGES):
    """This function builds a data table from sj.ru data."""
    try:
        title = 'HeadHunter Moscow'
        dataset_for_all_languages = {language:create_dataset_hh(language) for 
            language in LANGUAGES}
        table_content = [['language', 'vacancies_found', 'vacancies_processed', 
            'average_salary']]
        for language, data in dataset_for_all_languages.items():
            table_data = [language]
            data = [value for value in data.values()]
            table_data.extend(data)
            table_content.append(table_data)
    except requests.RequestException as err:
        None
    print(AsciiTable(table_content, title).table)
    
def count_it_vacancies_sj(language, api_headers):
    """This function calculates count of it vacancies through API sj.ru."""
    search_language = '{}'.format(language)
    headers=api_headers
    try:
        response = requests.get(url_sj, params={'keywords':['программист', 
            search_language], 'catalogues':'Разработка, программирование', 
            'period':30, 'town':4}, headers=api_headers)
        response.raise_for_status()
    except requests.RequestException as err:
        print(err.response)
    try:
        return response.json()['total']
    except KeyError:
        None

def collect_it_vacancies_sj(language, api_headers):
    """This function collects all vacancies across programming languages through API sj.ru."""
    try:
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
    except requests.RequestException as err:
        None
    return vacancies

def get_spreads_of_salary_for_language_sj(language, api_headers):
    """This function gives spreads of salary through API sj.ru."""
    try:
        list_of_it_vacancies = collect_it_vacancies_sj(language, api_headers)
        salary_spreads = [(item['payment_from'], item['payment_to']) for item 
            in list_of_it_vacancies]
    except requests.RequestException as err:
        None
    return salary_spreads

def predict_rub_salary_sj(language, api_headers):
    """This function computes average salary for language through API sj.ru."""
    try:
        salary_spreads = get_spreads_of_salary_for_language_sj(language, api_headers)
        salary_predicts = [predict_salary(salary_from, salary_to) for (salary_from, 
            salary_to) in salary_spreads if all((salary_from, salary_to)) != 0]
    except requests.RequestException as err:
        None
    return (salary_predicts, len(salary_predicts))

def create_dataset_sj(language, api_headers):
    """This function creates a dict of vacancies and avegare salary through API sj.ru."""
    try:
        salary_count, salary_length = predict_rub_salary_sj(language, api_headers)
        if salary_length > 0:
            average_rub_salary = int(sum(salary_count)/salary_length)
        else:
            average_rub_salary = 0
        vacancies_salary_by_language = {
            'vacancies_found':count_it_vacancies_sj(language, api_headers),
            'vacancies_processed':salary_length,
            'average_salary':average_rub_salary
        }
    except requests.RequestException as err:
        None
    return vacancies_salary_by_language

def build_and_print_table_sj(LANGUAGES, api_headers):
    """This function builds a data table from sj.ru data."""
    try:
        title = 'SuperJob Moscow'
        dataset_for_all_languages = {language:create_dataset_sj(language, 
            api_headers) for language in LANGUAGES}
        table_content = [['language', 'vacancies_found', 'vacancies_processed', 
            'average_salary']]
        for language, data in dataset_for_all_languages.items():
            table_data = [language]
            data = [value for key, value in data.items()]
            table_data.extend(data)
            table_content.append(table_data)
    except requests.RequestException as err:
        None
    print(AsciiTable(table_content, title).table)

def main(): 
    """This function prints two data tables from hh.ru and sj.ru data."""
    build_and_print_table_hh(LANGUAGES)
    build_and_print_table_sj(LANGUAGES, api_headers)


if __name__ == '__main__':
    
    load_dotenv()

    token = os.getenv('token')
    api_headers = {
        'X-Api-App-Id':str(token)
    }
 
    main()
