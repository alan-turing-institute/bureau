import pulumi
from pulumi_azure_native import compute, resources

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(
    'resource_group',
    resource_group_name='bureau'
)

gallery = compute.Gallery(
    "gallery",
    gallery_name="bureau_gallery",
    resource_group_name=resource_group.name
)
