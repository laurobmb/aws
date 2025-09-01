#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import boto3
import json


def get_root_id():
    client = boto3.client('organizations')
    roots = client.list_roots()
    root_id = roots['Roots'][0]['Id']
    return root_id


def move_account(account_id, destination_ou_id):
    client = boto3.client('organizations')
    try:
        response = client.move_account(
            AccountId=account_id,
            SourceParentId=get_root_id(),
            DestinationParentId=destination_ou_id
        )
        return dict(
            changed=True,
            msg=f"Conta {account_id} movida para OU {destination_ou_id}",
            response=response
        )
    except Exception as e:
        return dict(
            failed=True,
            msg=f"Erro ao mover conta: {str(e)}"
        )


def create_account(email, projeto):
    client = boto3.client('organizations')
    try:
        response = client.create_account(
            Email=email,
            AccountName=projeto,
            IamUserAccessToBilling='ALLOW'
        )
        request_id = response['CreateAccountStatus']['Id']

        waiter = client.get_waiter('account_created')
        waiter.wait(
            CreateAccountRequestId=request_id,
            WaiterConfig={'Delay': 20, 'MaxAttempts': 30}
        )

        status = client.describe_create_account_status(
            CreateAccountRequestId=request_id
        )['CreateAccountStatus']

        return dict(
            changed=True,
            msg="Conta criada com sucesso",
            status=status
        )
    except Exception as e:
        return dict(
            failed=True,
            msg=f"Erro ao criar conta: {str(e)}"
        )


def run_module():
    module_args = dict(
        action=dict(type='str', required=True, choices=['create_account', 'move_account']),
        email=dict(type='str', required=False),
        projeto=dict(type='str', required=False),
        account_id=dict(type='str', required=False),
        destination_ou_id=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        msg='',
        status={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    action = module.params['action']

    if action == 'create_account':
        if not module.params['email'] or not module.params['projeto']:
            module.fail_json(msg="Parâmetros 'email' e 'projeto' são obrigatórios para create_account")
        result = create_account(module.params['email'], module.params['projeto'])

    elif action == 'move_account':
        if not module.params['account_id'] or not module.params['destination_ou_id']:
            module.fail_json(msg="Parâmetros 'account_id' e 'destination_ou_id' são obrigatórios para move_account")
        result = move_account(module.params['account_id'], module.params['destination_ou_id'])

    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def main():
    run_module()

# Documentação do módulo
DOCUMENTATION = r'''
---
module: aws_organizations_account
short_description: Cria ou move contas AWS dentro de uma Organization
version_added: "1.0"
description:
  - "Módulo para criar contas AWS em uma Organization e mover contas existentes para Organizational Units (OUs)."
options:
    action:
        description:
          - Ação a ser executada: criar ou mover uma conta.
        required: true
        type: str
        choices: ['create_account', 'move_account']
    email:
        description:
          - Email da conta a ser criada. Obrigatório para create_account.
        required: false
        type: str
    projeto:
        description:
          - Nome do projeto / nome da conta a ser criada. Obrigatório para create_account.
        required: false
        type: str
    account_id:
        description:
          - ID da conta a ser movida. Obrigatório para move_account.
        required: false
        type: str
    destination_ou_id:
        description:
          - ID da OU de destino. Obrigatório para move_account.
        required: false
        type: str
author:
    - Lauro Gomes (@laurobmb)
'''

EXAMPLES = r'''
# Criar nova conta
- name: Criar nova conta AWS
  aws_organizations_account:
    action: create_account
    email: "nova.conta@example.com"
    projeto: "ProjetoDemo"

# Mover conta para uma OU específica
- name: Mover conta para OU
  aws_organizations_account:
    action: move_account
    account_id: "123456789012"
    destination_ou_id: "ou-xxxx-yyyy"
'''

RETURN = r'''
msg:
    description: Mensagem resumida da ação executada
    type: str
    returned: always
changed:
    description: Indica se houve alteração no ambiente
    type: bool
    returned: always
status:
    description: Status detalhado da criação da conta (apenas para create_account)
    type: dict
    returned: when action is create_account
response:
    description: Resposta da API AWS (apenas para move_account)
    type: dict
    returned: when action is move_account
'''

if __name__ == '__main__':
    main()
