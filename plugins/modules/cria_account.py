import boto3
import json


def criar_conta(email, projeto):
    client = boto3.client('organizations')

    try:
        # Cria a conta
        response = client.create_account(
            Email=email,
            AccountName=projeto,
            IamUserAccessToBilling='ALLOW'  # ou 'DENY' dependendo da política da sua org
        )

        # O create_account é assíncrono -> retorna um "CreateAccountStatusId"
        request_id = response['CreateAccountStatus']['Id']
        print(f"📨 Pedido de criação enviado. RequestId: {request_id}")

        # Acompanhar até a conta ser criada
        waiter = client.get_waiter('account_created')
        print("⏳ Aguardando a criação da conta...")
        waiter.wait(
            CreateAccountRequestId=request_id,
            WaiterConfig={'Delay': 20, 'MaxAttempts': 30}
        )

        # Buscar status final
        status = client.describe_create_account_status(
            CreateAccountRequestId=request_id
        )['CreateAccountStatus']

        return json.dumps(status, indent=4, default=str)

    except Exception as e:
        return f"❌ Erro ao criar conta: {str(e)}"


if __name__ == "__main__":
    print(listar_organizational_units())
