import click
from jinja2 import Template
import lxml.html
import requests
from requests.auth import HTTPBasicAuth

session = requests.Session()

default_cas_login_url="https://test-cas-patrinat.mnhn.fr/auth/login"
default_gn_url="https://sib1.dev.pigeosolutions.fr/geonetwork"


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


@click.command()
@click.option('--cas_login_url', default=default_cas_login_url, help='URL to the CAS login page')
@click.option('--gn_url', default=default_gn_url, help='GeoNetwork\'s base URL')
@click.option('--user', default="", help='User registred in the CAS SSO, with sufficient rights to import a poc record')
@click.option('--password', default="", help='User\'s password')
def poc_import(
                cas_login_url,
                gn_url,
                user,
                password,
                ):
    session = cas_login(cas_login_url, f'{gn_url}/srv/eng/info?type=me', user, password)
    session.headers.update({"Accept": "application/json"})

    files = {'file': ('contact.xml', open('/tmp/contacts/0e243418-a666-11eb-a518-fab7a7562f4a.xml', 'rb'))}
    values = {'metadataType': 'SUB_TEMPLATE', 'uuidProcessing': 'OVERWRITE', 'publishToAll': 'true', 'transformWith': '_none_'}
    importURL = session.post(
                                f'{gn_url}/srv/api/records',
                                data=values,
                                files=files,
                            )
    print(importURL.status_code)


if __name__ == '__main__':
    poc_import(auto_envvar_prefix='POCS')

