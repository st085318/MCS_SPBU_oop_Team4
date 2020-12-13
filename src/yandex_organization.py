import requests
import json


def find_clubs_in_yandex(city="Москва", search_query="секции"):
    apikey = "09ec3bea-ac24-482d-9670-7e57a2fcf222"
    url = f"https://search-maps.yandex.ru/v1/?text={search_query},{city}&type=biz&lang=ru_RU&results=50&apikey={apikey}"
    yandex_ans = requests.get(url)
    companies_with_info = []
    if str(yandex_ans) == "<Response [200]>":
        yandex_ans = json.loads(yandex_ans.text)
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



