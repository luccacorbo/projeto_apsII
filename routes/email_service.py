import os
import secrets
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis locais (Railway usa variáveis internas automaticamente)

class EmailService:
    def _init_(self):
        # API Key do SendGrid
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_from_email = os.getenv("EMAIL_FROM")
        self.base_url = os.getenv("BASE_URL", "http://localhost:5000")

        if not self.sendgrid_api_key or not self.sender_from_email:
            print("⚠ ERRO: SENDGRID_API_KEY ou EMAIL_FROM não configurados no Railway.")

        # URL oficial da API SendGrid
        self.sendgrid_url = "https://api.sendgrid.com/v3/mail/send"

    # ================================================================
    # MÉTODO PRIVADO CENTRALIZADO PARA ENVIAR EMAILS
    # (Isso evita duplicação de código - Princípio DRY)
    # ================================================================
    def _enviar_email_sendgrid(self, email_destinatario, assunto, mensagem_html):
        """
        Função auxiliar privada para montar o payload e enviar o email via SendGrid.
        """
        
        payload = {
            "personalizations": [
                {
                    "to": [{"email": email_destinatario}],
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

        print(f"📧 Preparando envio via SendGrid para: {email_destinatario} (Assunto: {assunto})")

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
                print(f"✅ Email enviado com sucesso para {email_destinatario}")
                return True
            else:
                print(f"❌ ERRO AO ENVIAR EMAIL para {email_destinatario}:")
                print(f"Status: {response.status_code}")
                print(f"Resposta: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Erro crítico na requisição para SendGrid: {e}")
            return False

    # ================================================================
    # ENVIAR CONVITE PARA PROJETO
    # (Agora usando o novo template e o método central)
    # ================================================================
    def enviar_convite_projeto(self, email_convidado, nome_convidado, nome_projeto, nome_convidante, token_convite):

        url_aceitacao = f"{self.base_url}/convite/aceitar/{token_convite}"
        assunto = f"🎉 Você foi convidado para o projeto: {nome_projeto}"

        # Template HTML Profissional (Versão 1 - Convite)
        mensagem_html = f"""
        <body style="margin: 0; padding: 0; background-color: #f6f9fc; font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td style="padding: 20px 0;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                            
                            <tr>
                                <td align="center" style="background-color: #4F46E5; padding: 30px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Você recebeu um convite!</h1>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #333333; margin-top: 0;">Olá, {nome_convidado}!</h2>
                                    
                                    <p style="color: #555555; line-height: 1.6; font-size: 16px;">
                                        Boas notícias! <strong>{nome_convidante}</strong> convidou você para colaborar no projeto:
                                    </p>
                                    
                                    <div style="background-color: #f6f9fc; padding: 15px 20px; border-radius: 5px; text-align: center; margin: 25px 0;">
                                        <h3 style="color: #4F46E5; margin: 0; font-size: 20px;">{nome_projeto}</h3>
                                    </div>
                                    
                                    <p style="color: #555555; line-height: 1.6; font-size: 16px; text-align: center;">
                                        Para aceitar o convite e começar, clique no botão abaixo.
                                    </p>
                                    
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px; margin-bottom: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{url_aceitacao}" target="_blank"
                                                   style="background-color: #4F46E5; color: #ffffff; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 16px;">
                                                    Aceitar e Acessar Projeto
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #777777; font-size: 14px; line-height: 1.5;">
                                        Se o botão não funcionar, copie e cole este link no seu navegador:
                                        <br>
                                        <a href="{url_aceitacao}" target="_blank" style="color: #4F46E5; text-decoration: none; word-break: break-all;">
                                            {url_aceitacao}
                                        </a>
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="background-color: #f1f4f8; padding: 20px 30px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; text-align: center;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        © 2025 FofoTechs. Todos os direitos reservados.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        """
        
        # Chama o método centralizado
        return self._enviar_email_sendgrid(email_convidado, assunto, mensagem_html)

    # ================================================================
    # ENVIAR REDEFINIÇÃO DE SENHA
    # (Agora usando o novo template e o método central)
    # ================================================================
    def enviar_redefinicao_senha(self, email_usuario, nome_usuario, token_redefinicao):

        url_redefinicao = f"{self.base_url}/redefinir-senha/{token_redefinicao}"
        
        # Usei o assunto que você já tinha definido no seu código
        assunto = "🔐 Redefinição de Senha - FofoTech"

        # Template HTML Profissional (Versão 2 - Redefinição de Senha)
        mensagem_html = f"""
        <body style="margin: 0; padding: 0; background-color: #f6f9fc; font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td style="padding: 20px 0;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                            
                            <tr>
                                <td align="center" style="background-color: #4F46E5; padding: 30px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px;">Redefinição de Senha</h1>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="padding: 40px 30px;">
                                    <h2 style="color: #333333; margin-top: 0;">Olá, {nome_usuario}.</h2>
                                    
                                    <p style="color: #555555; line-height: 1.6; font-size: 16px;">
                                        Recebemos uma solicitação para redefinir a senha da sua conta na FofoTech.
                                    </p>
                                    
                                    <p style="color: #555555; line-height: 1.6; font-size: 16px;">
                                        Se foi você, clique no botão abaixo para criar uma nova senha:
                                    </p>
                                    
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px; margin-bottom: 30px;">
                                        <tr>
                                            <td align="center">
                                                <a href="{url_redefinicao}" target="_blank"
                                                   style="background-color: #4F46E5; color: #ffffff; padding: 14px 28px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 16px;">
                                                    Redefinir Minha Senha
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="color: #777777; font-size: 14px; line-height: 1.5; margin-top: 25px;">
                                        <strong>Não solicitou essa mudança?</strong>
                                        <br>
                                        Se você não solicitou uma nova senha, pode ignorar este e-mail com segurança.
                                    </p>
                                    
                                    <p style="color: #777777; font-size: 14px; line-height: 1.5; margin-top: 15px;">
                                        Se o botão não funcionar, copie e cole este link no seu navegador:
                                        <br>
                                        <a href="{url_redefinicao}" target="_blank" style="color: #4F46E5; text-decoration: none; word-break: break-all;">
                                            {url_redefinicao}
                                        </a>
                                    </p>
                                </td>
                            </tr>
                            
                            <tr>
                                <td style="background-color: #f1f4f8; padding: 20px 30px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; text-align: center;">
                                    <p style="color: #999999; font-size: 12px; margin: 0;">
                                        © 2025 FofoTech. Todos os direitos reservados.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        """
        
        # Chama o método centralizado
        return self._enviar_email_sendgrid(email_usuario, assunto, mensagem_html)


# ================================================================
# FUNÇÕES AUXILIARES (mantidas iguais)
# ================================================================
def gerar_token_convite():
    return secrets.token_urlsafe(32)

def calcular_expiracao(dias=7):
    return datetime.now() + timedelta(days=dias)