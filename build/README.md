# bureau-build

Build and register bureau virtual machine images

## Dependencies

Python dependencies are defined in `pyproject.toml` and will be installed alongside the package.

```
pip install .
```

Additionally, [Pulumi](https://www.pulumi.com/) and [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) are required.
The Pulumi azure-native plugin is required but should be installed when running the build app.

## Prerequisites

You must be [logged in](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli) to Azure using the CLI.

You must also ensure you are [logged in](https://www.pulumi.com/docs/reference/cli/pulumi_login/) to the correct pulumi backend.

### Environment variables

| name            | value                               |
|-----------------|-------------------------------------|
| SUBSCRIPTION_ID | ID of the Azure subscription to use |
| PULUMI_ORG      | Name of the Pulumi organisation     |

The program uses [python-dotenv](https://pypi.org/project/python-dotenv/).
Environment variables may be set in a file called `.env` for convenience.

Additionally, if using a [service principal](https://learn.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli) to authenticate the following environment variables need to be defined

| name          | value                                       |
|---------------|---------------------------------------------|
| CLIENT_ID     | The service principal's app ID              |
| CLIENT_SECRET | The service principal's password            |
| TENANT_ID     | The tenant the service principal belongs to |

## Usage

All steps to build and register an image can be run with

```
bureaubuild all
```

Individual steps can also be run, most likely with the `--date-string` flag.
This may be useful for debugging, completing a partial deployment, or removing resources.

The steps are

| step        | description                                                                                                                                         |
| ----------- | -----------------------------------------------------------------------                                                                             |
| provision   | Provision Azure resources for the build (Pulumi)                                                                                                    |
| build       | Build bureau (Ansible)                                                                                                                              |
| generalise  | [Generalise](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/imaging#generalized-and-specialized) bureau images (Fabric + Azure SDK) |
| register    | Register bureau image versions in the gallery (Azure SDK)                                                                                           |
| destroy     | Destroy Azure resources for the build (but not the gallery!) (Pulumi)                                                                               |
| remove      | Remove the Pulumi stack used for the build (Pulumi)                                                                                                 |

The Pulumi stack name is a concatination of `--stack-prefix` (default: dev) and the date string.
**Note:** It is assumed that the name of the gallery project stack to deploy the images to is identical to the stack prefix.
