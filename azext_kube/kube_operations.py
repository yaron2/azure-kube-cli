from knack.log import get_logger
from knack.util import CLIError
from .cli_utils import az_cli
from collections import namedtuple
from azext_kube import storage
from azext_kube import kubewrapper
import uuid
import os


def get_clusters_info(source_acs_name, acs_resourcegroup, target_aks_name, aks_resourcegroup):
    acs_clusters = az_cli(['acs', 'list'])
    if acs_clusters:
        filtered_acs = [c for c in acs_clusters if c['resourceGroup'].lower() == acs_resourcegroup and c['name'] == source_acs_name]

        if not filtered_acs:
            raise CLIError(
                'ACS Cluster with name {0} not found'.format(source_acs_name))

        source_acs = filtered_acs[0]
        print("Found source ACS cluster with name {0}".format(source_acs_name))
        source_resource_group = source_acs['resourceGroup']
        source_location = source_acs['location']
    else:
        source_resource_group = acs_resourcegroup
        source_location = raw_input("ACS Location:")
    aks_clusters = az_cli(['aks', 'list'])
    filtered_aks = [c for c in aks_clusters if c['resourceGroup'].lower() == aks_resourcegroup and c['name'] == target_aks_name]

    if not filtered_aks:
        raise CLIError(
            'AKS Cluster with name {0} not found'.format(target_aks_name))

    target_aks = filtered_aks[0]
    print("Found target AKS cluster with name {0}".format(target_aks_name))

    target_resource_group = target_aks['resourceGroup']
    target_mc_resource_group = 'mc_{0}_{1}_{2}'.format(target_resource_group, target_aks['name'], target_aks['location'])
    target_location = target_aks['location']

    ClusterInfo = namedtuple('ClusterInfo', 'acs_resource_group aks_resource_group aks_mc_resource_group acs_name aks_name acs_location aks_location')

    info = ClusterInfo(acs_resource_group=source_resource_group, acs_name=source_acs_name,
                       aks_mc_resource_group=target_mc_resource_group, aks_resource_group=target_resource_group,
                       aks_name=target_aks_name, acs_location=source_location, aks_location=target_location)

    return info


def get_aks_clusters_info(source_aks_name, source_aks_resourcegroup, target_aks_name, target_aks_resourcegroup):
    
    aks_clusters = az_cli(['aks', 'list'])

#Target AKS Cluster Info

    filtered_target_aks = [c for c in aks_clusters if c['resourceGroup'].lower() == target_aks_resourcegroup and c['name'] == target_aks_name]

    if not filtered_target_aks:
        raise CLIError(
            'Target AKS Cluster with name {0} not found'.format(target_aks_name))

    target_aks = filtered_target_aks[0]
    print("Found target AKS cluster with name {0}".format(target_aks_name))

    target_resource_group = target_aks['resourceGroup']
    target_mc_resource_group = 'mc_{0}_{1}_{2}'.format(target_resource_group, target_aks['name'], target_aks['location'])
    target_location = target_aks['location']

#Source AKS Cluster Info
    filtered_source_aks = [c for c in aks_clusters if c['resourceGroup'].lower() == source_aks_resourcegroup and c['name'] == source_aks_name]

    if not filtered_source_aks:
        raise CLIError(
            'Source AKS Cluster with name {0} not found'.format(source_aks_name))

    source_aks = filtered_source_aks[0]
    print("Found source AKS cluster with name {0}".format(source_aks_name))

    source_resource_group = source_aks['resourceGroup']
    source_mc_resource_group = 'mc_{0}_{1}_{2}'.format(source_resource_group, source_aks['name'], source_aks['location'])
    source_location = source_aks['location']



    ClusterInfo = namedtuple('ClusterInfo', 'source_aks_resource_group source_aks_mc_resource_group target_aks_resource_group target_aks_mc_resource_group source_cluster_name target_cluster_name source_aks_location target_aks_location')

    info = ClusterInfo(source_aks_resource_group=source_resource_group, source_aks_mc_resource_group=source_mc_resource_group, source_cluster_name=source_aks_name,
                       target_aks_mc_resource_group=target_mc_resource_group, target_aks_resource_group=target_resource_group,
                       target_cluster_name=target_aks_name, source_aks_location=source_location, target_aks_location=target_location)

    return info



def get_kubeconfig(cli_service, name, resource_group):
    output_path = os.path.join(os.getcwd(), str(uuid.uuid4()))

    if cli_service.lower() == 'aks':
        az_cli([cli_service, 'get-credentials', '-n', name, '-g', resource_group, '-f', output_path])
    elif cli_service.lower() == 'acs':
        az_cli([cli_service, 'kubernetes', 'get-credentials', '-n', name, '-g', resource_group, '-f', output_path])

    if not os.path.isfile(output_path):
        raise CLIError(
            'Failed getting credentials for {0} cluster with cmd {1}'.format(cli_service, name))

    return output_path


