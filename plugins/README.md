# Módulo Python: Lógica para AWS Organizations

Este script Python contém funções para interagir com a API do AWS Organizations. Ele foi projetado primariamente para ser usado como um módulo Ansible customizado, mas sua lógica principal é autocontida e pode ser utilizada em outros contextos de automação com Python.

O script automatiza a criação e a movimentação de contas AWS, tratando operações assíncronas e garantindo que as ações sejam executadas de forma robusta.

---

## Funcionalidades Principais

-   **Criação de Contas**: Inicia o processo de criação de uma nova conta AWS e utiliza um sistema de *polling* para aguardar sua conclusão.
-   **Movimentação de Contas**: Move uma conta existente de sua localização atual (seja o Root da organização ou outra OU) para uma Organizational Unit (OU) de destino.

---

## Requisitos

-   **Python 3.7+**
-   **Boto3**: A biblioteca oficial da AWS para Python.

Para instalar a dependência necessária, execute:
```bash
pip install boto3
````

-----

## Configuração de Credenciais AWS

O script utiliza o Boto3, que buscará por credenciais AWS automaticamente na seguinte ordem:

1.  Variáveis de ambiente (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).
2.  Arquivo de credenciais compartilhadas (`~/.aws/credentials`).
3.  Roles IAM (quando executado em um ambiente AWS, como EC2, Lambda, etc.).

-----

## Funções Principais

O script expõe as seguintes funções para interação com a API:

### `create_account(client, email, projeto)`

Cria uma nova conta na AWS Organization e aguarda sua conclusão.

  - **Parâmetros:**

      - `client` (`boto3.client`): Uma instância pré-configurada do cliente `boto3.client('organizations')`.
      - `email` (`str`): O endereço de e-mail para a nova conta. Deve ser único.
      - `projeto` (`str`): O nome que será atribuído à nova conta.

  - **Retorno:**

      - Um `dict` Python contendo o status final da operação. Em caso de sucesso, o dicionário inclui uma chave `status` com os detalhes da conta criada. Em caso de falha, inclui as chaves `failed: True` e `msg` com o motivo do erro.

    *Exemplo de retorno de sucesso:*

    ```python
    {
        'changed': True,
        'msg': 'Conta 123456789012 criada com sucesso...',
        'status': {
            'AccountId': '123456789012',
            'AccountName': 'ProjetoDemo',
            'State': 'SUCCEEDED',
            # ... outros campos
        }
    }
    ```

### `move_account(client, account_id, destination_ou_id)`

Move uma conta AWS existente para uma nova Organizational Unit.

  - **Parâmetros:**

      - `client` (`boto3.client`): Uma instância do cliente `boto3.client('organizations')`.
      - `account_id` (`str`): O ID da conta de 12 dígitos a ser movida.
      - `destination_ou_id` (`str`): O ID da OU de destino (ex: `ou-xxxx-yyyyyyyy`).

  - **Retorno:**

      - Um `dict` Python com o resultado. A chave `changed` será `True` se a conta foi movida ou `False` se já estava no destino. Em caso de sucesso, a chave `response` contém a resposta da API da AWS.

    *Exemplo de retorno de sucesso:*

    ```python
    {
        'changed': True,
        'msg': 'Conta 123456789012 movida de r-abcd para ou-xxxx-yyyyyyyy.',
        'response': {
            'ResponseMetadata': {
                'RequestId': 'a1b2c3d4-example',
                'HTTPStatusCode': 200
            }
        }
    }
    ```

-----

## Exemplo de Uso (Standalone)

Para testar as funções diretamente com Python, você pode adicionar um bloco de execução ao final do script:

```python
# No final do arquivo aws_organizations_account.py

if __name__ == '__main__':
    # É necessário ter as credenciais AWS configuradas no ambiente
    try:
        org_client = boto3.client('organizations')

        # --- Teste de Criação de Conta ---
        print("--- Iniciando teste de criação de conta ---")
        email_teste = "seu-email+teste-standalone@example.com"
        projeto_teste = "ProjetoStandalone"
        resultado_criacao = create_account(org_client, email_teste, projeto_teste)
        
        print("Resultado da Criação:")
        # O resultado já é um dicionário, não precisa de json.loads
        import json
        print(json.dumps(resultado_criacao, indent=4))

        # --- Teste de Movimentação de Conta ---
        if not resultado_criacao.get('failed'):
            account_id_criado = resultado_criacao['status']['AccountId']
            ou_destino_id = "ou-xxxx-yyyyyyyy" # SUBSTITUA PELO ID DA SUA OU
            
            print(f"\n--- Iniciando teste de movimentação da conta {account_id_criado} ---")
            resultado_mov = move_account(org_client, account_id_criado, ou_destino_id)
            
            print("Resultado da Movimentação:")
            print(json.dumps(resultado_mov, indent=4, default=str))

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

```

-----

## Permissões IAM Necessárias

A entidade IAM que executa este script precisa das seguintes permissões na AWS:

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

## Autor

  - Lauro Gomes ([@laurobmb](https://github.com/laurobmb))

## Licença

MIT
