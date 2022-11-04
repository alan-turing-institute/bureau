from datetime import datetime
from time import sleep

from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import GalleryArtifactVersionSource
from azure.mgmt.compute.models import GalleryImageVersion
from azure.mgmt.compute.models import GalleryImageVersionPublishingProfile
from azure.mgmt.compute.models import GalleryImageVersionStorageProfile
from azure.mgmt.compute.models import TargetRegion


def register(stack, subscription_id):
    credential = get_azure_credential()
    compute_client = get_compute_client(credential, subscription_id)
    create_image_versions(stack, compute_client)


def get_azure_credential():
    return AzureCliCredential()


def get_compute_client(credential, subscription_id):
    return ComputeManagementClient(credential, subscription_id)


def create_image_versions(stack, compute_client):
    outputs = stack.outputs()

    dt = datetime.strptime(outputs['date_string'].value, '%Y%m%dT%H%M%S')
    version_name = dt.strftime('%Y.%m%d.%H%M%S')

    target_regions = [TargetRegion(name=outputs['location'])]

    print("\nCreating image versions")

    image_versions = {
        sku: compute_client.gallery_image_versions.begin_create_or_update(
            resource_group_name=outputs['gallery_resource_group_name'],
            gallery_name=outputs['gallery_name'],
            gallery_image_name=outputs[f'{sku}_image_name'],
            gallery_image_version_name=version_name,
            gallery_image_version=GalleryImageVersion(
                location=outputs['location'],
                publishing_profile=GalleryImageVersionPublishingProfile(
                    target_regions=target_regions,
                    replica_count=1,
                    storage_account_type='Standard_ZRS'
                ),
                storage_profile=GalleryImageVersionStorageProfile(
                    source=GalleryArtifactVersionSource(
                        id=outputs[f'{sku}_id']
                    )
                )
            )
        )
        for sku in ['focal', 'jammy']
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
