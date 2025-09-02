# Módulo Ansible: aws_organizations_account

[![CI/CD Pipeline](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml/badge.svg)](https://github.com/laurobmb/ansible-collection-aws/actions/workflows/ci.yml)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-laurobmb.aws-blue.svg)](https://galaxy.ansible.com/laurobmb/aws)

Um módulo Ansible para gerenciar de forma declarativa **contas AWS** dentro de uma **AWS Organization**. Este módulo permite criar novas contas e mover contas existentes entre **Organizational Units (OUs)** de forma segura e idempotente.

---

## Visão Geral

Este módulo foi projetado para automatizar duas operações críticas em AWS Organizations:

- **Criação de Contas**: Cria uma nova conta AWS de forma assíncrona, aguardando a sua conclusão antes de prosseguir. O módulo faz o *polling* do status da criação até que ela seja bem-sucedida ou falhe.
- **Movimentação de Contas**: Move uma conta existente de sua localização atual (Root ou outra OU) para uma OU de destino. A lógica é idempotente: se a conta já estiver no destino, nenhuma ação é executada.

Ele é ideal para ambientes que necessitam de provisionamento e organização de contas em escala, integrado a pipelines de CI/CD e playbooks de automação.

---

## Requisitos

- Python >= 3.7
- Ansible Core >= 2.12
- Boto3 >= 1.26
- Credenciais AWS configuradas (via `~/.aws/credentials`, variáveis de ambiente ou roles IAM).

**Permissões IAM Mínimas Necessárias:**

A entidade (usuário ou role) que executa o playbook precisa das seguintes permissões na conta de gerenciamento da Organization:

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
                "organizations:ListParents"
            ],
            "Resource": "*"
        }
    ]
}
````

-----

## Instalação

A forma recomendada de usar este módulo é através de uma **Ansible Collection**. Salve o código do módulo no seguinte caminho de diretório relativo ao seu projeto:

```text
ansible_collections/
└── laurobmb/
    └── aws/
        └── plugins/
            └── modules/
                └── aws_organizations_account.py
```

Com essa estrutura, o Ansible encontrará o módulo automaticamente ao chamá-lo por seu nome completo: `laurobmb.aws.aws_organizations_account`.

-----

## Parâmetros do Módulo

| Parâmetro | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `action` | `str` | **Sim** | Ação a ser executada: `create_account` ou `move_account`. |
| `email` | `str` | Condicional | Email para a nova conta. **Obrigatório para `action: create_account`**. |
| `projeto` | `str` | Condicional | Nome do projeto ou nome da conta a ser criada. **Obrigatório para `action: create_account`**. |
| `account_id` | `str` | Condicional | ID da conta AWS a ser movida (ex: `123456789012`). **Obrigatório para `action: move_account`**. |
| `destination_ou_id` | `str` | Condicional | ID da Organizational Unit de destino (ex: `ou-xxxx-yyyyyyyy`). **Obrigatório para `action: move_account`**. |

-----

## Exemplos de Playbooks

### Cenário 1: Criar uma nova conta AWS

Este playbook cria uma nova conta e aguarda até que o processo seja concluído.

```yaml
---
- name: Criar uma Nova Conta na AWS Organization
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    nova_conta_email: "novo.projeto.gamma@example.com"
    nova_conta_nome: "ProjetoGamma"

  tasks:
    - name: "CRIAR: Nova conta para o {{ nova_conta_nome }}"
      laurobmb.aws.aws_organizations_account:
        action: create_account
        email: "{{ nova_conta_email }}"
        projeto: "{{ nova_conta_nome }}"
      register: resultado_criacao

    - name: "DEBUG: Exibir o status da criação da conta"
      ansible.builtin.debug:
        var: resultado_criacao.status
      when: resultado_criacao.changed
```

### Cenário 2: Mover uma conta existente para uma OU

Este playbook move uma conta para a OU de "Projetos". Se a conta já estiver lá, nenhuma alteração será feita.

```yaml
---
- name: Organizar Conta AWS em uma OU
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    id_conta_alvo: "123456789012"
    ou_projetos_id: "ou-xxxx-yyyyyyyy"

  tasks:
    - name: "MOVER: Conta {{ id_conta_alvo }} para a OU de Projetos"
      laurobmb.aws.aws_organizations_account:
        action: move_account
        account_id: "{{ id_conta_alvo }}"
        destination_ou_id: "{{ ou_projetos_id }}"
      register: resultado_movimentacao

    - name: "DEBUG: Exibir resultado da movimentação"
      ansible.builtin.debug:
        var: resultado_movimentacao
```

-----

## Valores de Retorno

O módulo retorna um dicionário JSON com uma estrutura padronizada.

| Chave | Tipo | Descrição | Retornado |
| --- | --- | --- | --- |
| `changed` | `bool` | `true` se uma alteração foi feita, `false` caso contrário. | Sempre |
| `msg` | `str` | Mensagem resumida descrevendo o resultado da operação. | Sempre |
| `status` | `dict` | Dicionário com a resposta da API `describe_create_account_status`. | Apenas para `action: create_account` |
| `response` | `dict` | Dicionário com a resposta da API `move_account`. | Apenas para `action: move_account` |

#### Exemplo de Retorno (Criação de Conta)

```json
{
    "changed": true,
    "msg": "Conta 987654321098 criada com sucesso para o projeto ProjetoGamma.",
    "status": {
        "AccountId": "987654321098",
        "AccountName": "ProjetoGamma",
        "Id": "car-example12345",
        "State": "SUCCEEDED",
        "RequestedTimestamp": "2025-09-01T18:30:00.123Z",
        "CompletedTimestamp": "2025-09-01T18:32:15.456Z"
    }
}
```

#### Exemplo de Retorno (Movimentação de Conta bem-sucedida)

```json
{
    "changed": true,
    "msg": "Conta 123456789012 movida de r-abcd para ou-xxxx-yyyyyyyy.",
    "response": {
        "ResponseMetadata": {
            "RequestId": "a1b2c3d4-example",
            "HTTPStatusCode": 200
        }
    }
}
```

#### Exemplo de Retorno (Conta já no destino)

```json
{
    "changed": false,
    "msg": "Conta 123456789012 já está na OU de destino ou-xxxx-yyyyyyyy."
}
```

-----

## Como Funciona

1.  **Criação de Conta (`create_account`)**

      - Invoca a função `create_account` da API da AWS, que inicia o processo de forma assíncrona.
      - O módulo entra em um loop de *polling*, chamando `describe_create_account_status` a cada 15 segundos para verificar o status da criação.
      - O controle só é retornado ao playbook quando o status da criação é `SUCCEEDED` ou `FAILED`, garantindo que tarefas subsequentes possam usar o ID da conta recém-criada.

2.  **Movimentação de Conta (`move_account`)**

      - Primeiro, utiliza `list_parents` para descobrir a localização atual da conta (seu `SourceParentId`).
      - Compara a origem com o destino. Se forem iguais, o módulo retorna `changed: false`.
      - Se forem diferentes, ele invoca `move_account` com a origem descoberta e o destino fornecido. Esta abordagem garante que a movimentação seja idempotente e funcione independentemente de onde a conta esteja na hierarquia da organização.

-----

## Autor

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

-----

## Licença

MIT
