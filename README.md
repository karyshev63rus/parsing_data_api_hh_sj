# Собираем статистику о зарплатах программистов

Данный репозиторий содержит написанный на языке ```python``` скрипт (и опричь него файлы поддержки) с целью сбора данных о вакансиях для разработчиков разных языков программирования (программа выдает количество текущих вакансий и среднюю заработную плату по каждому ЯП из составленного списка). Эти данные собираются из двух источников: ***HeadHunters.ru*** и ***SuperJob.ru***. Получение информации производится через API вышеуказанных компаний. 

Доступ к программному интерфейсу приложения на HeadHunter возможен без какой-либо авторизации, а вот работа с API SuperJob требует некоторых усилий (необходимо зарегистриоваться на сайте компании, зарегистрировать свое приложение и получить секретный ключ - подробнее здесь (https://api.superjob.ru)). Получив ключ, следует (в одном (!!!) каталоге с файлом **main.py**) создать файл с названием **.env** и записать в него TOKEN=XXX (где XXX - это секретный ключ без кавычек и пробелов). 

Далее желательно установить требуемые библиотеки (в командной строке пишете ```pip install -r requirements.txt```) и запустить скрипт (например, набрав в командной строке ```python main.py```). Ожидаемым результатом отработанного сценария должны стать две таблицы (одна будет создана по мотивам HH, а вторая - SJ), которые и будут содержать информацию о предлагаемых отечественным программистам размерах оплаты труда (в выборкку входят вакансии по г. Москве).

Очевидно, что получение данных - процесс весьма длительный. Поэтому, для того, чтобы держать "руку на пульсе" - отслеживать скачивание, можно раскомментировать ```print``` в функциях ```collect_list_of_it_vacancies_hh()``` и ```collect_list_of_it_vacancies_sj()```. И еще. Всегда можно настроить параметры запроса к API под свои требования (лучше это делать на *HeadHunter* (https://github.com/hhru/api) - массив данных здесь существенно больше, чем на *SuperJob*).