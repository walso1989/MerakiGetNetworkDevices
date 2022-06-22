# Creator:    Walter J. Solano Vindas
#             CCIE #55772
#             wsolano@getcrg.com
# Script reads a file called config.cfg that should provide information information like organization name, API Key, and output filename (without extension)
# After that connects to the Meraki cloud, extracts the organization-ID, finds all networks within the organization, and all the vlans within each network
# dumps the information to a JSON an CSV file for later not review.
#
# config.cfg example
# [config]
# org_name = XXXX
# API_KEY = XXXXXX
# csv_file_name= XXXX

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
        checking_network = network["id"]
        print(f" Extracting list of VLANs for network ID: {checking_network}")
        dashboard = api_connect(config_dict)
        insert_headers=True
        try:
            #get information about VLANS and Networks
            dict_vlans_details = dashboard.appliance.getNetworkApplianceVlans(checking_network)
            dict_network_details = dashboard.networks.getNetwork(checking_network)

            #Get's the network name from the dict and add it to the vlan details dict
            network_name=dict_network_details["name"]
            for vlans in dict_vlans_details:
                vlans["networkName"]=network_name

        except meraki.APIError as e:
            print(f"Meraki API error: {e}")
            print(f"status code = {e.status}")
            print(f"reason = {e.reason}")
            print(f"error = {e.message}")
            continue

        final_info.append(dict_vlans_details)

    json_file=current_path + "//outputs//" + config_dict["org_name"] +"_vlan-info_"+datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')+".json"
    with open(json_file, 'a') as f:
        json.dump(final_info, f,indent=3)

    #flat list and moving to pandas DF and then file
    merged = list(itertools.chain(*final_info))
    df = pandas.DataFrame(merged)
    df.to_csv(csv_file)

if __name__ == "__main__":
    main()
