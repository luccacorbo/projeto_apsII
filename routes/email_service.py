import os
import secrets
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis locais (Railway usa variáveis internas automaticamente)

class EmailService:
    def __init__(self):
        # API Key do SendGrid
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_from_email = os.getenv("EMAIL_FROM")
        self.base_url = os.getenv("BASE_URL", "http://localhost:5000")

        if not self.sendgrid_api_key or not self.sender_from_email:
            print("⚠️ ERRO: SENDGRID_API_KEY ou EMAIL_FROM não configurados no Railway.")

        # URL oficial da API SendGrid
        self.sendgrid_url = "https://api.sendgrid.com/v3/mail/send"

    # ================================================================
    # ENVIAR CONVITE PARA PROJETO
    # ================================================================
    def enviar_convite_projeto(self, email_convidado, nome_convidado, nome_projeto, nome_convidante, token_convite):

        url_aceitacao = f"{self.base_url}/convite/aceitar/{token_convite}"

        assunto = f"🎉 Convite para o projeto: {nome_projeto}"

        mensagem_html = f"""
        <h2 style="color:#4F46E5;">Convite para Projeto</h2>
        <p>Olá <strong>{nome_convidado}</strong>,</p>
        <p>Você foi convidado por <strong>{nome_convidante}</strong> para participar do projeto:</p>
        <h3 style="color:#4F46E5;">{nome_projeto}</h3>
        <p>Clique no botão abaixo para aceitar:</p>
        <a href="{url_aceitacao}"
           style="background:#4F46E5;color:white;padding:12px 24px;border-radius:5px;text-decoration:none;">
           Aceitar Convite
        </a>
        <p>Se o botão não funcionar, acesse:<br>
        {url_aceitacao}</p>
        """

        payload = {
            "personalizations": [
                {
                    "to": [{"email": email_convidado}],
                    "subject": assunto
                }
            ],
            "from": {"email": self.sender_from_email},
            "content": [
                {
                    "type": "text/html",
                    "value": mensagem_html
                }
            ]
        }

        print(f"📧 Enviando convite via SendGrid API para: {email_convidado}")

        try:
            response = requests.post(
                self.sendgrid_url,
                headers={
                    "Authorization": f"Bearer {self.sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code in (200, 202):
                print(f"✅ Email de convite enviado para {email_convidado}")
                return True
            else:
                print("❌ ERRO AO ENVIAR EMAIL:")
                print(response.status_code, response.text)
                return False

        except Exception as e:
            print(f"❌ Erro crítico ao enviar email: {e}")
            return False

    # ================================================================
    # ENVIAR REDEFINIÇÃO DE SENHA
    # ================================================================
    def enviar_redefinicao_senha(self, email_usuario, nome_usuario, token_redefinicao):

        url_redefinicao = f"{self.base_url}/redefinir-senha/{token_redefinicao}"

        assunto = "🔐 Redefinição de Senha - FofoTech"

        mensagem_html = f"""
        <h2 style="color:#4F46E5;">Redefinição de Senha</h2>
        <p>Olá <strong>{nome_usuario}</strong>,</p>
        <p>Para redefinir sua senha, clique no botão abaixo:</p>
        <a href="{url_redefinicao}"
           style="background:#4F46E5;color:white;padding:12px 24px;border-radius:5px;text-decoration:none;">
           Redefinir Senha
        </a>
        <p>Ou use o link abaixo:<br>
        {url_redefinicao}</p>
        """

        payload = {
            "personalizations": [
                {
                    "to": [{"email": email_usuario}],
                    "subject": assunto
                }
            ],
            "from": {"email": self.sender_from_email},
            "content": [
                {
                    "type": "text/html",
                    "value": mensagem_html
                }
            ]
        }

        print(f"📧 Enviando redefinição via SendGrid API para: {email_usuario}")

        try:
            response = requests.post(
                self.sendgrid_url,
                headers={
                    "Authorization": f"Bearer {self.sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code in (200, 202):
                print(f"✅ Email de redefinição enviado para {email_usuario}")
                return True
            else:
                print("❌ ERRO AO ENVIAR EMAIL:")
                print(response.status_code, response.text)
                return False

        except Exception as e:
            print(f"❌ Erro crítico no envio: {e}")
            return False


# ================================================================
# FUNÇÕES AUXILIARES (mantidas iguais)
# ================================================================
def gerar_token_convite():
    return secrets.token_urlsafe(32)

def calcular_expiracao(dias=7):
    return datetime.now() + timedelta(days=dias)
