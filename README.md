# Azure CLI Extension for ACS/AKS Infrastructure Operations

![Python](https://img.shields.io/pypi/pyversions/azure-cli.svg?maxAge=2592000)

This CLI extension allows for various general purpose operations for Kubernetes clusters running on Azure.

Currently supports migration of Persistent Volumes and Data Disks between a source ACS (Azure Container Service) cluster and a target AKS (Managed Kubernetes) cluster as well as export the entire cluster state for backup/restore scenarios.

## Features

The CLI extension will let you:

- Take a snapshot of cluster state for back/restore purposes
- Migrate Persistent Volumes resources from ACS to AKS
- Migrate Persistent Volumes resources from AKS to AKS
- Move Unmanaged Data Disks from ACS to AKS 
- Move Managed Data Disks from ACS to AKS
- Migrate clusters between regions

### Cluster Backup Features

The following platforms are supported for cluster backup functionality:

- AKS
- ACS
- ACS-Engine
- OpenShift
- Tectonic

## Installation

### Step 0: Install/Update Azure CLI

Make sure you have the latest version of the Azure CLI installed.

If you don't have the Azure CLI intalled, follow the installation instructions on [GitHub](https://github.com/Azure/azure-cli) or [Microsoft Docs](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) to setup Azure CLI in your environment.

### Step 1: 

Navigate to this project's release tab in GitHub to see the list of releases. Run the extension add command using the `--source` parameter.

The argument for the source parameter is either the URL download path (the extension package ends with '.whl') of your chosen release, or the local path to the extension where you downloaded the release package.

`az extension add --source <local file path to release.whl OR  url for release.whl>`

For example, to install version 0.0.1

`az extension add --source 'https://github.com/yaron2/azure-kube-cli/releases/download/0.0.1/azure_kube_cli-0.0.1-py2.py3-none-any.whl'`

## Command-Line Usage

```bash
Group
    az kube

Commands:
    copy-volumes: Copy Persistent Volumes from ACS to AKS.
    copy-aks-volumes: Copy Persistent Volumes from AKS to AKS.
    export      : Export a Kubernetes cluster's resources to disk.
```

## Usage Examples

### migrate an ACS cluster to AKS

`az kube copy-volumes --source-acs-name=myacs --target-aks-name=myaks --acs-resourcegroup=rg1 --aks-resourcegroup=rg2`

### migrate and use your own source and target kubeconfigs

`az kube copy-volumes --source-kubeconfig=~/.source --target-kubeconfig=~/.target --source-acs-name=myacs --target-aks-name=myaks`

### migrate AKS cluster volumes to AKS

`az kube copy-aks-volumes --source-aks-name test-kube-source --source-aks-resourcegroup test-kube-source --target-aks-name test-kube-target --target-aks-resourcegroup test-kube-target --source-kubeconfig source.config --target-kubeconfig target.config`

### Backups a cluster's state

`az kube export --kubeconfig=./myconfig`

### Backups a cluster's state to a custom dir

`az kube export --kubeconfig=./myconfig --output-dir=./backup`

### Restore or migrate a cluster's state

Once you have executed the kube export command, the cluster's configuation will be generated and will be exported to a configuration file named cluster.json in the directory executed where executed or in the custom directory path specified. Execute the kubectl apply command on the cluster.json to import the saved cluster configuration. Make sure your config has the correct cluster context you want to restore to.

`kubectl apply -f cluster.json`

## Development

Extension development depends on a local Azure CLI dev environment. First, follow these [instructions](https://github.com/Azure/azure-cli/blob/master/doc/configuring_your_machine.md) to prepare your machine.

Next, update your `AZURE_EXTENSION_DIR` environment variable to a target extension deployment directory. This overrides the standard extension directory.

Example `export AZURE_EXTENSION_DIR=~/.azure/devcliextensions/`

Run the following command to setup and install all dependencies in the extension deployment directory.

`pip install -U --target <extension deployment directory>/azure_kube_cli_ext <kube extension code root>`

Repeat the above command as needed.

At this point, assuming the setup is good the extension should be loaded and you should see the extension command space. Use `az --debug` and `az extension list` for debugging this step.

Helpful [Reference](https://github.com/Azure/azure-cli/tree/master/doc/extensions) docs for Az CLI Extension development
