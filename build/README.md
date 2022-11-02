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
