# GenAI Gateway Resilience Service
This is a cookiecutter repository for a Gen AI Gateway Service. It serves 
as a gateway service for multiple OpenAI models. This service is designed to implement 
a resilient operation mechanism that implements a fallback mechanism between a primary and a fallback model. 
This repository is particularly suited for smaller architectures that 
use multiple LLMs models or architectures that don't have access to enterprise-grade balancing services or managed solutions. It
could also be used as a starting point for more complex gateway services implement other operational patterns 
that can be found [here](https://internal.playbook.microsoft.com/code-with-mlops/technology-guidance/generative-ai/dev-starters/genai-gateway/#5-key-considerations-while-building-genai-gateway).

## Features
* Fast API: Serves as a centralized entry point for accessing multiple OpenAI models.
* Fallback mechanism: Implements a circuit breaker pattern to switch between a primary and a fallback model when the primary model is unavailable.

## Getting Started

### Configuration
The OpenAI Gateway Service requires the following attributes 
to be configured in the `.env` file or with environment variables:

```bash
FALLBACK_OPENAI_HOST=""
FALLBACK_OPENAI_API_KEY=""
PRIMARY_OPENAI_HOST=""
PRIMARY_OPENAI_API_KEY=""
```
   
### Setting up your service
To get started with the OpenAI Gateway Service, follow these steps:

1) Clone the Repository and create a new project based on the template:
    ```bash
    git clone <repository_url>
    ```
   Create a new project based on the template:
    ```bash
    cookiecutter <cloned_directory>
    ```
2) Install the project dependencies with poetry:
    ```bash
    cd <project_name>
    poetry install
    ```
3) Create an `.env` file with the following environment variables:
    ```bash
    FALLBACK_OPENAI_HOST=""
    FALLBACK_OPENAI_API_KEY=""
    PRIMARY_OPENAI_HOST=""
    PRIMARY_OPENAI_API_KEY=""
    ```
4) Run the application locally:
    ```bash
    poetry run uvicorn src.app:app --reload
    ```
5) Build and run the application with docker-compose:
    ```bash
    docker build -t <image_name> .
    ```
   Run the docker image:
    ```bash
   docker run -p 8000:8000 <image_name>
    ```

## Usage
Once the service is up and running, you can send requests to the 
gateway endpoint to interact with the configured OpenAI models. Make sure 
to refer to the API documentation for details on the supported 
endpoints and request/response formats.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
