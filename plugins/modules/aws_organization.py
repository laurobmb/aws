import boto3
import json

def listar_organizational_units():
    client = boto3.client('organizations')

    # Passo 1: pegar o Root ID
    roots = client.list_roots()
    root_id = roots['Roots'][0]['Id']  # geralmente só tem 1 root
    print(f"Root ID encontrado: {root_id}")

    # Passo 2: listar OUs desse Root
    paginator = client.get_paginator('list_organizational_units_for_parent')
    ous = []
    for page in paginator.paginate(ParentId=root_id):
        ous.extend(page['OrganizationalUnits'])

    saida = {"OrganizationalUnits": ous}
    print(json.dumps(saida, indent=4, default=str))


if __name__ == "__main__":
    listar_organizational_units()
