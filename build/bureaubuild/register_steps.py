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
