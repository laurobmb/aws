import boto3
import json

def get_root_id():
    client = boto3.client('organizations')
    roots = client.list_roots()
    root_id = roots['Roots'][0]['Id']
    return root_id

def mover_conta(account_id, destination_ou_id):
    client = boto3.client('organizations')
    roots = client.list_roots()
    root_id = roots['Roots'][0]['Id']

    try:
        response = client.move_account(
            AccountId=account_id,
            SourceParentId=get_root_id(),
            DestinationParentId=destination_ou_id
        )
        return f"✅ Conta {account_id} movida do Root {root_id} para OU {destination_ou_id}"

    except Exception as e:
        return f"❌ Erro ao mover conta: {str(e)}"


if __name__ == "__main__":
    mover_conta("559716407582", "ou-xxxx-aaaaaaaa")


