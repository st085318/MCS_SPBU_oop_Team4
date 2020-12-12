import requests
import json


if __name__ == "__main__":
    url = "https://search-maps.yandex.ru/v1/?text=образовательный центр&type=biz&lang=ru_RU&results=50&apikey="
    yandex_ans = requests.get(url)
    if str(yandex_ans) == "<Response [200]>":
        yandex_ans = json.loads(yandex_ans.text)
        companies = yandex_ans.get("features")
        for company in companies:
            company_information = company.get("properties").get("CompanyMetaData")
            print(str(company_information.get("name"))+"\n")
            print(str(company_information.get("address"))+"\n")
            if company_information.get("url") is not None:
                print(str(company_information.get("url")) + "\n")
            if company_information.get("Phones") is not None:
                for phone in company_information.get("Phones"):
                    if phone.get("type") == "phone":
                        print(str(phone.get("formatted"))+"\n")
            print("\n")
