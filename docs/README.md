# aws_organizations_account

Módulo Ansible customizado para **criar contas AWS** dentro de uma Organization e **mover contas existentes para Organizational Units (OUs)**.

---

## Descrição

O módulo permite:  

1. Criar uma nova conta AWS dentro do **Root** da organização.  
2. Mover uma conta existente para uma **OU específica**.  

O módulo é compatível com o Ansible >= 2.9 e requer que o usuário tenha permissões adequadas na AWS Organizations.

---

## Requisitos

- Python 3.7+
- [boto3](https://boto3.amazonaws.com/) (`pip install boto3`)
- Credenciais AWS configuradas (`~/.aws/credentials` ou variáveis de ambiente)

---

## Opções do Módulo

| Opção             | Descrição                                                                                   | Tipo   | Obrigatório | Valores possíveis          |
|------------------|---------------------------------------------------------------------------------------------|-------|------------|---------------------------|
| `action`          | Ação a ser executada pelo módulo                                                            | str   | sim        | `create_account`, `move_account` |
| `email`           | Email da nova conta (necessário apenas para `create_account`)                               | str   | não        | —                         |
| `projeto`         | Nome do projeto / nome da conta (necessário apenas para `create_account`)                  | str   | não        | —                         |
| `account_id`      | ID da conta a ser movida (necessário apenas para `move_account`)                             | str   | não        | —                         |
| `destination_ou_id` | ID da OU de destino (necessário apenas para `move_account`)                                 | str   | não        | —                         |

---

## Exemplos de Uso

### Criar uma nova conta AWS

```yaml
- name: Criar nova conta AWS
  aws_organizations_account:
    action: create_account
    email: "nova.conta@example.com"
    projeto: "ProjetoDemo"
````

### Mover uma conta existente para uma OU específica

```yaml
- name: Mover conta para OU
  aws_organizations_account:
    action: move_account
    account_id: "123456789012"
    destination_ou_id: "ou-xxxx-yyyy"
```

---

## Retorno

O módulo retorna um dicionário contendo:

* `changed`: Indica se houve alteração no ambiente (bool).
* `msg`: Mensagem resumida sobre a ação executada (str).
* `status`: Status detalhado da criação da conta (apenas para `create_account`).
* `response`: Resposta da API AWS (apenas para `move_account`).

Exemplo de retorno ao criar uma conta:

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

Exemplo de retorno ao mover uma conta:

```json
{
    "changed": true,
    "msg": "Conta 123456789012 movida para OU ou-xxxx-yyyy",
    "response": {}
}
```

---

## Autor

* Lauro Gomes (@laurobmb)

---

## Observações

* A criação de contas AWS **leva alguns minutos** para ser concluída.
* Certifique-se de que o usuário AWS tenha permissões adequadas no **Organizations**.
* O módulo só suporta **Root** ou OUs existentes. Para criar novas OUs, use outro módulo ou o console AWS.

