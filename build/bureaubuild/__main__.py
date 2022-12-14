import argparse
from datetime import datetime
from functools import partial
from os import getenv
from time import sleep

from dotenv import load_dotenv

from . import build_steps, datestring, infrastructure_steps, register_steps


def get_clargs():
    parser = argparse.ArgumentParser(
        prog='bureaubuild',
        description='Build bureau images',
    )
    parser.add_argument(
        'steps',
        action='store',
        choices=['all', 'provision', 'build', 'generalise', 'register',
                 'destroy', 'remove'],
        nargs='+',
        default=['all'],
        help='action(s) to perform'
    )
    parser.add_argument(
        '--stack-prefix',
        action='store',
        required=False,
        help='specify a stack name prefix'
    )
    parser.add_argument(
        '--date-string',
        action='store',
        required=False,
        help='specify a date string, applied to stack prefix'
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
    if clargs.date_string:
        date_string = clargs.date_string
        if not datestring.validate_date_string(clargs.date_string):
            print(
                'Date string must be zero-padded and of the format'
                f' {date_string.fmt}')
            exit(1)
    else:
        date_string = datetime.today().strftime('%Y%m%dT%H%M%S')

    if clargs.stack_prefix:
        stack_prefix = clargs.stack_prefix
    else:
        stack_prefix = 'dev'

    stack_name = f'{stack_prefix}_{date_string}'

    # Process environment variables
    load_dotenv()
    subscription_id = getenv('SUBSCRIPTION_ID')
    pulumi_org = getenv('PULUMI_ORG')
    client_id = getenv('CLIENT_ID')
    client_secret = getenv('CLIENT_SECRET')
    tenant_id = getenv('TENANT_ID')

    step = partial(run_step, steps=clargs.steps)

    stack = infrastructure_steps.get_stack(stack_name)

    infrastructure_steps.install_plugins(stack)

    infrastructure_steps.set_stack_config(stack, date_string, subscription_id,
                                          pulumi_org, client_id, client_secret,
                                          tenant_id)

    infrastructure_steps.refresh_stack(stack)

    if step('provision'):
        infrastructure_steps.provision(stack)

    if step('provision') and step('build'):
        sleep_time = 120
        print(f'Waiting {sleep_time}s so that build VMs are available')
        sleep(sleep_time)

    if step('build'):
        build_steps.build(stack)

    if step('generalise'):
        register_steps.generalise(stack)

    if step('register'):
        register_steps.register(stack)

    if step('destroy'):
        infrastructure_steps.destroy(stack)

    if step('remove'):
        infrastructure_steps.remove_stack(stack)


if __name__ == '__main__':
    main()
