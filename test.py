from azext_kube.cli_utils import az_cli

#source_acs = az_cli(['acs', 'list', '--query', "[?name=='{0}'] | [0] | [?resourceGroup=='{1}'] | [0]".format("storagecs", "STORAGERG")])
source_acs = az_cli(['acs', 'list'])
sa = [c for c in source_acs if c['resourceGroup'].lower() == 'storagerg' and c['name'] == 'storagecsa'][0]
x = 0
