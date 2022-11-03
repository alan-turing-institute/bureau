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

focal_image_definition, jammy_image_definition = (
    compute.GalleryImage(
        f"bureau_{sku}",
        resource_group_name=resource_group.name,
        gallery_name=gallery.name,
        identifier=compute.GalleryImageIdentifierArgs(
            publisher="The_Alan_Turing_Institute",
            offer="Bureau",
            sku=sku,
        ),
        os_state=compute.OperatingSystemStateTypes.GENERALIZED,
        os_type=compute.OperatingSystemTypes.LINUX,
    )
    for sku in ["focal", "jammy"]
)


pulumi.export("gallery_resource_group_name", resource_group.name)
pulumi.export("gallery_name", gallery.name)
pulumi.export("focal_image_name", focal_image_definition.name)
pulumi.export("jammy_image_name", jammy_image_definition.name)
