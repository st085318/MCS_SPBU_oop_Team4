import requests
import json


def find_clubs_in_yandex(apikey: str, city="Москва", search_query="Секции") -> [str]:
    url = f"https://search-maps.yandex.ru/v1/?text={search_query}," \
          f"{city}&type=biz&lang=ru_RU&results=50&apikey={apikey}"
    yandex_ans = requests.get(url)
    companies_with_info = []
    if str(yandex_ans) == "<Response [200]>":
        # Запрошенный ресурс был найден
        yandex_ans = yandex_ans.json()
        companies = yandex_ans.get("features")
        for company in companies:
            companies_info = ""
            company_information = company.get("properties").get("CompanyMetaData")
            companies_info += str(company_information.get("name"))+"\n"
            companies_info += str(company_information.get("address"))+"\n"
            if company_information.get("url") is not None:
                companies_info += str(company_information.get("url")) + "\n"
            if company_information.get("Phones") is not None:
                for phone in company_information.get("Phones"):
                    if phone.get("type") == "phone":
                        companies_info += str(phone.get("formatted"))+"\n"
            companies_info += "\n"
            companies_with_info.append(companies_info)
    else:
        companies_with_info.append("BAD ANSWER")
    return companies_with_info
