# This is a sample Python script.

import json
import meraki
import logging

def get_organizationid(API_KEY, org_name):
    # get organization_ID
    dashboard = meraki.DashboardAPI(API_KEY)
    response = dashboard.organizations.getOrganizations()
    # if respose
    org_id = 0
    print(f" response from API {json.dumps(response, indent=2)}")
    org_name = "devnet"
    print(f" Looking for Organizaion: {org_name}")
    for org in response:
        if org_name.lower() in org["name"].lower():
            org_id = org["id"]
            break
    print(f" Organizaion Id for {org_name} is {org_id}")
    return(org_id)

def get_networksid(API_KEY , organization_id):
    print(f"Looking for networks in organization id {organization_id}")
    dashboard = meraki.DashboardAPI(API_KEY)
    response=dashboard.organizations.getOrganizationNetworks(organization_id)
    print(f" response from API {json.dumps(response, indent=2)}")
    return(response)

def main ():
    API_KEY="6bec40cf957de430a6f1f2baa056b99a4fac9ea0"
    org_name="devnet"
    organization_id=get_organizationid(API_KEY, org_name)
    network_id=get_networksid(API_KEY,organization_id)
    for network in network_id:
        checking_network=network["id"]
        print(f" Extracting list of VLANs for network ID: {checking_network}")
        dashboard = meraki.DashboardAPI(API_KEY)
        try:
            response = dashboard.appliance.getNetworkApplianceVlans(checking_network)
            print(f"{json.dumps(response, indent=2)}")
        except meraki.APIError as e:
            print(f'Meraki API error: {e}')
            print(f'status code = {e.status}')
            print(f'reason = {e.reason}')
            print(f'error = {e.message}')
            continue

if __name__ == "__main__":
    # Creating and setting logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    handler = logging.FileHandler("process.log")
    handler.setLevel(logging.INFO)

    # Create a logging format
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(handler)

    main()