#!/usr/bin/env python
"""\
Import points of contact to GeoNetwork, using the INPN API as source

Usage: contacts_api_to_api inpn-to-gn --user your_gn_username --password your_gn_passwd
"""

import click
import glob
from jinja2 import Template
import lxml.html
from pathlib import Path
import requests

__author__ = "Jean Pommier"
__license__ = "Apache"
__email__ = "jean.pommier@pi-geosolutions.fr"

# TODO: allow to merge an existing, edited poc with the data taken from the inpn api
# TODO: proper logging
# TODO: metrics/reporting
# TODO: manage possible errors/exceptions (network, API, )


session = requests.Session()

default_inpn_api_url="https://odata-sinp.mnhn.fr/organizations?inpnPartner=true"
default_inpn_api_page_size=100
default_cas_login_url="https://test-cas-patrinat.mnhn.fr/auth/login"
default_gn_url="https://sib1.dev.pigeosolutions.fr/geonetwork"


def get_pocs(api_url, api_page_size):
    """
    Helper iterator that loops through the API's paginated results
    :param api_url:
    :param api_page_size:
    :return: every page, in an iterator
    """
    currP = 0
    totalP = 1 #assuming there's gonna be 2nd page, it'll get overwritten if not.
    while (currP < totalP):
        page = session.get(api_url, params={'size': api_page_size, 'page': currP}).json()
        totalP = page['page']['totalPages']
        currP += 1
        yield page


def _api_harvest(api_url,
                template_file,
                destination_path,
                ):
    # Make sure the destination folder exists
    Path(destination_path).mkdir(parents=True, exist_ok=True)

    for page in get_pocs(api_url, default_inpn_api_page_size):
        if not page.get('_embedded', None):
            break
        for entry in page['_embedded']['organizationModelList']:
            with open(template_file) as file_:
                template = Template(file_.read())
                poc_xml = template.render(poc=entry)
                with open(f'{destination_path}/{entry["organizationCode"]}.xml', 'w') as f:
                    f.write(poc_xml)
            print(entry['enrichedLabel'])


@click.group()
def cli():
    pass


@cli.command()
@click.option('--api_url', default=default_inpn_api_url, help='URL to the contact point reference service')
@click.option('-t','--template_file', default='templates/poc_xml.j2', help='Jinja2 template to structure each POC')
@click.option('-d', '--destination_path', default='/tmp/contacts', help='Folder where the contact xml files will be written')
def api_harvest(api_url,
                template_file,
                destination_path,
                ):
    """
    Harvest the INPN API and write XML points of contact as ISO19139-suitable XML fragments
    :param api_url:
    :param template_file:
    :param destination_path:
    :return:
    """
    _api_harvest(api_url,
                 template_file,
                 destination_path,
                 )



def cas_login(cas_login_url, service_url, username, password):
    """
    Implements SSO: just call this function, and you get a session object, with the correct cookies,
    namely the jsessionid
    Taken from https://brennan.io/2016/03/02/logging-in-with-requests/
    :param cas_login_url: e.g. "https://test-cas-patrinat.mnhn.fr/auth/login"
    :param gn_url: base geonetwork URL, e.g. "https://sib1.dev.pigeosolutions.fr/geonetwork/"
    :param username:
    :param password:
    :return: requests.session object
    """
    # GET parameters - URL we'd like to log into.
    params = {'service': service_url}

    # Start session and get login form.
    session = requests.session()
    login = session.get(cas_login_url, params=params)
    # Get the hidden elements and put them in our form.
    login_html = lxml.html.fromstring(login.text)
    hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
    form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements[:2]}

    # "Fill out" the form.
    form['username'] = username
    form['password'] = password

    # Finally, login and return the session.
    p = session.post(cas_login_url, data=form, params=params)
    return session


def _poc_import(
                source_path,
                cas_login_url,
                gn_url,
                local,
                user,
                password,
                ):
    # Open an authenticated session, that we can use for the GN API calls
    session = cas_login(cas_login_url, f'{gn_url}/srv/eng/info?type=me', user, password)
    session.headers.update({"Accept": "application/json"})

    if local:
        print(f'Importing the XML files using a local serverFolder ({source_path})')
        values = {
            'metadataType': 'SUB_TEMPLATE',
            'serverFolder': source_path,
            'uuidProcessing': 'OVERWRITE',
            'publishToAll': 'true',
            'transformWith': '_none_',
        }
        processURL = session.put(f'{gn_url}/srv/api/records',
                              data=values,
                              verify=False
                              )
    else:
        print(f'Importing the XML files through http')
        # Iterate through the files and call GN API to import them 1 by 1
        # TODO: try to import using a global MEF file
        values = {
            'metadataType': 'SUB_TEMPLATE',
            'uuidProcessing': 'OVERWRITE',
            'publishToAll': 'true',
            'transformWith': '_none_',
        }
        list_files = Path(source_path).glob('*.xml')
        for f in list_files:
            files = { 'file': ('contact.xml', open(f, 'rb')) }
            importURL = session.post(
                                        f'{gn_url}/srv/api/records',
                                        data=values,
                                        files=files,
                                    )
            print(f'Import file {f}: status code {importURL.status_code}')


@cli.command()
@click.option('--source_path', default='/tmp/contacts', help='Path where the xml files are read from')
@click.option('--cas_login_url', default=default_cas_login_url, help='URL to the CAS login page')
@click.option('--gn_url', default=default_gn_url, help='GeoNetwork\'s base URL')
@click.option('--local', is_flag=True, help='If set, it will use the "import from folder" option, which will be much faster than iterating through every record and pushing it through http')
@click.option('--user', help='User registred in the CAS SSO, with sufficient rights to import a poc record')
@click.option('--password', help='User\'s password')
def poc_import(
                source_path,
                cas_login_url,
                gn_url,
                local,
                user,
                password,
                ):
    """
    Read a folder of XML files and import them into the GN catalog's directory of contacts
    """
    _poc_import(
        source_path,
        cas_login_url,
        gn_url,
        local,
        user,
        password,
    )


@cli.command()
@click.option('--api_url', default=default_inpn_api_url, help='URL to the contact point reference service')
@click.option('-t', '--template_file', default='templates/poc_xml.j2', help='Jinja2 template to structure each POC')
@click.option('-d', '--destination_path', default='/tmp/contacts',
              help='Folder where the contact xml files will be written')
@click.option('--server_path', default='/catalog/upload/contacts', help='Path where the xml files are read from')
@click.option('--cas_login_url', default=default_cas_login_url, help='URL to the CAS login page')
@click.option('--gn_url', default=default_gn_url, help='GeoNetwork\'s base URL')
@click.option('--local', is_flag=True, help='If set, it will use the "import from folder" option, which will be much faster than iterating through every record and pushing it through http')
@click.option('--user', help='User registred in the CAS SSO, with sufficient rights to import a poc record')
@click.option('--password', help='User\'s password')
@click.option('-d', '--delete', is_flag=True, help='Delete files once imported')
def inpn_to_gn(
                api_url,
                template_file,
                destination_path,
                server_path,
                cas_login_url,
                gn_url,
                local,
                user,
                password,
                delete,
                ):
    _api_harvest(api_url, template_file, destination_path)
    _poc_import(server_path, cas_login_url, gn_url, local, user, password )
    if delete:
        for f in Path(destination_path).glob('*.xml'):
            f.unlink()


if __name__ == '__main__':
    cli(auto_envvar_prefix='POCS')

