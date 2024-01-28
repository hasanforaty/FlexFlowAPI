# FlexFlow API

FlexFlow API is a RESTful application that allows you to create and manage workflows for your company. With this API, you can define the steps of your workflow and connect them to create a seamless process for handling messages and approvals.

## Features

- Create and manage workflows.
- Add nodes (steps) to your workflows.
- Connect nodes to define the flow of the workflow.
- Submit messages through the workflow for approval.


## UML Diagram

![UML Diagram](diagrams/Classes.drawio.png)


## Getting Started

### Prerequisites

- Python 3.x
- Django
- Django REST framework
- Docker

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/hasanforaty/FlexFlowAPI.git
   cd flex_flow_api
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```
   The API should now be accessible at http://localhost:8000/.
## API Endpoints
# Users
- Login: POST /api/users/login/
- Retrieve User: GET /api/users/me/
- Update User: PUT /api/users/me/
- Partial Update User: PATCH /api/users/me/
- Register User: POST /api/users/register/
# Workflow
- List Workflows: GET /api/workflow/
- Create Workflow: POST /api/workflow/
- Retrieve Workflow: GET /api/workflow/{workflowId}/
- Update Workflow: PUT /api/workflow/{workflowId}/
- Partial Update Workflow: PATCH /api/workflow/{workflowId}/
- Delete Workflow: DELETE /api/workflow/{workflowId}/
# Node
- List Nodes in Workflow: GET /api/workflow/{workflowId}/nodes/
- Create Node in Workflow: POST /api/workflow/{workflowId}/nodes/
- Retrieve Node in Workflow: GET /api/workflow/{workflowId}/nodes/{nodeId}/
- Update Node in Workflow: PUT /api/workflow/{workflowId}/nodes/{nodeId}/
- Partial Update Node in Workflow: PATCH /api/workflow/{workflowId}/nodes/{nodeId}/
- Delete Node in Workflow: DELETE /api/workflow/{workflowId}/nodes/{nodeId}/
# Edge
- List Edges in Workflow: GET /api/workflow/{workflowId}/edges/
- Create Edge in Workflow: POST /api/workflow/{workflowId}/edges/
- Retrieve Edge in Workflow: GET /api/workflow/{workflowId}/edges/{edgeId}/
- Update Edge in Workflow: PUT /api/workflow/{workflowId}/edges/{edgeId}/
- Partial Update Edge in Workflow: PATCH /api/workflow/{workflowId}/edges/{edgeId}/
- Delete Edge in Workflow: DELETE /api/workflow/{workflowId}/edges/{edgeId}/
# Messages
- List Messages in Workflow: GET /api/workflow/{workflowId}/messages/
- Create Message in Workflow: POST /api/workflow/{workflowId}/messages/
- Retrieve Message in Workflow: GET /api/workflow/{workflowId}/messages/{messageId}/
- Retrieve Message History: GET /api/workflow/{workflowId}/messages/{messageId}/history/
- Change Message Status: POST /api/workflow/{workflowId}/messages/{messageId}/status/
# Schema
- Retrieve OpenAPI Schema: GET /api/schema/
# History
- List History: GET /api/history/

## Testing
To run tests for the API, use the following command:
```bash
  python manage.py test
```
## Contributing

Feel free to contribute to this project by opening issues or creating pull requests. Your contributions are highly appreciated.

## License

This project is licensed under the [MIT License](LICENSE).


