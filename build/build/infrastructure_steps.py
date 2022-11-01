from pulumi import automation as auto  # type: ignore

from .infrastructure import pulumi_program


def get_stack(stack_name):
    stack = auto.create_or_select_stack(
        project_name='bureau_build',
        stack_name=stack_name,
        program=pulumi_program
    )

    return stack


def set_stack_config(stack, date_string):
    stack.set_config('date_string', auto.ConfigValue(value=date_string))
    stack.set_config('azure-native:location',
                     auto.ConfigValue(value='uksouth'))


def refresh_stack(stack):
    stack.refresh(on_output=print)


def provision(stack):
    up_result = stack.up(on_output=print)

    print(f'Focal IP: {up_result.outputs["focal_ip"].value}')
    print(f'{type(up_result.outputs["focal_ip"].value)}')


def destroy(stack):
    stack.destroy(on_output=print)

    print('\nIgnore the pulumi message above, there is no pulumi project file')
    print('Instead, either use the fully-qualified stack name, or run this app'
          f' with the flags [remove --stack-name {stack.name}]')


def remove_stack(stack):
    print(f'Removing stack {stack.name}')
    stack.workspace.remove_stack(stack_name=stack.name)
