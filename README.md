# Contacts API to API
The aim of this CLI is to be able to tap into the [INPN organisms reference](https://inpn.mnhn.fr/telechargement/referentiels/organismes) and generate point of contact resources for GeoNetwork.

It operates in 2 steps, that can possibly be run independently:
- harvest the [INPN API](https://odata-sinp.mnhn.fr/organizations) and generate the points of contact as ISO19139-suitable XML fragments
- scan such generated fragments and import them into GeoNetwork

This CLI uses the [click](https://click.palletsprojects.com) library. If you want to understand how it works, it is advised that you at least run through click's documentation.

## Install
It leverages setuptools, [as advised in the click documentation](https://click.palletsprojects.com/en/8.0.x/quickstart/#switching-to-setuptools) to build an executable file. You don't necessary need this, but it can provide you ultimately with a nice executable. It should even be ble to run on Windows (not tested though).

To install the script, you can run 
```shell
python3 -m venv .venv
. .venv/bin/activate
pip install --editable .
contacts_api_to_api --help
```

## Run
To harvest the INPN API, you can run 
```shell
contacts_api_to_api api-harvest
```

To import the generated files into GN, you can run
```shell
contacts_api_to_api poc-import your_gn_username your_gn_password
```
If you want to improve the import process, you can switch to a *local* import: Geonetwork is able to 
- either import through http, transfering the files over to the server in the POST request and loading them
- or import from a folder of XML files located on the GN server and accessible by GN

This is what we call here a *local* import. It will be much faster. 

## Develop
*Hint:*

When I want to test the local mode, I'm mounting on my filesystem the geonetwork-accessible folder from a distant server, using sshfs