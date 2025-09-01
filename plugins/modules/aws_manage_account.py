#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import boto3
import time # CORREÇÃO: Importar o módulo time
from botocore.exceptions import ClientError


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
- name: Criar nova conta AWS
  aws_organizations_account:
    action: create_account
    email: "nova.conta+ansible@example.com"
    projeto: "ProjetoAnsible"

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


def get_current_parent_id(client, account_id):
    """Descobre o Parent ID (Root ou OU) atual de uma conta."""
    parents = client.list_parents(ChildId=account_id)
    return parents['Parents'][0]['Id']


def move_account(client, account_id, destination_ou_id):
    """Move uma conta para uma nova OU."""
    try:
        # CORREÇÃO: Descobrir o pai de origem dinamicamente
        source_parent_id = get_current_parent_id(client, account_id)
        
        # Não fazer nada se já estiver no destino
        if source_parent_id == destination_ou_id:
            return dict(
                changed=False,
                msg=f"Conta {account_id} já está na OU de destino {destination_ou_id}."
            )

        response = client.move_account(
            AccountId=account_id,
            SourceParentId=source_parent_id,
            DestinationParentId=destination_ou_id
        )
        return dict(
            changed=True,
            msg=f"Conta {account_id} movida de {source_parent_id} para {destination_ou_id}.",
            response=response
        )
    except ClientError as e:
        return dict(
            failed=True,
            msg=f"Erro ao mover conta: {e.response['Error']['Message']}"
        )


def create_account(client, email, projeto):
    """Cria uma nova conta na AWS Organization e aguarda sua conclusão."""
    try:
        response = client.create_account(
            Email=email,
            AccountName=projeto,
            IamUserAccessToBilling='ALLOW'
        )

        request_id = response['CreateAccountStatus']['Id']

        while True:
            status_response = client.describe_create_account_status(
                CreateAccountRequestId=request_id
            )
            status = status_response['CreateAccountStatus']
            state = status['State']

            if state == 'SUCCEEDED':
                # CORREÇÃO: Retornar um dicionário Python formatado para o Ansible
                return dict(
                    changed=True,
                    msg=f"Conta {status['AccountId']} criada com sucesso para o projeto {projeto}.",
                    status=status
                )

            if state == 'FAILED':
                # CORREÇÃO: Retornar um dicionário de falha
                return dict(
                    failed=True,
                    msg=f"Criação da conta falhou. Motivo: {status.get('FailureReason', 'Não especificado')}"
                )
            
            time.sleep(15) # Pausa antes da próxima verificação

    except ClientError as e:
        return dict(
            failed=True,
            msg=f"Erro de API da AWS ao criar conta: {e.response['Error']['Message']}"
        )


def run_module():
    module_args = dict(
        action=dict(type='str', required=True, choices=['create_account', 'move_account']),
        email=dict(type='str', required=False),
        projeto=dict(type='str', required=False),
        account_id=dict(type='str', required=False),
        destination_ou_id=dict(type='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False # Este módulo faz alterações reais, então check_mode não é suportado
    )

    action = module.params['action']
    result = {}

    # MELHORIA: Criar o cliente uma vez e passá-lo como parâmetro
    try:
        client = boto3.client('organizations')
    except Exception as e:
        module.fail_json(msg=f"Falha ao iniciar cliente boto3: {str(e)}")


    if action == 'create_account':
        if not module.params['email'] or not module.params['projeto']:
            module.fail_json(msg="Parâmetros 'email' e 'projeto' são obrigatórios para create_account.")
        result = create_account(client, module.params['email'], module.params['projeto'])

    elif action == 'move_account':
        if not module.params['account_id'] or not module.params['destination_ou_id']:
            module.fail_json(msg="Parâmetros 'account_id' e 'destination_ou_id' são obrigatórios para move_account.")
        result = move_account(client, module.params['account_id'], module.params['destination_ou_id'])

    # Lógica de saída final
    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()