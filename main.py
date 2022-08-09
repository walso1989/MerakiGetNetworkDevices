# Creator:    Walter J. Solano Vindas
#             CCIE #55772
#             wsolano@getcrg.com
# Script reads a file called config.cfg that should provide information information like organization name, API Key, and output filename (without extension) and network from where
# we need to extract the list of HW
# After that connects to the Meraki cloud, extracts the organization-ID, finds all networks within the organization, compares the name of each network with the one set in the config file
# Then extracts the information for all the devices in that network and save it to a CSV file
#
# config.cfg example
# [config]
# org_name = XXXX
# API_KEY = XXXXXX
# csv_file_name= XXXX
# network_name = XXXX

import json
import meraki
import pandas
import os
import configparser
import datetime
import itertools

def api_connect(config_dict):
    print(f"Connecting to Meraki API")
    dashboard = meraki.DashboardAPI(config_dict["api_key"], output_log=False)
    return (dashboard)

def get_organization_id(config_dict):
    org_id = 0
    print(f" Looking for Organizaion: {config_dict['org_name']}")

    dashboard=api_connect(config_dict)
    response = dashboard.organizations.getOrganizations()

    print(f" response from API {json.dumps(response, indent=2)}")

    for org in response:
        if config_dict["org_name"].lower() in org["name"].lower():
            return(org["id"])
            print(f" Organization Id for {org_name} is {org_id}")
            break
        else:
            print(f" Please check config file and add a valid organization name")

def get_networks_id(config_dict, organization_id):
    print(f"Looking for networks in organization id {organization_id}")

    dashboard=api_connect(config_dict)
    response = dashboard.organizations.getOrganizationNetworks(organization_id)

    print(f" response from API {json.dumps(response, indent=2)}")

    return (response)

def main():
    current_path = os.getcwd()

    # reading config values from config file
    config = configparser.RawConfigParser()
    configfile_path = current_path + "//config.cfg"
    config.read(configfile_path)
    config_dict = dict(config.items('config'))

    # Variable definitions
    csv_file = current_path + "//outputs//" + config_dict["org_name"] + "_"+  config_dict["csv_file_name"] +"_" + datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')+".csv"
    final_info=[]

    #getting organization ID and Networks within the organization
    organization_id = get_organization_id(config_dict)
    network_id = get_networks_id(config_dict, organization_id)

    #to extract VLAN information from the different networks in the organization
    for network in network_id:
        if network['name']==config_dict['network_name']:
            print(f"Network found")
            dashboard = api_connect(config_dict)
            dict_devices = dashboard.networks.getNetworkDevices(network['id'])
            df=pandas.DataFrame.from_dict(dict_devices)
            df.to_csv(csv_file)
    print(f" Evaluating next network")


if __name__ == "__main__":
    main()
