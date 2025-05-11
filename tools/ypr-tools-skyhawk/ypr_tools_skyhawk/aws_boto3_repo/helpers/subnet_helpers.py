import pandas as pd
import ipaddress

def get_subnet_info(subnets):
    store = list()
    for i in subnets:
        subnet_info = {
        "subnet_id": i.get("SubnetId", "-"),
        "vpc_id": i.get("VpcId", "-"),
        "az": i.get("AvailabilityZone", "-"),
        "state": i.get("State", "-"),
        "cidr_block": i.get("CidrBlock") or "-"
                }
        store.append(subnet_info.copy())
    df = pd.DataFrame(store)
    df['cidr_sort_key'] = df['cidr_block'].apply(lambda x: ipaddress.ip_network(x))
    df = df.sort_values(by=["cidr_sort_key", "az", "subnet_id"])
    df = df.drop(columns=["cidr_sort_key"])
    df = df.reset_index(drop=True)
    # return values as list and header as list
    table_data = df.values.tolist()
    header = df.columns.tolist()
    return table_data, header
