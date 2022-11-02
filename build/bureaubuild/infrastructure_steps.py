from pulumi import automation as auto  # type: ignore

from .infrastructure import pulumi_program


def get_stack(stack_name):
    stack = auto.create_or_select_stack(
        project_name='bureau_build',
        stack_name=stack_name,
        program=pulumi_program
    )

    return stack


def install_plugins(stack):
    stack.workspace.install_plugin('azure-native', 'v1.80.0')


def set_stack_config(stack, date_string, subscription_id, pulumi_org):
    stack.set_config('azure-native:location',
                     auto.ConfigValue(value='uksouth'))
    stack.set_config('azure-native:subscriptionId',
                     auto.ConfigValue(value=subscription_id))
    stack.set_config('date_string', auto.ConfigValue(value=date_string))
    stack.set_config('pulumi_org', auto.ConfigValue(value=pulumi_org))


def refresh_stack(stack):
    stack.refresh(on_output=print)


def provision(stack):
    stack.up(on_output=print)


def destroy(stack):
    stack.destroy(on_output=print)

    print('\nIgnore the pulumi message above, there is no pulumi project file')
    print('Instead, either use the fully-qualified stack name, or run this app'
          f' with the flags [remove --stack-name {stack.name}]')


def remove_stack(stack):
    print(f'Removing stack {stack.name}')
    stack.workspace.remove_stack(stack_name=stack.name)
