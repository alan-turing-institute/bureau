from time import sleep

from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import (GalleryArtifactVersionSource,
                                       GalleryImageVersion,
                                       GalleryImageVersionPublishingProfile,
                                       GalleryImageVersionStorageProfile,
                                       TargetRegion)
from fabric import ThreadingGroup as Group

from . import datestring


def get_compute_client(subscription_id):
    credential = AzureCliCredential()

    return ComputeManagementClient(credential, subscription_id)


def generalise(stack):
    outputs = stack.outputs()

    print('\nPreparing VMs for generalisation')

    group = Group(
        *[outputs['ips'].value[sku] for sku in outputs['skus'].value],
        user=outputs['admin_username'].value
    )
    group.sudo('waagent -deprovision+user -force')


def register(stack):
    outputs = stack.outputs()
    compute_client = get_compute_client(outputs['subscription_id'].value)

    version_name = datestring.image_version_string(
        outputs['date_string'].value)

    print('\nCreating image versions')

    image_versions = {
        sku: compute_client.gallery_image_versions.begin_create_or_update(
            resource_group_name=outputs['gallery_resource_group_name'],
            gallery_name=outputs['gallery_name'],
            gallery_image_name=outputs['image_names'].value[sku],
            gallery_image_version_name=version_name,
            gallery_image_version=GalleryImageVersion(
                location=outputs['location'],
                publishing_profile=GalleryImageVersionPublishingProfile(
                    target_regions=[TargetRegion(name=outputs['location'])],
                    replica_count=1,
                    storage_account_type='Standard_ZRS'
                ),
                storage_profile=GalleryImageVersionStorageProfile(
                    source=GalleryArtifactVersionSource(
                        id=outputs['ids'].value[sku]
                    )
                )
            )
        )
        for sku in outputs['skus'].value
    }

    print('\nStatus:')
    while not all([item.done() for item in image_versions.values()]):
        print_status(image_versions)
        sleep(30)

    print_status(image_versions)


def print_status(pollers):
    print('\n'.join(
        f'{name}: {value.status()}'
        for name, value in pollers.items()
    ))
