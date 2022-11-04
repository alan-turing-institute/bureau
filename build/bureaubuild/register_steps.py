from time import sleep

from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import (GalleryArtifactVersionSource,
                                       GalleryImageVersion,
                                       GalleryImageVersionPublishingProfile,
                                       GalleryImageVersionStorageProfile,
                                       TargetRegion)

from . import datestring


def register(stack):
    outputs = stack.outputs()
    credential = AzureCliCredential()
    compute_client = ComputeManagementClient(
        credential, outputs['subscription_id'].value)

    create_image_versions(stack, compute_client)


def create_image_versions(stack, compute_client):
    outputs = stack.outputs()

    version_name = datestring.image_version_string(
        outputs['date_string'].value)

    print("\nCreating image versions")

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

    print("\nStatus:")
    while not all([item.done() for item in image_versions.values()]):
        print_status(image_versions)
        sleep(30)

    print_status(image_versions)


def print_status(image_versions):
    print('\n'.join(
        f'{name}: {value.status()}'
        for name, value in image_versions.items()
    ))
