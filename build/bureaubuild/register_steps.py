from azure.identity import AzureCliCredential
from azure.mgmt.compute import ComputeManagementClient


def get_azure_credential():
    return AzureCliCredential()


def get_compute_client(credential, subscription_id):
    return ComputeManagementClient(credential, subscription_id)


def get_image_gallery(credential, subscription_id):
    # gallery = compute_client.galleries.get()
    pass
