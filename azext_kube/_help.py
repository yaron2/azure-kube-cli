from knack.help_files import helps

helps['kube copy-volumes'] = """
    type: command
    short-summary: Copy Persistent Volumes from ACS to AKS.
    long-summary: >
        Creates Managed Disks in target AKS resource group using storage snapshots and copies PV k8s resources from ACS cluster to AKS.
        Supports cross-region copies.
    parameters:
        - name: --source-acs-name
          type: string
          short-summary: Name of the source ACS instance
        - name: --target-aks-name
          type: string
          short-summary: Name of the target AKS instance
        - name: --source-kubeconfig
          type: string
          short-summary: Path to the source cluster kubeconfig file
        - name: --target-kubeconfig
          type: string
          short-summary: Path to the target cluster kubeconfig file
    examples:
        - name: Copy all Persistent Volumes from ACS to AKS
          text: >
            az kube copy-volumes --source-acs-name=acs-cluster --target-aks-name=aks-cluster
        - name: Copy using a custom Kubeconfig file
          text: >
            az kube copy-volumes --source-kubeconfig=/.myconfig --source-acs-name=acs-cluster --target-aks-name=aks-cluster
"""

helps['kube export'] = """
    type: command
    short-summary: Export a Kubernetes cluster's resources to disk
    long-summary: >
        Export deployments, replication controllers, secrets, limits, quotas, deployments, services, config maps, daemon sets, stateful sets
        and horizontal pod autoscalers to disk in a format that allows for a later restore
    parameters:
        - name: --kubeconfig
          type: string
          short-summary: Path to the cluster kubeconfig file
        - name: --output-dir
          type: string
          short-summary: The directory to write the backup to
    examples:
        - name: Export a cluster to dir
          text: >
            az kube export --kubeconfig=./myconfig --output-dir=./cluster
"""
