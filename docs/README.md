# Ansible Module: aws_organizations_account

[![CI/CD Pipeline](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml/badge.svg)](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-laurobmb.aws-blue.svg)](https://galaxy.ansible.com/laurobmb/aws)

An Ansible module to declaratively manage **AWS accounts** within an **AWS Organization**. This module allows you to create new accounts and move existing accounts between **Organizational Units (OUs)** securely and idempotently.

-----

## Overview

This module is designed to automate two critical operations in AWS Organizations:

  - **Account Creation**: Asynchronously creates a new AWS account, waiting for its completion before proceeding.
  - **Account Movement**: Moves an existing account from its current location (Root or another OU) to a target OU.

It is ideal for environments that require account provisioning and organization at scale, integrated with CI/CD pipelines and automation playbooks.

-----

## Requirements

  - Python >= 3.7
  - Ansible Core >= 2.12
  - Boto3 >= 1.26
  - AWS credentials configured (via `~/.aws/credentials`, environment variables, or IAM roles).

**Minimum Required IAM Permissions:**

The entity (user or role) executing the playbook needs the following permissions:

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
                "organizations:ListRoots"
            ],
            "Resource": "*"
        }
    ]
}
```

-----

## Installation and Configuration

The recommended way to use this module is through an **Ansible Collection**. Create the following directory structure:

```text
ansible_collections/
└── laurobmb/
    └── aws/
        ├── plugins/
        │   └── modules/
        │       └── aws_organizations_account.py  # Paste the module code here
        └── galaxy.yml
```

With this structure, Ansible will automatically find the module when you call it by its full name: `laurobmb.aws.aws_organizations_account`.

-----

## Module Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `action` | `str` | **Yes** | The action to be performed: `create_account` or `move_account`. |
| `email` | `str` | Conditional | Email for the new account (required for `create_account`). |
| `projeto` | `str` | Conditional | Project name / account name (required for `create_account`). |
| `account_id` | `str` | Conditional | ID of the AWS account to be moved (required for `move_account`). |
| `destination_ou_id` | `str` | Conditional | ID of the destination Organizational Unit (required for `move_account`). |

-----

## Playbook Examples

### Create a new account and move it

This playbook demonstrates a complete flow: first, it creates the account, and then it uses the returned ID to move it to a specific OU.

```yaml
---
- name: Manage AWS Accounts in the Organization
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    ou_projects_id: "ou-xxxx-yyyyyyyy"
    new_account_email: "project.alpha.account@example.com"
    new_account_name: "ProjectAlpha"

  tasks:
    - name: "CREATE: New account for {{ new_account_name }}"
      laurobmb.aws.aws_organizations_account:
        action: create_account
        email: "{{ new_account_email }}"
        projeto: "{{ new_account_name }}"
      register: creation_result

    - name: "DEBUG: Display creation result"
      ansible.builtin.debug:
        var: creation_result

    - name: "MOVE: Move account {{ creation_result.status.AccountId }} to the Projects OU"
      laurobmb.aws.aws_organizations_account:
        action: move_account
        account_id: "{{ creation_result.status.AccountId }}"
        destination_ou_id: "{{ ou_projects_id }}"
      when: creation_result.changed
```

-----

## Return Values

The module returns a JSON dictionary with a standardized structure.

| Key | Type | Description |
|---|---|---|
| `changed` | `bool` | `true` if a change was made, `false` otherwise. |
| `msg` | `str` | A summary message describing the result of the operation. |
| `status` | `dict` | Dictionary with the response from the `describe_create_account_status` API (only for `create_account`). |
| `response` | `dict` | Dictionary with the response from the `move_account` API (only for `move_account`). |

#### Example Return (Account Creation)

```json
{
    "changed": true,
    "msg": "Account 987654321098 created successfully for the ProjectAlpha project.",
    "status": {
        "AccountId": "987654321098",
        "AccountName": "ProjectAlpha",
        "Id": "car-example12345",
        "State": "SUCCEEDED",
        "RequestedTimestamp": "2025-09-01T18:30:00.123Z",
        "CompletedTimestamp": "2025-09-01T18:32:15.456Z"
    }
}
```

#### Example Return (Account Movement)

```json
{
    "changed": true,
    "msg": "Account 987654321098 moved from r-abcd to ou-xxxx-yyyyyyyy.",
    "response": {
        "ResponseMetadata": {
            "RequestId": "a1b2c3d4-example",
            "HTTPStatusCode": 200,
            "...": "..."
        }
    }
}
```

-----

## How It Works

1.  **Account Creation (`create_account`)**

      - Invokes the `create_account` function of the AWS API, which starts the process asynchronously.
      - Enters a polling loop, calling `describe_create_account_status` periodically to check the creation status.
      - The module waits until the status is `SUCCEEDED` or `FAILED` before returning the result.

2.  **Account Movement (`move_account`)**

      - First, it uses `list_parents` to discover the current location of the account (its `SourceParentId`).
      - Then, it invokes `move_account` with the discovered source and the provided destination.
      - This approach ensures that the movement works regardless of where the account is in the organization's hierarchy.

-----

## Author

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

-----

## License

MIT