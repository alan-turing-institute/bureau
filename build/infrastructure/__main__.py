from pathlib import Path
import pulumi
from pulumi import ComponentResource, ResourceOptions
from pulumi_azure_native import compute, network, resources


class BuildVMArgs:
    def __init__(
        self,
        resource_group: resources.ResourceGroup,
        image_reference: compute.ImageReferenceArgs,
        subnet: network.subnet
    ):
        self.resource_group = resource_group
        self.image_reference = image_reference
        self.subnet = subnet


class BuildVM(ComponentResource):
    def __init__(self, name: str, args: BuildVMArgs,
                 opts: ResourceOptions = None):
        super().__init__("custom:app:BuildVM", name, {}, opts)

        child_opts = ResourceOptions(parent=self)

        public_ip = network.PublicIPAddress(
            f"{name}_ip",
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            public_ip_address_version="IPv4",
            public_ip_allocation_method="Dynamic",
            sku=network.PublicIPAddressSkuArgs(
                name="Basic",
                tier="Regional",
            ),
            opts=child_opts,
        )

        nic = network.NetworkInterface(
            f"{name}_nic",
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            ip_configurations=[
                network.NetworkInterfaceIPConfigurationArgs(
                    name="buildvmipconfig",
                    subnet=network.SubnetArgs(id=args.subnet.id),
                    public_ip_address=network.PublicIPAddressArgs(
                        id=public_ip.id
                    )
                )
            ],
            opts=child_opts,
        )

        vm = compute.VirtualMachine(
            f"{name}_vm",
            resource_group_name=args.resource_group.name,
            location=args.resource_group.location,
            hardware_profile=compute.HardwareProfileArgs(
                vm_size="Standard_DC4s_v2",
            ),
            network_profile=compute.NetworkProfileArgs(network_interfaces=[
                compute.NetworkInterfaceReferenceArgs(id=nic.id)
            ]),
            os_profile=compute.OSProfileArgs(
                computer_name="bureau",
                admin_username="build_admin",
                linux_configuration=compute.LinuxConfigurationArgs(
                    disable_password_authentication=True,
                    ssh=compute.SshConfigurationArgs(
                        public_keys=[compute.SshPublicKeyArgs(
                            key_data=(open(f"{Path.home()}/.ssh/id_rsa.pub").read()),
                            path="/home/build_admin/.ssh/authorized_keys"
                        )]
                    )
                )
            ),
            storage_profile=compute.StorageProfileArgs(
                image_reference=args.image_reference,
                os_disk=compute.OSDiskArgs(
                    name=f"{name}_osdisk",
                    caching=compute.CachingTypes.READ_WRITE,
                    create_option="FromImage",
                    managed_disk=compute.ManagedDiskParametersArgs(
                        storage_account_type="StandardSSD_LRS",
                    ),
                )
            ),
            opts=child_opts,
        )

        self.public_ip = vm.id.apply(
            lambda _: network.get_public_ip_address_output(
                public_ip_address_name=public_ip.name,
                resource_group_name=resource_group.name
            )
        )

        self.register_outputs({})


config = pulumi.Config()
date_string = config.require('date_string')

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(
    'resource_group',
    resource_group_name=f'bureau_build_{date_string}'
)

vnet = network.VirtualNetwork(
    "vnet",
    virtual_network_name="vnet",
    resource_group_name=resource_group.name,
    address_space=network.AddressSpaceArgs(
        address_prefixes=["10.0.0.0/16"],
    ),
    subnets=[network.SubnetArgs(
        name="default",
        address_prefix="10.0.0.0/24"
    )]
)

vm_focal = BuildVM(
    "vm_focal",
    BuildVMArgs(
        resource_group=resource_group,
        image_reference=compute.ImageReferenceArgs(
                offer="0001-com-ubuntu-server-focal",
                publisher="canonical",
                sku="20_04-lts-gen2",
                version="latest",
            ),
        subnet=vnet.subnets[0]
    )
)


vm_jammy = BuildVM(
    "vm_jammy",
    BuildVMArgs(
        resource_group=resource_group,
        image_reference=compute.ImageReferenceArgs(
                offer="0001-com-ubuntu-server-jammy",
                publisher="canonical",
                sku="22_04-lts-gen2",
                version="latest",
            ),
        subnet=vnet.subnets[0]
    )
)


pulumi.export("focal_ip", vm_focal.public_ip)
pulumi.export("jammy_ip", vm_jammy.public_ip)
