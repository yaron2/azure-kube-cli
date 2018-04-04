# Azure CLI Extension for ACS/AKS Infrastructure Operations

![Python](https://img.shields.io/pypi/pyversions/azure-cli.svg?maxAge=2592000)

This CLI extension allows for various general purpose operations for Kubernetes clusters running on Azure.

Currently supports migration of Persistent Volumes and Data Disks between a source ACS (Azure Container Service) cluster and a target AKS (Managed Kubernetes) cluster.

## Features

The CLI extension will let you:

- Migrate Persistent Volumes resources from ACS to AKS
- Move Unmanaged Data Disks from ACS to AKS 
- Move Managed Data Disks from ACS to AKS
- Migrate clusters between regions

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
Command
    az kube copy-volumes: Copy Persistent Volumes from ACS to AKS.
        Creates Managed Disks in target AKS resource group using storage snapshots and copies PV k8s
        resources from ACS cluster to AKS. Supports cross-region copies.

Arguments
    --source-acs-name [Required]: Name of the source ACS instance.
    --target-aks-name [Required]: Name of the target AKS instance.
    --source-kubeconfig         : Path to the source cluster kubeconfig file.
    --target-kubeconfig         : Path to the target cluster kubeconfig file.

Global Arguments
    --debug                     : Increase logging verbosity to show all debug logs.
    --help -h                   : Show this help message and exit.
    --output -o                 : Output format.  Allowed values: json, jsonc, table, tsv.  Default:
                                  json.
    --query                     : JMESPath query string. See http://jmespath.org/ for more
                                  information and examples.
    --verbose                   : Increase logging verbosity. Use --debug for full debug logs.
```

## Usage Examples

### migrate an ACS cluster to AKS

`az kube copy-volumes --source-acs-name=myacs --target-aks-name=myaks"`

### migrate and use your own source and target kubeconfigs

`az kube copy-volumes --source-kubeconfig=~/.source --target-kubeconfig=~/.target --source-acs-name=myacs --target-aks-name=myaks"`

## Development

Extension development depends on a local Azure CLI dev environment. First, follow these [instructions](https://github.com/Azure/azure-cli/blob/master/doc/configuring_your_machine.md) to prepare your machine.

Next, update your `AZURE_EXTENSION_DIR` environment variable to a target extension deployment directory. This overrides the standard extension directory.

Example `export AZURE_EXTENSION_DIR=~/.azure/devcliextensions/`

Run the following command to setup and install all dependencies in the extension deployment directory.

`pip install -U --target <extension deployment directory>/azure_kube_cli_ext <kube extension code root>`

Repeat the above command as needed.

At this point, assuming the setup is good the extension should be loaded and you should see the extension command space. Use `az --debug` and `az extension list` for debugging this step.

Helpful [Reference](https://github.com/Azure/azure-cli/tree/master/doc/extensions) docs for Az CLI Extension development