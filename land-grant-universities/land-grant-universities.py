import collections
import pprint
import csv

import mechanicalsoup
import tldextract


def get_institutions_from_page(page):
    views_table = page.soup.find('table', class_='views-table')
    views_table_body = views_table.find('tbody')
    views_fields_titles = views_table_body.find_all('td',
                                                    class_='views-field-title')

    page_institutions = []
    for view_field_title in views_fields_titles:
        institution_link = view_field_title.find('a', target='_blank')
        institution_name = institution_link.get_text()
        institution_url = institution_link['href']
        extract_result = tldextract.extract(institution_url)
        institution_domain = extract_result.registered_domain
        institution = Institution(name=institution_name, url=institution_url,
                                  domain=institution_domain)
        page_institutions.append(institution)
    return page_institutions


def get_next_page_from_page(browser, page, base_url):
    next_page_link = page.soup.find('a', class_='pager__link pager__link--next')
    print(f'next_page_link={next_page_link}')
    if next_page_link:
        next_page_relative_url = next_page_link['href']
        print(f'next_page_relative_url={next_page_relative_url}')
        next_page_absolute_url = f'{base_url}{next_page_relative_url}'
        print(f'next_page_absolute_url={next_page_absolute_url}')
        next_page = browser.get(next_page_absolute_url)
        return next_page


Institution = collections.namedtuple('Institution', ['name', 'url', 'domain'])

if __name__ == '__main__':
    browser = mechanicalsoup.Browser()
    base_url = 'https://nifa.usda.gov'
    first_page_url = f'{base_url}/land-grant-colleges-and-universities-partner-website-directory'
    all_institutions = []
    page = browser.get(first_page_url)
    while page is not None:
        page_institutions = get_institutions_from_page(page)
        all_institutions.extend(page_institutions)
        page = get_next_page_from_page(browser, page, base_url)

    with open('land-grant-universities.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'url', 'domain']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for institution in all_institutions:
            writer.writerow(institution._asdict())
