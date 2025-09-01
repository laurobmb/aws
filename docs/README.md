# Módulo Ansible: aws_organizations_account

[![CI/CD Pipeline](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml/badge.svg)](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-laurobmb.aws-blue.svg)](https://galaxy.ansible.com/laurobmb/aws)

Um módulo Ansible para gerenciar de forma declarativa **contas AWS** dentro de uma **AWS Organization**. Este módulo permite criar novas contas e mover contas existentes entre **Organizational Units (OUs)** de forma segura e idempotente.

---

## Visão Geral

Este módulo foi projetado para automatizar duas operações críticas em AWS Organizations:

- **Criação de Contas**: Cria uma nova conta AWS de forma assíncrona, aguardando a sua conclusão antes de prosseguir.
- **Movimentação de Contas**: Move uma conta existente de sua localização atual (Root ou outra OU) para uma OU de destino.

Ele é ideal para ambientes que necessitam de provisionamento e organização de contas em escala, integrado a pipelines de CI/CD e playbooks de automação.

---

## Requisitos

- Python >= 3.7
- Ansible Core >= 2.12
- Boto3 >= 1.26
- Credenciais AWS configuradas (via `~/.aws/credentials`, variáveis de ambiente ou roles IAM).

**Permissões IAM Mínimas Necessárias:**

A entidade (usuário ou role) que executa o playbook precisa das seguintes permissões:

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
````

-----

## Instalação e Configuração

A forma recomendada de usar este módulo é através de uma **Ansible Collection**. Crie a seguinte estrutura de diretórios:

```text
ansible_collections/
└── laurobmb/
    └── aws/
        ├── plugins/
        │   └── modules/
        │       └── aws_organizations_account.py  # Cole o código do módulo aqui
        └── galaxy.yml
```

Com essa estrutura, o Ansible encontrará o módulo automaticamente ao chamá-lo por seu nome completo: `laurobmb.aws.aws_organizations_account`.

-----

## Parâmetros do Módulo

| Parâmetro           | Tipo | Obrigatório | Descrição                                                               |
| ------------------- | ---- | ----------- | ----------------------------------------------------------------------- |
| `action`            | `str`  | **Sim** | Ação a ser executada: `create_account` ou `move_account`.               |
| `email`             | `str`  | Condicional | Email para a nova conta (obrigatório para `create_account`).            |
| `projeto`           | `str`  | Condicional | Nome do projeto / nome da conta (obrigatório para `create_account`).    |
| `account_id`        | `str`  | Condicional | ID da conta AWS a ser movida (obrigatório para `move_account`).         |
| `destination_ou_id` | `str`  | Condicional | ID da Organizational Unit de destino (obrigatório para `move_account`). |

-----

## Exemplos de Playbooks

### Criar uma nova conta e movê-la

Este playbook demonstra um fluxo completo: primeiro cria a conta e, em seguida, usa o ID retornado para movê-la para uma OU específica.

```yaml
---
- name: Gerenciar Contas AWS na Organization
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    ou_projetos_id: "ou-xxxx-yyyyyyyy"
    nova_conta_email: "conta.projeto.alpha@example.com"
    nova_conta_nome: "ProjetoAlpha"

  tasks:
    - name: "CRIAR: Nova conta para o {{ nova_conta_nome }}"
      laurobmb.aws.aws_organizations_account:
        action: create_account
        email: "{{ nova_conta_email }}"
        projeto: "{{ nova_conta_nome }}"
      register: resultado_criacao

    - name: "DEBUG: Exibir resultado da criação"
      ansible.builtin.debug:
        var: resultado_criacao

    - name: "MOVER: Mover conta {{ resultado_criacao.status.AccountId }} para a OU de Projetos"
      laurobmb.aws.aws_organizations_account:
        action: move_account
        account_id: "{{ resultado_criacao.status.AccountId }}"
        destination_ou_id: "{{ ou_projetos_id }}"
      when: resultado_criacao.changed
```

-----

## Valores de Retorno

O módulo retorna um dicionário JSON com uma estrutura padronizada.

| Chave      | Tipo   | Descrição                                                               |
| ---------- | ------ | ----------------------------------------------------------------------- |
| `changed`  | `bool` | `true` se uma alteração foi feita, `false` caso contrário.              |
| `msg`      | `str`  | Mensagem resumida descrevendo o resultado da operação.                  |
| `status`   | `dict` | Dicionário com a resposta da API `describe_create_account_status` (apenas para `create_account`). |
| `response` | `dict` | Dicionário com a resposta da API `move_account` (apenas para `move_account`). |

#### Exemplo de Retorno (Criação de Conta)

```json
{
    "changed": true,
    "msg": "Conta 987654321098 criada com sucesso para o projeto ProjetoAlpha.",
    "status": {
        "AccountId": "987654321098",
        "AccountName": "ProjetoAlpha",
        "Id": "car-example12345",
        "State": "SUCCEEDED",
        "RequestedTimestamp": "2025-09-01T18:30:00.123Z",
        "CompletedTimestamp": "2025-09-01T18:32:15.456Z"
    }
}
```

#### Exemplo de Retorno (Movimentação de Conta)

```json
{
    "changed": true,
    "msg": "Conta 987654321098 movida de r-abcd para ou-xxxx-yyyyyyyy.",
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

## Como Funciona

1.  **Criação de Conta (`create_account`)**

      - Invoca a função `create_account` da API da AWS, que inicia o processo de forma assíncrona.
      - Entra em um loop de *polling*, chamando `describe_create_account_status` periodicamente para verificar o status da criação.
      - O módulo aguarda até que o status seja `SUCCEEDED` ou `FAILED` antes de retornar o resultado.

2.  **Movimentação de Conta (`move_account`)**

      - Primeiro, utiliza `list_parents` para descobrir a localização atual da conta (seu `SourceParentId`).
      - Em seguida, invoca `move_account` com a origem descoberta e o destino fornecido.
      - Esta abordagem garante que a movimentação funcione independentemente de onde a conta esteja na hierarquia da organização.

-----

## Autor

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

-----

## Licença

MIT

