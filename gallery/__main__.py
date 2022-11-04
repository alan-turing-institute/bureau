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

image_definitions = {
    sku: compute.GalleryImage(
        f"bureau_{sku}",
        resource_group_name=resource_group.name,
        gallery_name=gallery.name,
        hyper_v_generation="V2",
        identifier=compute.GalleryImageIdentifierArgs(
            publisher="The_Alan_Turing_Institute",
            offer="Bureau",
            sku=sku,
        ),
        os_state=compute.OperatingSystemStateTypes.SPECIALIZED,
        os_type=compute.OperatingSystemTypes.LINUX,
    )
    for sku in ["focal", "jammy"]
}


pulumi.export("gallery_resource_group_name", resource_group.name)
pulumi.export("gallery_name", gallery.name)
pulumi.export(
    "image_names",
    {
        sku: image_definition.name
        for sku, image_definition in image_definitions.items()
    }
)
