import smtplib
from email.message import EmailMessage
import os
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv
load_dotenv()

class EmailService:
    def __init__(self):
        # Configurações SMTP — agora para SendGrid
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.sendgrid.net')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))

        # Usuário e senha SMTP
        # Para SendGrid:
        # USER = "apikey"
        # PASS = API KEY criada no painel
        self.sender_email_user = os.getenv('EMAIL_USER')   # sempre "apikey"
        self.sender_email_pass = os.getenv('EMAIL_PASSWORD')  # sua API KEY
        self.sender_from_email = os.getenv('EMAIL_FROM')  # email de envio

        # Base URL para links
        self.base_url = os.getenv("BASE_URL", "http://localhost:5000")

        # Verificação de variáveis
        if not self.sender_email_user or not self.sender_email_pass or not self.sender_from_email:
            print("⚠️ AVISO: Variáveis de email do SendGrid não estão configuradas corretamente.")

    # ---------------------------------------------------------------------
    # ENVIO DE CONVITE
    # ---------------------------------------------------------------------
    def enviar_convite_projeto(self, email_convidado, nome_convidado, nome_projeto, nome_convidante, token_convite):
        """Envia email de convite usando SendGrid SMTP"""

        # Gerar link real de produção
        url_aceitacao = f"{self.base_url}/convite/aceitar/{token_convite}"

        assunto = f"🎉 Convite para o projeto: {nome_projeto}"

        mensagem_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">Convite para Projeto</h2>

                <p>Olá <strong>{nome_convidado}</strong>,</p>

                <p>Você foi convidado por <strong>{nome_convidante}</strong> para participar do projeto:</p>

                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin: 0; color: #4F46E5;">{nome_projeto}</h3>
                </div>

                <p>Para aceitar este convite, clique no botão abaixo:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_aceitacao}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;
                              display: inline-block;">
                        ✅ Aceitar Convite
                    </a>
                </div>

                <p><strong>⚠️ Atenção:</strong> Este convite expira em 7 dias.</p>

                <p>Se o botão não funcionar, copie este link no navegador:</p>
                <p style="word-break: break-all; color: #4F46E5;">{url_aceitacao}</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">Se você não reconhece este convite, ignore este email.</p>
            </div>
        </body>
        </html>
        """

        try:
            print(f"📧 Tentando enviar convite via SendGrid para: {email_convidado}")

            msg = EmailMessage()
            msg["Subject"] = assunto
            msg["From"] = self.sender_from_email
            msg["To"] = email_convidado
            msg.set_content("Você recebeu um convite para participar de um projeto.")
            msg.add_alternative(mensagem_html, subtype="html")

            # Conectando via SendGrid SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email_user, self.sender_email_pass)
                server.send_message(msg)

            print(f"✅ Email de convite via SendGrid enviado para: {email_convidado}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar email de convite (SendGrid): {e}")
            return False

    # ---------------------------------------------------------------------
    # ENVIO DE LINK DE REDEFINIÇÃO
    # ---------------------------------------------------------------------
    def enviar_redefinicao_senha(self, email_usuario, nome_usuario, token_redefinicao):
        """Envia email de redefinição de senha via SendGrid"""

        url_redefinicao = f"{self.base_url}/redefinir-senha/{token_redefinicao}"

        assunto = "🔐 Redefinição de Senha - FofoTech"

        mensagem_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4F46E5; text-align: center;">Redefinição de Senha</h2>

                <p>Olá <strong>{nome_usuario}</strong>,</p>

                <p>Recebemos uma solicitação para redefinir sua senha.</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_redefinicao}"
                       style="background-color: #4F46E5; color: white; padding: 12px 24px;
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        🔑 Redefinir Senha
                    </a>
                </div>

                <p>Se o botão não funcionar, use este link:</p>
                <p style="word-break: break-all; color: #4F46E5;">{url_redefinicao}</p>

                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    Se você não solicitou, ignore este email.
                </p>
            </div>
        </body>
        </html>
        """

        try:
            print(f"📧 Tentando enviar email de redefinição via SendGrid para: {email_usuario}")

            msg = EmailMessage()
            msg["Subject"] = assunto
            msg["From"] = self.sender_from_email
            msg["To"] = email_usuario
            msg.set_content(f"Redefina sua senha acessando: {url_redefinicao}")
            msg.add_alternative(mensagem_html, subtype="html")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email_user, self.sender_email_pass)
                server.send_message(msg)

            print(f"✅ Email de redefinição via SendGrid enviado para: {email_usuario}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar email de redefinição (SendGrid): {e}")
            return False


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================
def gerar_token_convite():
    return secrets.token_urlsafe(32)

def calcular_expiracao(dias=7):
    return datetime.now() + timedelta(days=dias)
