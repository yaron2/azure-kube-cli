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
