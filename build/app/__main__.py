from datetime import datetime
from functools import partial
from pathlib import Path
import argparse

from pulumi import automation as auto  # type: ignore
import ansible_runner  # type: ignore


def get_clargs():
    parser = argparse.ArgumentParser(
        prog='bureaubuild',
        description='Build bureau images',
    )
    parser.add_argument(
        'steps',
        action='store',
        choices=['all', 'provision', 'build', 'register', 'destroy', 'remove'],
        nargs='+',
        default=['all'],
        help='action(s) to perform'
    )
    parser.add_argument(
        '--stack-name',
        action='store',
        required=False,
        help='specify a stack name'
    )

    return parser.parse_args()


def run_step(step_name, steps):
    if ('all' in steps or step_name in steps):
        return True
    else:
        return False


def main():
    clargs = get_clargs()

    if clargs.stack_name:
        stack_name = clargs.stack_name
        date_string = clargs.stack_name.split('_')[1]
    else:
        date_string = datetime.today().strftime('%Y%m%dT%H%M%S')
        stack_name = f'dev_{date_string}'

    step = partial(run_step, steps=clargs.steps)

    work_dir = (
        Path(__file__).parent.parent.absolute() / 'infrastructure/'
    )
    stack = auto.create_or_select_stack(
        stack_name=stack_name,
        work_dir=work_dir
    )
    stack.set_config('date_string', auto.ConfigValue(value=date_string))
    stack.set_config('azure-native:location',
                     auto.ConfigValue(value='uksouth'))
    stack.refresh(on_output=print)

    if step('provision'):
        up_result = stack.up(on_output=print)

        print(f'Focal IP: {up_result.outputs["focal_ip"].value}')
        print(f'{type(up_result.outputs["focal_ip"].value)}')

    if step('build'):
        outputs = stack.workspace.stack_outputs(stack_name)
        inventory = {
            'all': {
                'hosts': {
                    name.split('_')[0]: {
                        'ansible_host': str(ip),
                        'ansible_user': 'build_admin'
                    }
                    for name, ip in outputs.items()
                }
            }
        }

        ansible_runner.run(
            role='bureau',
            roles_path=str(
                (Path(__file__).parent.parent.parent).absolute()
            ),
            inventory=inventory,
            cmdline='--become'
        )

    if step('register'):
        pass

    if step('destroy'):
        stack.destroy(on_output=print)

    if step('remove'):
        stack.workspace.remove_stack(stack_name=stack_name)


if __name__ == '__main__':
    main()