def get_pvs_from_source(kubeconfig_path):
    pvs = kubewrapper.get_persistent_volumes(kubeconfig_path)

    if not pvs:
        raise CLIError(
            "No Persistent Volumes found to migrate")

    return pvs


def export_cluster_to_dir(kubeconfig_path, output_dir = os.getcwd()):
    kubewrapper.export_cluster_to_dir(kubeconfig_path, output_dir)
    print("Cluster exported successfully")


def copy_volumes(source_acs_name, target_aks_name, acs_resourcegroup, aks_resourcegroup, source_kubeconfig=None, target_kubeconfig=None):
    clusters_info = get_clusters_info(source_acs_name, acs_resourcegroup,  target_aks_name, aks_resourcegroup)

    remove_source_config = False
    remove_target_config = False

    if not source_kubeconfig:
        source_kubeconfig = get_kubeconfig('acs', clusters_info.acs_name, clusters_info.acs_resource_group)
        remove_source_config = True

    source_pvs = get_pvs_from_source(source_kubeconfig)

    print("Starting migration of {0} Persistent Volumes from ACS cluster {1} in {2} to AKS cluster {3} in {4}".format(len(source_pvs), clusters_info.acs_name,
        clusters_info.acs_location, clusters_info.aks_name, clusters_info.aks_location))

    for pv in source_pvs:
        if pv.spec.azure_disk.kind.lower() == 'managed':
            disk_name = pv.spec.azure_disk.disk_name
            disk = storage.copy_disk_to_disk(clusters_info.acs_resource_group, disk_name ,clusters_info.aks_mc_resource_group)
            pv.target_disk_name = disk['name']
            pv.target_disk_uri = disk['id']
        else:
            disk_uri = pv.spec.azure_disk.disk_uri
            disk = storage.copy_vhd_to_disk(disk_uri, clusters_info.aks_mc_resource_group)
            pv.target_disk_uri = disk['creationData']['sourceUri']
    print("Disks migration successful")
    print("Starting Persistent Volume creation on target cluster")

    if not target_kubeconfig:
        target_kubeconfig = get_kubeconfig('aks', clusters_info.aks_name, clusters_info.aks_resource_group)
        remove_target_config = True

    # this is a shady business right here.
    for pv in source_pvs:
        pv_copy_result = kubewrapper.create_pv_from_current_pv(target_kubeconfig, pv)

        if pv_copy_result:
            print("Persistent Volume migration successful")
        else:
            print("Failed migrating Persistent Volumes")

    if remove_source_config:
        os.remove(source_kubeconfig)
    
    if remove_target_config:
        os.remove(target_kubeconfig)
        
    print("All done")


def copy_aks_volumes(source_aks_name, target_aks_name, source_aks_resourcegroup, target_aks_resourcegroup, source_kubeconfig=None, target_kubeconfig=None):
    clusters_info = get_aks_clusters_info(source_aks_name, source_aks_resourcegroup,  target_aks_name, target_aks_resourcegroup)

    remove_source_config = False
    remove_target_config = False

    if not source_kubeconfig:
        source_kubeconfig = get_kubeconfig('aks', clusters_info.source_aks_name, clusters_info.source_aks_resource_group)
        remove_source_config = True

    source_pvs = get_pvs_from_source(source_kubeconfig)

    print("Starting migration of {0} Persistent Volumes from AKS cluster {1} in {2} to AKS cluster {3} in {4}".format(len(source_pvs), clusters_info.source_cluster_name,
        clusters_info.source_aks_location, clusters_info.target_cluster_name, clusters_info.target_aks_location))

    for pv in source_pvs:
        if pv.spec.azure_disk.kind.lower() == 'managed':
            disk_name = pv.spec.azure_disk.disk_name
            disk = storage.copy_disk_to_disk(clusters_info.source_aks_mc_resource_group, disk_name ,clusters_info.target_aks_mc_resource_group)
            pv.target_disk_name = disk['name']
            pv.target_disk_uri = disk['id']
        else:
            disk_uri = pv.spec.azure_disk.disk_uri
            disk = storage.copy_vhd_to_disk(disk_uri, clusters_info.aks_mc_resource_group)
            pv.target_disk_uri = disk['creationData']['sourceUri']
    print("Disks migration successful")
    print("Starting Persistent Volume creation on target cluster")

    if not target_kubeconfig:
        target_kubeconfig = get_kubeconfig('aks', clusters_info.target_aks_name, clusters_info.target_aks_resource_group)
        remove_target_config = True

    # this is a shady business right here.
    for pv in source_pvs:
        pv_copy_result = kubewrapper.create_pv_from_current_pv(target_kubeconfig, pv)

        if pv_copy_result:
            print("Persistent Volume migration successful")
        else:
            print("Failed migrating Persistent Volumes")

    if remove_source_config:
        os.remove(source_kubeconfig)
    
    if remove_target_config:
        os.remove(target_kubeconfig)
        
    print("All done")