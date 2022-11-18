import pulumi
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi_azure_native import compute, network, resources
from pulumi_tls import PrivateKey


class BuildVMArgs:
    def __init__(
        self,
        resource_group: resources.ResourceGroup,
        image_reference: compute.ImageReferenceArgs,
        subnet: network.subnet,
        private_key: PrivateKey
    ):
        self.resource_group = resource_group
        self.image_reference = image_reference
        self.subnet = subnet
        self.private_key = private_key


class BuildVM(ComponentResource):
    admin_username = 'build_admin'

    def __init__(self, name: str, args: BuildVMArgs,
                 opts: ResourceOptions = None):
        super().__init__('custom:app:BuildVM', name, {}, opts)

        child_opts = ResourceOptions(parent=self)

        public_ip = network.PublicIPAddress(
            f'{name}_ip',
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            public_ip_address_version='IPv4',
            public_ip_allocation_method='Dynamic',
            sku=network.PublicIPAddressSkuArgs(
                name='Basic',
                tier='Regional',
            ),
            opts=child_opts,
        )

        nic = network.NetworkInterface(
            f'{name}_nic',
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            ip_configurations=[
                network.NetworkInterfaceIPConfigurationArgs(
                    name='buildvmipconfig',
                    subnet=network.SubnetArgs(id=args.subnet.id),
                    public_ip_address=network.PublicIPAddressArgs(
                        id=public_ip.id
                    )
                )
            ],
            opts=child_opts,
        )

        self.vm = compute.VirtualMachine(
            f'{name}_vm',
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            hardware_profile=compute.HardwareProfileArgs(
                vm_size='Standard_D4_v5',
            ),
            network_profile=compute.NetworkProfileArgs(network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(id=nic.id)
            ]),
            os_profile=compute.OSProfileArgs(
                computer_name='bureau',
                admin_username=self.admin_username,
                linux_configuration=compute.LinuxConfigurationArgs(
                    disable_password_authentication=True,
                    ssh=compute.SshConfigurationArgs(
                        public_keys=[compute.SshPublicKeyArgs(
                            key_data=(
                                args.private_key.public_key_openssh
                            ),
                            path='/home/build_admin/.ssh/authorized_keys'
                        )]
                    )
                )
            ),
            storage_profile=compute.StorageProfileArgs(
                image_reference=args.image_reference,
                os_disk=compute.OSDiskArgs(
                    name=f'{name}_osdisk',
                    caching=compute.CachingTypes.READ_WRITE,
                    create_option='FromImage',
                    managed_disk=compute.ManagedDiskParametersArgs(
                        storage_account_type='StandardSSD_LRS',
                    ),
                )
            ),
            opts=child_opts,
        )

        self.public_ip = self.vm.id.apply(
            lambda _: network.get_public_ip_address_output(
                public_ip_address_name=public_ip.name,
                resource_group_name=args.resource_group.name
            )
        )

        self.register_outputs({})


def pulumi_program():
    config = pulumi.Config()
    date_string = config.require('date_string')
    pulumi_org = config.require('pulumi_org')
    stack_prefix = pulumi.get_stack().split('_')[0]

    private_key = PrivateKey(
        'private_key',
        algorithm='RSA',
        rsa_bits=2048
    )

    # Create an Azure Resource Group
    resource_group = resources.ResourceGroup(
        'resource_group',
        resource_group_name=f'bureau_build_{date_string}'
    )

    vnet = network.VirtualNetwork(
        'vnet',
        virtual_network_name='vnet',
        resource_group_name=resource_group.name,
        address_space=network.AddressSpaceArgs(
            address_prefixes=['10.0.0.0/16'],
        ),
        subnets=[network.SubnetArgs(
            name='default',
            address_prefix='10.0.0.0/24'
        )]
    )

    skus = {
        'focal': BuildVMArgs(
            resource_group=resource_group,
            image_reference=compute.ImageReferenceArgs(
                offer='0001-com-ubuntu-server-focal',
                publisher='canonical',
                sku='20_04-lts-gen2',
                version='latest',
            ),
            subnet=vnet.subnets[0],
            private_key=private_key
        ),
        'jammy': BuildVMArgs(
            resource_group=resource_group,
            image_reference=compute.ImageReferenceArgs(
                offer='0001-com-ubuntu-server-jammy',
                publisher='canonical',
                sku='22_04-lts-gen2',
                version='latest',
            ),
            subnet=vnet.subnets[0],
            private_key=private_key
        )
    }

    vms = {
        sku: BuildVM(sku, args)
        for sku, args in skus.items()
    }

    # Export provider information
    provider_config = pulumi.Config('azure-native')
    pulumi.export('location', provider_config.require('location'))
    pulumi.export('subscription_id', provider_config.require('subscriptionId'))

    # Export build stack information
    pulumi.export('resource_group_name', resource_group.name)
    pulumi.export('skus', skus.keys())
    pulumi.export('names', {sku: vms[sku].vm.name for sku in skus.keys()})
    pulumi.export('ids', {sku: vms[sku].vm.id for sku in skus.keys()})
    pulumi.export(
        'ips', {sku: vms[sku].public_ip.ip_address for sku in skus.keys()})
    pulumi.export('admin_username', BuildVM.admin_username)
    pulumi.export('private_key', private_key.private_key_openssh)
    pulumi.export('date_string', date_string)

    # Export gallery stack information
    gallery_stack = StackReference(
        f'{pulumi_org}/bureau_gallery/{stack_prefix}')
    pulumi.export('gallery_name', gallery_stack.get_output('gallery_name'))
    pulumi.export('gallery_resource_group_name',
                  gallery_stack.get_output('gallery_resource_group_name'))
    pulumi.export('image_names', gallery_stack.get_output('image_names'))
