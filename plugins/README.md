# Python Module: AWS Organizations Logic

This Python script contains functions to interact with the AWS Organizations API. It is designed primarily for use as a custom Ansible module, but its core logic is self-contained and can be used in other Python-based automation contexts.

The script automates the creation and movement of AWS accounts, handling asynchronous operations and ensuring that actions are executed robustly.

-----

## Key Features

  - **Account Creation**: Initiates the creation process for a new AWS account and uses a polling system to await its completion, with optional support for custom IAM role names and resource tags.
  - **Account Moving**: Moves an existing account from its current location (either the organization's Root or another OU) to a destination Organizational Unit (OU).

-----

## Requirements

  - **Python 3.7+**
  - **Boto3**: The official AWS SDK for Python.

To install the necessary dependency, run:

```bash
pip install boto3
```

-----

## AWS Credential Setup

The script uses Boto3, which will automatically search for AWS credentials in the following order:

1.  Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).
2.  The shared credentials file (`~/.aws/credentials`).
3.  IAM roles (when running in an AWS environment like EC2, Lambda, etc.).

-----

## Main Functions

The script exposes the following functions for API interaction:

### `create_account(client, email, projeto, role_name=None, tags=None)`

Creates a new account in the AWS Organization and waits for its completion.

  - **Parameters:**

      - `client` (`boto3.client`): A pre-configured instance of the `boto3.client('organizations')`.
      - `email` (`str`): The email address for the new account. Must be unique.
      - `projeto` (`str`): The name to be assigned to the new account.
      - `role_name` (`str`, optional): The name of the IAM role to create in the new account. Defaults to the AWS standard if not provided.
      - `tags` (`list`, optional): A list of dictionaries for tagging the account. Format: `[{'Key': 'TagName', 'Value': 'TagValue'}]`.

  - **Return:**

      - A Python `dict` containing the final status of the operation. On success, the dictionary includes a `status` key with details of the created account. On failure, it includes `failed: True` and a `msg` with the reason for the error.

    *Example of a successful return:*

    ```python
    {
        'changed': True,
        'msg': 'Account 123456789012 successfully created...',
        'status': {
            'AccountId': '123456789012',
            'AccountName': 'ProjectDemo',
            'State': 'SUCCEEDED',
            # ... other fields
        }
    }
    ```

### `move_account(client, account_id, destination_ou_id)`

Moves an existing AWS account to a new Organizational Unit.

  - **Parameters:**

      - `client` (`boto3.client`): An instance of the `boto3.client('organizations')`.
      - `account_id` (`str`): The 12-digit ID of the account to be moved.
      - `destination_ou_id` (`str`): The ID of the destination OU (e.g., `ou-xxxx-yyyyyyyy`).

  - **Return:**

      - A Python `dict` with the result. The `changed` key will be `True` if the account was moved or `False` if it was already at the destination. On success, the `response` key contains the AWS API response.

    *Example of a successful return:*

    ```python
    {
        'changed': True,
        'msg': 'Account 123456789012 moved from r-abcd to ou-xxxx-yyyyyyyy.',
        'response': {
            'ResponseMetadata': {
                'RequestId': 'a1b2c3d4-example',
                'HTTPStatusCode': 200
            }
        }
    }
    ```

-----

## Standalone Usage Example

To test the functions directly with Python, you can add an execution block at the end of the script:

```python
# At the end of the aws_organizations_account.py file

if __name__ == '__main__':
    # AWS credentials must be configured in the environment
    try:
        org_client = boto3.client('organizations')

        # --- Test Account Creation ---
        print("--- Starting account creation test ---")
        test_email = "your-email+test-standalone@example.com"
        test_project = "ProjectStandalone"
        test_role = "CustomStandaloneRole"
        test_tags = [{'Key': 'ManagedBy', 'Value': 'PythonScript'}]
        
        creation_result = create_account(
            org_client,
            test_email,
            test_project,
            role_name=test_role,
            tags=test_tags
        )
        
        print("Creation Result:")
        import json
        print(json.dumps(creation_result, indent=4, default=str))

        # --- Test Account Move ---
        if not creation_result.get('failed'):
            created_account_id = creation_result['status']['AccountId']
            dest_ou_id = "ou-xxxx-yyyyyyyy" # REPLACE WITH YOUR OU ID
            
            print(f"\n--- Starting move test for account {created_account_id} ---")
            move_result = move_account(org_client, created_account_id, dest_ou_id)
            
            print("Move Result:")
            print(json.dumps(move_result, indent=4, default=str))

    except Exception as e:
        print(f"An error occurred: {e}")
```

-----

## Required IAM Permissions

The IAM entity executing this script needs the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "organizations:CreateAccount",
                "organizations:DescribeCreateAccountStatus",
                "organizations:MoveAccount",
                "organizations:ListParents",
                "organizations:TagResource"
            ],
            "Resource": "*"
        }
    ]
}
```

-----

## Author

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

## License

GPL-3.0-or-later