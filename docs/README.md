# Ansible Module: aws_manage_account

[](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml)
[](https://galaxy.ansible.com/laurobmb/aws)

An Ansible module to declaratively manage **AWS accounts** within an **AWS Organization**. This module allows you to create new accounts and move existing accounts between **Organizational Units (OUs)** safely and idempotently.

-----

## Overview

This module is designed to automate two critical operations in AWS Organizations:

  - **Account Creation**: Creates a new AWS account asynchronously, waiting for its completion before proceeding. The module polls the creation status until it succeeds or fails. It also supports applying resource tags and specifying a custom IAM role name upon creation.
  - **Account Moving**: Moves an existing account from its current location (Root or another OU) to a destination OU. The logic is idempotent: if the account is already at the destination, no action is taken.

It is ideal for environments that require account provisioning and organization at scale, integrated into CI/CD pipelines and automation playbooks.

-----

## Requirements

  - Python \>= 3.7
  - Ansible Core \>= 2.12
  - Boto3 \>= 1.26
  - AWS credentials configured (via `~/.aws/credentials`, environment variables, or IAM roles).

**Minimum Required IAM Permissions:**

The entity (user or role) executing the playbook needs the following permissions in the Organization's management account:

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

> **Note**: The `organizations:TagResource` permission is required to use the `account_tags` parameter.

-----

## Installation

The recommended way to use this module is as part of an **Ansible Collection**. Save the module's code in the following directory path relative to your project:

```text
ansible_collections/
└── laurobmb/
    └── aws/
        └── plugins/
            └── modules/
                └── aws_organizations_account.py
```

With this structure, Ansible will automatically find the module when you call it by its Fully Qualified Collection Name (FQCN): `laurobmb.aws.aws_organizations_account`.

-----

## Module Parameters

| Parameter           | Type   | Required    | Description                                                                                             |
| ------------------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------- |
| `action`            | `str`  | **Yes** | The action to perform: `create_account` or `move_account`.                                              |
| `email`             | `str`  | Conditional | Email for the new account. **Required for `action: create_account`**.                                     |
| `projeto`           | `str`  | Conditional | The project name or account name to be created. **Required for `action: create_account`**.              |
| `role_name`         | `str`  | No          | The name of the IAM role to be created by default in the new account (e.g., 'OrganizationAccountAccessRole'). |
| `account_tags`      | `list` | No          | A list of tags to apply to the new account. Each item should be a dictionary with `Key` and `Value`.      |
| `account_id`        | `str`  | Conditional | ID of the AWS account to be moved (e.g., `123456789012`). **Required for `action: move_account`**.       |
| `destination_ou_id` | `str`  | Conditional | ID of the destination Organizational Unit (e.g., `ou-xxxx-yyyyyyyy`). **Required for `action: move_account`**. |

-----

## Playbook Examples

### Scenario 1: Create a new AWS account

This playbook creates a new account and waits until the process is complete.

```yaml
---
- name: Create a New Account in AWS Organization
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    new_account_email: "new.project.gamma@example.com"
    new_account_name: "ProjectGamma"

  tasks:
    - name: "CREATE: New account for {{ new_account_name }}"
      laurobmb.aws.aws_organizations_account:
        action: create_account
        email: "{{ new_account_email }}"
        projeto: "{{ new_account_name }}"
      register: creation_result

    - name: "DEBUG: Display the account creation status"
      ansible.builtin.debug:
        var: creation_result.status
      when: creation_result.changed
```

### Scenario 2: Create a new account with a custom role and tags

This example demonstrates creating an account with all the advanced options.

```yaml
---
- name: Create a New Tagged Account in AWS Organization
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    account_email: "new.project.delta@example.com"
    account_name: "ProjectDelta"
    custom_role: "CustomOrgAccessRole"
    account_tags_list:
      - Key: Environment
        Value: "production"
      - Key: Project
        Value: "{{ account_name }}"

  tasks:
    - name: "CREATE: New tagged account for {{ account_name }}"
      laurobmb.aws.aws_organizations_account:
        action: create_account
        email: "{{ account_email }}"
        projeto: "{{ account_name }}"
        role_name: "{{ custom_role }}"
        account_tags: "{{ account_tags_list }}"
      register: creation_result
```

### Scenario 3: Move an existing account to an OU

This playbook moves an account to the "Projects" OU. If the account is already there, no changes will be made.

```yaml
---
- name: Organize an AWS Account into an OU
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    target_account_id: "123456789012"
    projects_ou_id: "ou-xxxx-yyyyyyyy"

  tasks:
    - name: "MOVE: Account {{ target_account_id }} to the Projects OU"
      laurobmb.aws.aws_organizations_account:
        action: move_account
        account_id: "{{ target_account_id }}"
        destination_ou_id: "{{ projects_ou_id }}"
      register: move_result

    - name: "DEBUG: Display the move result"
      ansible.builtin.debug:
        var: move_result
```

-----

## Return Values

The module returns a standard JSON dictionary.

| Key        | Type   | Description                                                           | Returned                          |
| ---------- | ------ | --------------------------------------------------------------------- | --------------------------------- |
| `changed`  | `bool` | `true` if a change was made, `false` otherwise.                       | Always                            |
| `msg`      | `str`  | A summary message describing the result of the operation.             | Always                            |
| `status`   | `dict` | Dictionary with the `describe_create_account_status` API response.    | Only for `action: create_account` |
| `response` | `dict` | Dictionary with the `move_account` API response.                      | Only for `action: move_account`   |

#### Return Example (Account Creation)

```json
{
    "changed": true,
    "msg": "Account 987654321098 successfully created for project ProjectGamma.",
    "status": {
        "AccountId": "987654321098",
        "AccountName": "ProjectGamma",
        "Id": "car-example12345",
        "State": "SUCCEEDED",
        "RequestedTimestamp": "2025-09-01T18:30:00.123Z",
        "CompletedTimestamp": "2025-09-01T18:32:15.456Z"
    }
}
```

#### Return Example (Successful Account Move)

```json
{
    "changed": true,
    "msg": "Account 123456789012 moved from r-abcd to ou-xxxx-yyyyyyyy.",
    "response": {
        "ResponseMetadata": {
            "RequestId": "a1b2c3d4-example",
            "HTTPStatusCode": 200
        }
    }
}
```

#### Return Example (Account already at destination)

```json
{
    "changed": false,
    "msg": "Account 123456789012 is already in the destination OU ou-xxxx-yyyyyyyy."
}
```

-----

## How It Works

1.  **Account Creation (`create_account`)**

      - Invokes the `create_account` function of the AWS API, which starts the process asynchronously.
      - The module enters a polling loop, calling `describe_create_account_status` every 15 seconds to check the creation status.
      - Control is returned to the playbook only when the creation status is `SUCCEEDED` or `FAILED`, ensuring that subsequent tasks can reliably use the ID of the newly created account.

2.  **Account Moving (`move_account`)**

      - First, it uses `list_parents` to discover the account's current location (its `SourceParentId`).
      - It compares the source with the destination. If they are the same, the module returns `changed: false`.
      - If they are different, it invokes `move_account` with the discovered source and the provided destination. This approach ensures that the move is idempotent and works regardless of where the account is in the organization's hierarchy.

-----

## Author

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

-----

## License

GPL-3.0-or-later