import click
from jinja2 import Template
import requests
from requests.auth import HTTPBasicAuth

session = requests.Session()

gn_url="http://localhost/geonetwork/srv"
gn_api_url="http://localhost/geonetwork/srv/api/records"
username='admin'
password='admin'

class Context:
    obj: None


@click.command()
def api_harvest():
    geonetwork_session = requests.Session()
    geonetwork_session.auth = HTTPBasicAuth(username, password)
    geonetwork_session.headers.update({"Accept": "application/json"})

    # Make a call to an endpoint to get cookies and an xsrf token

    geonetwork_url = gn_url + '/eng/info?type=me'
    r_post = geonetwork_session.post(geonetwork_url,
                                     verify=False
                                     )

    token = geonetwork_session.cookies.get('XSRF-TOKEN')
    geonetwork_session.headers.update({"X-XSRF-TOKEN": geonetwork_session.cookies.get('XSRF-TOKEN')})

    ctx = Context()
    # add session and credentials as context objects so they can be used elsewhere
    ctx.obj = {
        'session': geonetwork_session,
        'username': username,
        'password': password,
        'url': gn_url
    }

    session = ctx.obj['session']
    url = ctx.obj['url']
    session.auth = HTTPBasicAuth(ctx.obj['username'],ctx.obj['password'])
    headers = session.headers
    cookies = session.cookies

    files = {'file': ('contact.xml', open('/home/jean/dev/SIB/contacts_sync/src/build/0e243418-a666-11eb-a518-fab7a7562f4a.xml', 'rb'))}
    values = {'metadataType': 'SUB_TEMPLATE', 'uuidProcessing': 'OVERWRITE', 'publishToAll': 'true', 'transformWith': '_none_'}
    processURL = session.post(gn_api_url,
                          data=values,
                          files=files,
                          headers=headers,
                          verify=False
                          )
    # values = {
    #     'metadataType': 'SUB_TEMPLATE',
    #     'serverFolder':'/catalog/upload/build',
    #     'uuidProcessing': 'OVERWRITE',
    #     'publishToAll': 'true',
    #     'transformWith': '_none_',
    # }
    # processURL = session.put(gn_api_url,
    #                       data=values,
    #                       headers=headers,
    #                       verify=False
    #                       )

    print('ok')


if __name__ == '__main__':
    api_harvest(auto_envvar_prefix='POCS')

