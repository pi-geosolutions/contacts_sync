import click
from jinja2 import Template
import requests
from requests.auth import HTTPBasicAuth

session = requests.Session()

gn_url="http://localhost/geonetwork/srv"
gn_api_url="http://localhost/geonetwork/srv/api/records"
username='admin'
password='admin'

xml = """<gmd:CI_ResponsibleParty xmlns:gmd="http://www.isotc211.org/2005/gmd"
                         xmlns:gco="http://www.isotc211.org/2005/gco"
                         uuid="inpn-contacts-ref-5A433BD0-2007-25D9-E053-2614A8C026F8">
  <gmd:individualName>
      <gco:CharacterString></gco:CharacterString>
   </gmd:individualName>
  <gmd:organisationName>
      <gco:CharacterString>Réserves naturelles de France</gco:CharacterString>
   </gmd:organisationName>
  <gmd:positionName>
      <gco:CharacterString></gco:CharacterString>
   </gmd:positionName>
  <gmd:contactInfo>
      <gmd:CI_Contact>
         <gmd:phone>
            <gmd:CI_Telephone>
               <gmd:voice>
                  <gco:CharacterString>0380489100</gco:CharacterString>
               </gmd:voice>
               <gmd:facsimile>
                  <gco:CharacterString></gco:CharacterString>
               </gmd:facsimile>
            </gmd:CI_Telephone>
         </gmd:phone>
         <gmd:address>
            <gmd:CI_Address>
               <gmd:deliveryPoint>
                  <gco:CharacterString>2 allee pierre lacroute</gco:CharacterString>
               </gmd:deliveryPoint>
               <gmd:city>
                  <gco:CharacterString>Dijon</gco:CharacterString>
               </gmd:city>
               <gmd:administrativeArea>
                  <gco:CharacterString/>
               </gmd:administrativeArea>
               <gmd:postalCode>
                  <gco:CharacterString></gco:CharacterString>
               </gmd:postalCode>
               <gmd:country>
                  <gco:CharacterString>France</gco:CharacterString>
               </gmd:country>
               <gmd:electronicMailAddress>
                  <gco:CharacterString></gco:CharacterString>
               </gmd:electronicMailAddress>
            </gmd:CI_Address>
         </gmd:address>
         <gmd:onlineResource>
            <gmd:CI_OnlineResource>
               <gmd:linkage>
                 <gmd:URL>http://www.reserves-naturelles.org</gmd:URL>
               </gmd:linkage>
               <gmd:protocol>
                  <gco:CharacterString>WWW:LINK-1.0-http--link</gco:CharacterString>
               </gmd:protocol>
               <gmd:name>
                  <gco:CharacterString/>
               </gmd:name>
               <gmd:description>
                  <gco:CharacterString/>
               </gmd:description>
            </gmd:CI_OnlineResource>
         </gmd:onlineResource>
      </gmd:CI_Contact>
  </gmd:contactInfo>
  <gmd:role>
      <gmd:CI_RoleCode codeList="./resources/codeList.xml#CI_RoleCode" codeListValue="pointOfContact"/>
  </gmd:role>
</gmd:CI_ResponsibleParty>"""

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

