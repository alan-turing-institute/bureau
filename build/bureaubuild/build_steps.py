from pathlib import Path

import ansible_runner  # type: ignore


def build(stack):
    outputs = stack.outputs()
    inventory = {
        'all': {
            'hosts': {
                name: {
                    'ansible_host': str(ip),
                    'ansible_user': 'build_admin'
                }
                for name, ip in outputs['ips'].value.items()
            }
        }
    }

    runner = ansible_runner.run(
        role='bureau',
        roles_path=str(
            # Path to directory containing the bureau role directory
            (Path(__file__).parent.parent.parent).absolute()
        ),
        inventory=inventory,
        cmdline='--become'
    )

    if runner.rc != 0:
        print('Ansible returned non-zero code')
        print(f'{runner.status}: {runner.rc}')
        exit(1)
