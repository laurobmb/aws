import boto3
import json

def listar_contas():
    client = boto3.client('organizations')

    contas = []
    paginator = client.get_paginator('list_accounts')
    for page in paginator.paginate():
        contas.extend(page['Accounts'])

    # Monta a saída igual ao awscli
    saida = {"Accounts": contas}
    print(json.dumps(saida, indent=4, default=str))


if __name__ == "__main__":
    listar_contas()
