import requests
import json

# Функция для получения кода города по его названию
def get_city_code(city_name):
    url = 'https://api.hh.ru/areas'
    response = requests.get(url)

    if response.status_code == 200:
        areas = response.json()
        for country in areas:
            for area in country['areas']:
                if area['name'].lower() == city_name.lower():
                    return area['id']
                for sub_area in area['areas']:
                    if sub_area['name'].lower() == city_name.lower():
                        return sub_area['id']
    return None

# Функция для получения данных о вакансиях с HH.ru
def get_vacancies(city_code, vacancy_name):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': vacancy_name,
        'area': city_code,
        'per_page': 100
    }

    vacancies = []
    page = 0
    while True:
        params['page'] = page
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Ошибка: {response.status_code} - {response.text}")
            break

        data = response.json()

        if 'items' not in data or not data['items']:
            print("Вакансии не найдены.")
            break

        vacancies.extend(data['items'])
        page += 1

        if page >= data['pages']:
            break

    return vacancies

# Функция для анализа вакансий
def analyze_vacancies(vacancies):
    total_vacancies = len(vacancies)
    total_salary = 0
    requirements_count = {}

    for vacancy in vacancies:
        salary = vacancy.get('salary')
        if salary and salary['currency'] == 'RUR':
            if salary['from'] and salary['to']:
                avg_salary = (salary['from'] + salary['to']) / 2
            elif salary['from']:
                avg_salary = salary['from']
            elif salary['to']:
                avg_salary = salary['to']
            else:
                avg_salary = 0
            total_salary += avg_salary

        description = vacancy.get('snippet', {}).get('requirement', '')
        if description:
            words = description.lower().split()
            for word in words:
                if len(word) >= 3:
                    if word in requirements_count:
                        requirements_count[word] += 1
                    else:
                        requirements_count[word] = 1

    avg_salary = total_salary / total_vacancies if total_vacancies > 0 else 0

    sorted_requirements = sorted(requirements_count.items(), key=lambda x: x[1], reverse=True)
    top_5_requirements = sorted_requirements[:5]

    total_requirements = sum(requirements_count.values())

    top_5_with_percent = [(req, count, (count / total_requirements) * 100) for req, count in top_5_requirements]

    return total_vacancies, avg_salary, top_5_with_percent

# Функция для сохранения результата анализа в файл JSON
def save_analysis_to_json(city, vacancy_name, total_vacancies, avg_salary, top_5_requirements):
    data = {
        "city": city,
        "vacancy_name": vacancy_name,
        "total_vacancies": total_vacancies,
        "average_salary": avg_salary,
        "top_requirements": [
            {"requirement": req, "count": count, "percentage": percent}
            for req, count, percent in top_5_requirements
        ]
    }

    with open("vacancies_analysis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция для сохранения всех данных вакансий в файл JSON
def save_vacancies_to_json(vacancies):
    with open("vacancies_data.json", "w", encoding="utf-8") as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=4)

# Основная функция для запуска парсинга
def run_parser(city, vacancy):
    city_code = get_city_code(city)
    
    if city_code:
        print(f"Код города {city}: {city_code}")
        print("\nПолучение данных с hh.ru...")
        vacancies = get_vacancies(city_code, vacancy)

        if vacancies:
            total_vacancies, avg_salary, top_5_requirements = analyze_vacancies(vacancies)

            print(f"\nВсего вакансий: {total_vacancies}")
            print(f"Средняя зарплата: {avg_salary:.2f} руб.")
            print("\nТоп 5 требований и их количество упоминаний (с процентами):")
            for req, count, percent in top_5_requirements:
                print(f"{req}: {count} упоминаний ({percent:.2f}%)")

            save_analysis_to_json(city, vacancy, total_vacancies, avg_salary, top_5_requirements)
            save_vacancies_to_json(vacancies)

            print("\nРезультаты сохранены в файлы vacancies_analysis.json и vacancies_data.json")

        else:
            print("Нет доступных вакансий по заданным параметрам.")
    else:
        print(f"Город '{city}' не найден.")
