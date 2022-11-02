import argparse
from datetime import datetime
from functools import partial
from os import getenv

from dotenv import load_dotenv

from . import build_steps, infrastructure_steps


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

    # Process command line arguments
    if clargs.stack_name:
        stack_name = clargs.stack_name
        date_string = clargs.stack_name.split('_')[1]
    else:
        date_string = datetime.today().strftime('%Y%m%dT%H%M%S')
        stack_name = f'dev_{date_string}'

    # Process environment variables
    load_dotenv()
    subscription_id = getenv('SUBSCRIPTION_ID')

    step = partial(run_step, steps=clargs.steps)

    stack = infrastructure_steps.get_stack(stack_name)

    infrastructure_steps.install_plugins(stack)

    infrastructure_steps.set_stack_config(stack, date_string, subscription_id)

    infrastructure_steps.refresh_stack(stack)

    if step('provision'):
        infrastructure_steps.provision(stack)

    if step('build'):
        build_steps.build(stack)

    if step('register'):
        pass

    if step('destroy'):
        infrastructure_steps.destroy(stack)

    if step('remove'):
        infrastructure_steps.remove_stack(stack)


if __name__ == '__main__':
    main()
