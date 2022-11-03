import pulumi
from pulumi import ComponentResource, ResourceOptions
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


class ImageDefinitionArgs:
    def __init__(
        self,
        gallery: compute.Gallery,
        resource_group: resources.ResourceGroup,
        sku: str
    ):
        self.gallery = gallery
        self.resource_group = resource_group
        self.sku = sku


class ImageDefinition(ComponentResource):
    def __init__(self, name: str, args: ImageDefinitionArgs,
                 opts: ResourceOptions = None):
        super().__init__("custom:app:ImageDefinition", name, {}, opts)
        child_opts = ResourceOptions(parent=self)

        compute.GalleryImage(
            name,
            resource_group_name=args.resource_group.name,
            gallery_name=args.gallery.name,
            identifier=compute.GalleryImageIdentifierArgs(
                publisher="The_Alan_Turing_Institute",
                offer="Bureau",
                sku=args.sku,
            ),
            os_state=compute.OperatingSystemStateTypes.GENERALIZED,
            os_type=compute.OperatingSystemTypes.LINUX,
            opts=child_opts
        )

        self.register_outputs({})


focal_image_definition, jammy_image_definition = (
    ImageDefinition(
        f"bureau_{sku}",
        ImageDefinitionArgs(
            gallery=gallery,
            resource_group=resource_group,
            sku=sku
        )
    )
    for sku in ["focal", "jammy"]
)


pulumi.export("gallery_resource_group_name", resource_group.name)
pulumi.export("gallery_name", gallery.name)
