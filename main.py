# This is a sample Python script.

import json
import meraki
import pandas
import os
import configparser

def get_organizationid(API_KEY, org_name):
    # get organization_ID
    dashboard = meraki.DashboardAPI(API_KEY,output_log=False)
    response = dashboard.organizations.getOrganizations()
    org_id = 0
    print(f" response from API {json.dumps(response, indent=2)}")
    org_name = "CRG-CORP"
    print(f" Looking for Organizaion: {org_name}")
    for org in response:
        if org_name.lower() in org["name"].lower():
            org_id = org["id"]
            break
    print(f" Organizaion Id for {org_name} is {org_id}")
    return (org_id)


def get_networksid(API_KEY, organization_id):
    print(f"Looking for networks in organization id {organization_id}")
    dashboard = meraki.DashboardAPI(API_KEY,output_log=False)
    response = dashboard.organizations.getOrganizationNetworks(organization_id)
    print(f" response from API {json.dumps(response, indent=2)}")
    return (response)

def get_organizationnames(API_KEY,network_id):
    network_names={}
    cont=0
    dashboard = meraki.DashboardAPI(API_KEY,output_log=False)
    for networks in network_id:
        checking_id=networks["id"]
        network_names=response["id"]["name"]
        cont=cont+1
    return(network_names)


def main():
    current_path = os.getcwd()

    #reading config values from config file
    config = configparser.RawConfigParser()
    configfile_path=current_path+"//config.cfg"
    config.read(configfile_path)
    config_dict = dict(config.items('config'))

    #Variable definitions
    API_KEY = config_dict["api_key"]
    org_name = config_dict["org_name"]

    csv_file = current_path + "//"+config_dict["csv_file_name"]



    #getting organization ID and Networks within the organization
    organization_id = get_organizationid(API_KEY, org_name)
    network_id = get_networksid(API_KEY, organization_id)

    #to extract VLAN information from the different networks in the organization
    for network in network_id:
        checking_network = network["id"]
        print(f" Extracting list of VLANs for network ID: {checking_network}")
        dashboard = meraki.DashboardAPI(API_KEY,output_log=False)
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

            df = pandas.DataFrame(dict_vlans_details)

            try:
                if insert_headers == True:
                    df.to_csv(csv_file,index=True,sep=',',mode='a')
                    insert_headers=False
                else:
                    df.to_csv(csv_file, index=True, sep=',', mode='a',header=False)
            except csv as strerror:
                logger.debug("Error creating File %s " + strerror)

        except meraki.APIError as e:
            print(f"Meraki API error: {e}")
            print(f"status code = {e.status}")
            print(f"reason = {e.reason}")
            print(f"error = {e.message}")
            continue
    exit(0)
if __name__ == "__main__":
    main()
