# aws_organizations_account

[![Build Status](https://github.com/username/aws_organizations_account/actions/workflows/ci.yml/badge.svg)](https://github.com/username/aws_organizations_account/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/username/aws_organizations_account/badge.svg?branch=main)](https://coveralls.io/github/username/aws_organizations_account?branch=main)
[![Ansible Galaxy](https://img.shields.io/badge/Ansible%20Galaxy-aws__organizations__account-blue.svg)](https://galaxy.ansible.com/username/aws_organizations_account)

Módulo Ansible customizado para gerenciar **contas AWS** dentro de uma Organization. Permite criar novas contas e mover contas existentes para **Organizational Units (OUs)**.

---

## Visão Geral

O módulo automatiza operações críticas em **AWS Organizations**, incluindo:

- Criação de contas AWS com email e nome do projeto obrigatórios.
- Movimentação de contas entre Root e OUs específicas.
- Retorno estruturado compatível com playbooks e pipelines CI/CD.

Útil para ambientes corporativos que gerenciam múltiplas contas AWS de forma centralizada.

---

## Requisitos

- Python 3.7+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) >= 1.26
- Credenciais AWS configuradas via `~/.aws/credentials` ou variáveis de ambiente:

```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
````

* Permissões AWS necessárias:

  * `organizations:CreateAccount`
  * `organizations:MoveAccount`
  * `organizations:ListRoots`
  * `organizations:DescribeCreateAccountStatus`

---

## Estrutura de Pastas Recomendada

```text
aws_organizations_account/
├── library/
│   └── aws_organizations_account.py   # módulo principal
├── tests/
│   ├── test_create_account.yml
│   └── test_move_account.yml
├── meta/
│   └── main.yml
├── README.md
├── requirements.txt
└── .github/
    └── workflows/ci.yml               # CI/CD GitHub Actions
```

---

## Argumentos do Módulo

| Parâmetro           | Tipo | Obrigatório | Descrição                                                   |
| ------------------- | ---- | ----------- | ----------------------------------------------------------- |
| `action`            | str  | sim         | Ação a ser executada: `create_account` ou `move_account`.   |
| `email`             | str  | Condicional | Email da conta nova (necessário para `create_account`).     |
| `projeto`           | str  | Condicional | Nome do projeto / conta (necessário para `create_account`). |
| `account_id`        | str  | Condicional | ID da conta a ser movida (necessário para `move_account`).  |
| `destination_ou_id` | str  | Condicional | ID da OU de destino (necessário para `move_account`).       |

---

## Exemplos de Uso

### Criar uma nova conta AWS

```yaml
- name: Criar conta AWS no Root
  aws_organizations_account:
    action: create_account
    email: "nova.conta@example.com"
    projeto: "ProjetoDemo"
```

### Mover conta existente para uma OU

```yaml
- name: Mover conta para OU específica
  aws_organizations_account:
    action: move_account
    account_id: "123456789012"
    destination_ou_id: "ou-xxxx-yyyy"
```

---

## Retorno

O módulo retorna um dicionário JSON com os seguintes campos:

| Campo      | Tipo | Descrição                                                        |
| ---------- | ---- | ---------------------------------------------------------------- |
| `changed`  | bool | Indica se houve alteração no ambiente.                           |
| `msg`      | str  | Mensagem resumida da operação realizada.                         |
| `status`   | dict | Status detalhado da criação da conta (somente `create_account`). |
| `response` | dict | Resposta detalhada da API AWS (somente `move_account`).          |

#### Exemplo: Criação de conta

```json
{
    "changed": true,
    "msg": "Conta criada com sucesso",
    "status": {
        "Id": "car-xxxxxxxx",
        "AccountName": "ProjetoDemo",
        "State": "SUCCEEDED",
        "RequestedTimestamp": "2025-09-01T12:53:59.574000-03:00",
        "CompletedTimestamp": "2025-09-01T12:55:30.123000-03:00"
    }
}
```

#### Exemplo: Movimentação de conta

```json
{
    "changed": true,
    "msg": "Conta 123456789012 movida para OU ou-xxxx-yyyy",
    "response": {}
}
```

---

## Fluxo Interno

1. **Criação de conta (`create_account`)**

   * Chama `create_account()` da boto3.
   * Aguarda conclusão usando `account_created waiter`.
   * Retorna status detalhado da criação.

2. **Movimentação de conta (`move_account`)**

   * Obtém Root ID via `list_roots()`.
   * Executa `move_account()` da boto3 com `SourceParentId=root_id` e `DestinationParentId=ou_id`.
   * Retorna resposta da API AWS.

---

## Boas Práticas

* Use credenciais com **permissões mínimas necessárias**.
* Teste primeiramente em **sandbox** antes de aplicar em produção.
* A criação de contas pode levar **vários minutos**. Ajuste `WaiterConfig` se necessário.
* Monitore limites de conta na AWS, especialmente se criar múltiplas contas programaticamente.

---

## Versionamento Semântico

* **MAJOR** – alterações incompatíveis com versões anteriores.
* **MINOR** – adição de funcionalidades compatíveis.
* **PATCH** – correções de bugs e melhorias pequenas.

Exemplo: `v1.2.0` → versão 1, segundo release de funcionalidades, patch 0.

---

## Autor

* Lauro Gomes (@laurobmb)

---

## Licença

MIT License

