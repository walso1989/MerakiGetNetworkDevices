# This is a sample Python script.

import json
import meraki
import pandas
import os
import configparser

def api_connect(config_dict):
    print(f"Connecting to Meraki API")
    dashboard = meraki.DashboardAPI(config_dict["api_key"], output_log=False)
    return (dashboard)

def get_organization_id(config_dict):
    # print(f" Looking for Organizaion: {config_dict[org_name]}")

    org_id = 0

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
    # Variable definitions
    current_path = os.getcwd()
    csv_file = current_path + "//" + config_dict["csv_file_name"]

    #reading config values from config file
    config = configparser.RawConfigParser()
    configfile_path=current_path+"//config.cfg"
    config.read(configfile_path)
    config_dict = dict(config.items('config'))

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
            response = dashboard.appliance.getNetworkApplianceVlans(checking_network)
            response2 = dashboard.networks.getNetwork(checking_network)

            #Transforms the outputs to a JSON and then move them to a dict for easy manipulation
            vlans_details=json.dumps(response,indent=3)
            network_details=json.dumps(response2,indent=3)
            dict_vlans_details = json.loads(vlans_details)
            dict_network_details = json.loads(network_details)

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
        #writting information to JSON file
        with open('vlan-info.json', 'a') as f:
            json.dump(dict_vlans_details, f,indent=3)

    exit(0)
if __name__ == "__main__":
    main()
