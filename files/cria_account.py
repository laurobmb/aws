import boto3
import json
import time # Importe o módulo time para fazer pausas

def criar_conta(email, projeto):
    """
    Cria uma nova conta na AWS Organization e aguarda sua conclusão.
    """
    client = boto3.client('organizations')

    try:
        # 1. Inicia a criação da conta
        response = client.create_account(
            Email=email,
            AccountName=projeto,
            IamUserAccessToBilling='ALLOW'
        )

        request_id = response['CreateAccountStatus']['Id']
        print(f"📨 Pedido de criação enviado. RequestId: {request_id}")

        # 2. Aguarda a criação da conta usando polling
        print("⏳ Aguardando a finalização do processo...")
        while True:
            status_response = client.describe_create_account_status(
                CreateAccountRequestId=request_id
            )
            status = status_response['CreateAccountStatus']
            state = status['State']

            print(f"   -> Status atual: {state}")

            if state == 'SUCCEEDED':
                print(f"✅ Conta {status['AccountId']} criada com sucesso!")
                # Retorna o status final completo
                return json.dumps(status, indent=4, default=str)

            if state == 'FAILED':
                raise Exception(f"❌ Criação da conta falhou. Motivo: {status.get('FailureReason', 'Não especificado')}")

            # Espera 20 segundos antes de verificar novamente
            time.sleep(20)

    except client.exceptions.ClientError as e:
        # Tratamento de erro mais específico para a API da AWS
        return f"❌ Erro de API da AWS: {e.response['Error']['Message']}"
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}"


if __name__ == "__main__":
    # Substitua com um e-mail e nome de projeto válidos
    resultado = criar_conta("seu-email-unico@provedor.com", "NomeDoProjeto")
    print("\n--- Resultado Final ---")
    print(resultado)