from datetime import datetime
from time import sleep

from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import GalleryArtifactVersionSource
from azure.mgmt.compute.models import GalleryImageVersion
from azure.mgmt.compute.models import GalleryImageVersionPublishingProfile
from azure.mgmt.compute.models import GalleryImageVersionStorageProfile
from azure.mgmt.compute.models import TargetRegion


def get_azure_credential():
    return AzureCliCredential()


def get_compute_client(credential, subscription_id):
    return ComputeManagementClient(credential, subscription_id)


def get_image_gallery(stack, compute_client):
    outputs = stack.outputs()
    gallery = compute_client.galleries.get(
        resource_group_name=outputs['gallery_resource_group_name'],
        gallery_name=outputs['gallery_name']
    )
    return gallery


def gallery_image_identifier(sku):
    return dict(
        publisher='The_Alan_Turing_Institute',
        offer='Bureau',
        sku=sku
    )


def get_image_definitions(stack, compute_client):
    outputs = stack.outputs()

    return [
        compute_client.gallery_images.get(
            resource_group_name=outputs['gallery_resource_group_name'],
            gallery_name=outputs['gallery_name'],
            gallery_image_name=outputs[f'{sku}_image_name']
        )
        for sku in ['focal', 'jammy']
    ]


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
        print('\n'.join(
            f'{name}: {value.status()}'
            for name, value in image_versions.items()
        ))
        sleep(30)
