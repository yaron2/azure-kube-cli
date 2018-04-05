from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import re
import os

type_map = {'kubernetes.client.models.v1_replication_controller.V1ReplicationController': 'ReplicationController',
'kubernetes.client.models.v1_limit_range.V1LimitRange': 'LimitRange', 'kubernetes.client.models.v1_service.V1Service': 'Service',
'kubernetes.client.models.v1_config_map.V1ConfigMap': 'ConfigMap', 'kubernetes.client.models.v1_resource_quota.V1ResourceQuota': 'ResourceQuota',
'kubernetes.client.models.v1_daemon_set': 'DaemonSet', 'kubernetes.client.models.v1_deployment.V1Deployment': 'Deployment',
'kubernetes.client.models.v1_stateful_set.V1StatefulSet': 'StatefulSet', 'kubernetes.client.models.v1_horizontal_pod_autoscaler': 'V1HorizontalPodAutoscaler',
'kubernetes.client.models.v1_secret.V1Secret': 'Secret', 'kubernetes.client.models.v1_namespace.V1Namespace': 'Namespace',
'kubernetes.client.models.v1beta1_storage_class.V1beta1StorageClass': 'StorageClass'}

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

def get_cluster_resources(kubeconfig_path):
    config.load_kube_config(kubeconfig_path)
    coreV1 = client.CoreV1Api()
    extV1 = client.ExtensionsV1beta1Api()
    appsV1 = client.AppsV1beta1Api()
    storageV1 = client.StorageV1beta1Api()
    autoscaleV1 = client.AutoscalingV1Api()

    fields_to_remove_for_ns = ['status', 'uid', 'selfLink', 'resourceVersion', 'creationTimestamp', 'generation']
    fields_to_remove_for_resources = ['clusterIP', 'claimRef', 'securityContext', 'terminationGracePeriodSeconds', 'restartPolicy', 'nodePort', 'dnsPolicy']
    fields_to_remove_for_resources.extend(fields_to_remove_for_ns)

    ns_exclusions = ['kube-system']

    response = coreV1.list_namespace()
    all_namespaces = client.ApiClient().sanitize_for_serialization(fix_kubernetes_objects(response.items))
    namespaces = [n for n in all_namespaces if n['metadata']['name'] not in ns_exclusions]

    resources = []

    storage_classes = client.ApiClient().sanitize_for_serialization(fix_kubernetes_objects(storageV1.list_storage_class().items))
    resources.extend(storage_classes)

    list_of_operations = [coreV1.list_namespaced_replication_controller,coreV1.list_namespaced_limit_range,coreV1.list_namespaced_service,
        coreV1.list_namespaced_config_map,coreV1.list_namespaced_resource_quota,extV1.list_namespaced_daemon_set,extV1.list_namespaced_deployment,
        appsV1.list_namespaced_stateful_set,autoscaleV1.list_namespaced_horizontal_pod_autoscaler,coreV1.list_namespaced_secret]


    for ns in namespaces:
        __delete_keys_from_dict__(ns, fields_to_remove_for_ns)
        ns_name = ns['metadata']['name']

        for op in list_of_operations:
            res = client.ApiClient().sanitize_for_serialization(fix_kubernetes_objects(op(ns_name).items))
            resources.extend(res)

        resources.append(ns)


    filtered = []

    for r in resources:
            if 'type' in r and r['type'] == 'kubernetes.io/service-account-token':
                continue

            # bypass kubernetes python client bug... again. manually detect StorageClasses...
            if 'provisioner' in r:
                r['apiVersion'] = 'storage.k8s.io/v1'
            else:
                r['apiVersion'] = 'v1'
            
            __delete_keys_from_dict__(r, fields_to_remove_for_resources)
            filtered.append(r)

    return filtered


def fix_kubernetes_objects(items, api_version = 'v1'):
    # bypass kubernetes python client bug...
    for item in items:
        item_type = str(type(item))
        item.kind = type_map[re.findall(r"'(.*?)'", item_type, re.DOTALL)[0]]

    return items

def export_cluster_to_dir(kubeconfig_path, output_dir):
    resources = get_cluster_resources(kubeconfig_path)
    items_obj = {'kind': 'List', 'items': resources, 'apiVersion': 'v1'}

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    
    file = open(os.path.join(output_dir, "cluster.json"), 'w')
    file.write(json.dumps(items_obj))

    file.close()


def __delete_keys_from_dict__(dict_del, lst_keys):
    for k in lst_keys:
        try:
            del dict_del[k]
        except KeyError:
            pass
    for v in dict_del.values():
        if isinstance(v, dict):
            __delete_keys_from_dict__(v, lst_keys)

    return dict_del
