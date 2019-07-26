from ._help import helps
from azure.cli.core import AzCommandsLoader


class KubeCommandsLoader(AzCommandsLoader):
    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        custom_type = CliCommandType(
            operations_tmpl='azext_kube.kube_operations#{}')
        super(KubeCommandsLoader, self).__init__(
            cli_ctx=cli_ctx, custom_command_type=custom_type)

    def load_command_table(self, args):
        with self.command_group('kube') as g:
            g.custom_command('copy-volumes', 'copy_volumes')
            g.custom_command('copy-aks-volumes', 'copy_aks_volumes')
            g.custom_command('export', 'export_cluster_to_dir')
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('kube copy-volumes') as c:
            c.argument('source_acs_name', options_list=['--source-acs-name'])
            c.argument('target_aks_name', options_list=['--target-aks-name'])
            c.argument('acs_resource_group', options_list=['--acs-resourcegroup'])
            c.argument('aks_resource_group', options_list=['--aks-resourcegroup'])
            c.argument('source_kubeconfig', options_list=['--source-kubeconfig'])
            c.argument('target_kubeconfig', options_list=['--target-kubeconfig'])
        with self.argument_context('kube copy-aks-volumes') as c:
            c.argument('source_aks_name', options_list=['--source-aks-name'])
            c.argument('target_aks_name', options_list=['--target-aks-name'])
            c.argument('source_aks_resource_group', options_list=['--source-aks-resourcegroup'])
            c.argument('target_aks_resource_group', options_list=['--target-aks-resourcegroup'])
            c.argument('source_kubeconfig', options_list=['--source-kubeconfig'])
            c.argument('target_kubeconfig', options_list=['--target-kubeconfig'])
        with self.argument_context('kube export') as c:
            c.argument('kubeconfig_path', options_list=['--kubeconfig'])
            c.argument('output_dir', options_list=['--output-dir'])


COMMAND_LOADER_CLS = KubeCommandsLoader
