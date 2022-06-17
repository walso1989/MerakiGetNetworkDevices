# This is a sample Python script.

import json
import meraki
import pandas
import os
import configparser

def get_organizationid(API_KEY, org_name):
    # get organization_ID
    dashboard = meraki.DashboardAPI(API_KEY)
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
    dashboard = meraki.DashboardAPI(API_KEY)
    response = dashboard.organizations.getOrganizationNetworks(organization_id)
    print(f" response from API {json.dumps(response, indent=2)}")
    return (response)

def get_organizationnames(API_KEY,network_id):
    networknames={}
    cont=0
    dashboard = meraki.DashboardAPI(API_KEY)
    for networks in network_id:
        checkingid=networks["id"]

        networknames=response["id"]["name"]
        cont=cont+1
    return(networknames)


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
        dashboard = meraki.DashboardAPI(API_KEY)
        insert_headers=True
        try:
            #get information about VLANS and Networks
            response = dashboard.appliance.getNetworkApplianceVlans(checking_network)
            response2 = dashboard.networks.getNetwork(checking_network)

            #Changes the dictionaries to dataframes
            vlansdetails = pandas.DataFrame(response)
            networkdetails = pandas.DataFrame(response2.items())

            #Transpose the datafram and remove first column -> this comes as a list so it is changed to dataframe the columns has integer names
            #here we transpose the dataframe (Invert colums and rows) then rename the colums and drop the first line of code
            networkdetails=pandas.DataFrame.transpose(networkdetails)
            networkdetails.rename(columns={0: 'id', 1:"organizationId",2:"productTypes",3: "url",4: "name", 5:"timeZone",6: "enrollmentString",7: "tags",8: "notes",9: "isBoundToConfigTemplate"}, inplace=True)
            networkdetails=networkdetails.iloc[1:,:]

            #merging both dataframes ***IT DOES NOT WORK YET
            df_merged = pandas.merge(vlansdetails,networkdetails,on=['networkId', 'id'])

            print(f"{json.dumps(response, indent=2)}")
            try:
                if insert_headers == True:
                    df = pandas.DataFrame(response)
                    df.to_csv(csv_file,index=True,sep=',',mode='a')
                    insert_headers=False
                else:
                    df = pandas.DataFrame(response)
                    df.to_csv(csv_file, index=True, sep=',', mode='a',header=False)
            except csv as strerror:
                logger.debug("Error creating File %s " + strerror)

        except meraki.APIError as e:
            print(f"Meraki API error: {e}")
            print(f"status code = {e.status}")
            print(f"reason = {e.reason}")
            print(f"error = {e.message}")
            continue
if __name__ == "__main__":
    main()
