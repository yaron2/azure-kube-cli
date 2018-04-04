from kubernetes import client, config
from kubernetes.client.rest import ApiException

def get_persistent_volumes(kubeconfig_path):
    config.load_kube_config(kubeconfig_path)
    v1 = client.CoreV1Api()

    pvs = v1.list_persistent_volume()
    return pvs.items

def create_pv_from_current_pv(kubeconfig_path, pv):
    config.load_kube_config(kubeconfig_path)
    v1 = client.CoreV1Api()

    newpv = client.V1PersistentVolume()
    newpv.kind = "PersistentVolume"
    newpv.api_version = "v1"
    newpv.metadata = client.V1ObjectMeta()
    newpv.metadata.name = pv.metadata.name

    newpv.spec = client.V1PersistentVolumeSpec()
    newpv.spec.capacity = pv.spec.capacity
    newpv.spec.access_modes = pv.spec.access_modes
    newpv.spec.azure_disk = pv.spec.azure_disk

    if pv.spec.azure_disk.kind.lower() == 'managed':
        newpv.spec.azure_disk.disk_name = pv.target_disk_name
    else:
        newpv.spec.azure_disk.disk_uri = pv.target_disk_uri
    
    try:
        v1.create_persistent_volume(newpv)
    except ApiException:
        return False

    return True
