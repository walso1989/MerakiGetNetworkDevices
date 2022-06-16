# This is a sample Python script.

import json
import meraki
import pandas
import os

def get_organizationid(API_KEY, org_name):
    # get organization_ID
    dashboard = meraki.DashboardAPI(API_KEY)
    response = dashboard.organizations.getOrganizations()
    org_id = 0
    print(f" response from API {json.dumps(response, indent=2)}")
    org_name = "devnet"
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


def main():
    #Variable definitions
    API_KEY = "1f02da6afc079e16960440836c0a0e522f776d80"
    org_name = "FIFCO"
    current_path = os.getcwd()
    csv_file = current_path + "//VLAN-Info.csv"

    #getting organization ID and Networks within the organization
    organization_id = get_organizationid(API_KEY, org_name)
    network_id = get_networksid(API_KEY, organization_id)

    #to extract VLAN information from the different networks in the organization
    for network in network_id:
        checking_network = network["id"]
        print(f" Extracting list of VLANs for network ID: {checking_network}")
        dashboard = meraki.DashboardAPI(API_KEY)
        try:
            response = dashboard.appliance.getNetworkApplianceVlans(checking_network)
            print(f"{json.dumps(response, indent=2)}")
            try:
                df = pandas.DataFrame(response)
                df.to_csv(csv_file,index=True,sep=',',mode='a')
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
