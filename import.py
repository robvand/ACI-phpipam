import requests
import json
import acitoolkit.acitoolkit as aci

server = "http://ipam"
appid = "other"
username = ""
password = ""
token = ""
apic = "https://apic"
apicuser = ""
apicpw = ""

# Login to the APIC
session = aci.Session(apic, apicuser, apicpw)
resp = session.login()
if not resp.ok:
    print('%% Could not login to APIC')

data = []
longest_names = {'Tenant': len('Tenant'),
                 'Bridge Domain': len('Bridge Domain'),
                 'Subnet': len('Subnet'),
                 'Scope': len('Scope')}

def check_longest_name(item, title):

    if len(item) > longest_names[title]:
        longest_names[title] = len(item)

def get_subnet(session, tenant):

    bds = aci.BridgeDomain.get(session, tenant)
    for bd in bds:
        check_longest_name(bd.name, "Bridge Domain")
        subnets = aci.Subnet.get(session, bd, tenant)
        for subnet in subnets:
            check_longest_name(subnet.addr, "Subnet")
            check_longest_name(subnet.get_scope(), "Scope")
            subnet.addr.split('/')
            test_subnet = subnet.addr
            subnet = test_subnet.split('/', 1)[0]
            netmask = test_subnet.split('/', 1)[1]
            subnet = subnet[:subnet.rfind('.') + 1] + '0'
            desc = "ACI " + "Tenant: " + tenant.name + " " + "BD: " + bd.name
            data.append({'subnet': subnet, 'netmask': netmask, 'desc': desc})

tenants = aci.Tenant.get(session)
for tenant in tenants:
    check_longest_name(tenant.name, "Tenant"),
    get_subnet(session, tenant)

print(data)


i = 0
baseurl = server + "/api/" + appid

res = requests.post(baseurl + '/user/', auth=(username, password))
print(res.status_code)
print(res.content)
token = json.loads(res.content)['data']['token']

res = requests.get(baseurl + '/sections/', headers={'token': token})
print(res.status_code)
print(res.content)

res = requests.get(baseurl + '/sections/4/subnets/', headers={'token': token})
print(res.status_code)
print(res.content)

for subnet in data:
    res = requests.post(baseurl + '/subnets/', headers={'token': token}, data={
        "sectionId": "4",
        "subnet": subnet["subnet"],
        "mask": subnet["netmask"],
        "description": subnet["desc"]
    })
    i += 1