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
        return self.command_table

    def load_arguments(self, _):
        with self.argument_context('kube copy-volumes') as c:
            c.argument('source_acs_name', options_list=['--source-acs-name'])
            c.argument('target_aks_name', options_list=['--target-aks-name'])
            c.argument('source_kubeconfig', options_list=['--source-kubeconfig'])
            c.argument('target_kubeconfig', options_list=['--target-kubeconfig'])


COMMAND_LOADER_CLS = KubeCommandsLoader
