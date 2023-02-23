import click
from jinja2 import Template
import requests

session = requests.Session()

default_api_url="https://odata-sinp.mnhn.fr/organizations?inpnPartner=true"
api_page_size=100

def get_pocs(api_url):
    currP = 0
    totalP = 1 #assuming there's gonna be 2nd page, it'll get overwritten if not.
    while (currP < totalP):
        page = session.get(api_url, params={'size': api_page_size, 'page': currP}).json()
        totalP = page['page']['totalPages']
        currP += 1
        yield page



@click.command()
@click.option('--api_url', default=default_api_url, help='URL to the contact point reference service')
@click.option('--template_file', default='templates/poc_xml.j2', help='Jinja2 template to structure each POC')
def api_harvest(api_url,
                template_file
                ):
    for page in get_pocs(api_url):
        if not page.get('_embedded', None):
            break
        for entry in page['_embedded']['organizationModelList']:
            with open(template_file) as file_:
                template = Template(file_.read())
                poc_xml = template.render(poc=entry)
                with open(f'build/{entry["organizationCode"]}.xml', 'w') as f:
                    f.write(poc_xml)
            print(entry['enrichedLabel'])


if __name__ == '__main__':
    api_harvest(auto_envvar_prefix='POCS')

