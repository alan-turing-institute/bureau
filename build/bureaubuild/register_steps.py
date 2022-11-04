from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient


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


# def create_image_version(stack, compute_client):
#     outputs = stack.outputs()

#     poller = compute_client.gallery_image_versions.begin_create_or_update(
#         resource_group_name=outputs['gallery_resource_group_name'],
#         gallery_name=outputs['gallery_name'],
#         gallery_image_name='bureau',
#         gallery_image_verison_name=outputs['date_string'],
#         gallery_image_version=GalleryImageVersion(
#             location=outputs['location'],

#         )
#     )
#     image_version = poller.result()
#     return image_version
