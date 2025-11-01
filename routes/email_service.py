import smtplib
from email.message import EmailMessage
import os
from datetime import datetime, timedelta
import secrets

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('EMAIL_USER')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
    
    def enviar_convite_projeto(self, email_convidado, nome_convidado, nome_projeto, nome_convidante, token_convite):
        """Envia email de convite para participar de um projeto"""
        
        # URL para aceitar o convite
        url_aceitacao = f"http://localhost:5000/convite/aceitar/{token_convite}"
        
        assunto = f"🎉 Convite para o projeto: {nome_projeto}"
        
        # Corpo do email em HTML
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
                
                <p>Para aceitar este convite e começar a colaborar, clique no botão abaixo:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_aceitacao}" 
                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;
                              display: inline-block;">
                        ✅ Aceitar Convite
                    </a>
                </div>
                
                <p><strong>⚠️ Atenção:</strong> Este convite expira em 7 dias.</p>
                
                <p>Se o botão não funcionar, copie e cole este link no seu navegador:</p>
                <p style="word-break: break-all; color: #4F46E5;">{url_aceitacao}</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    Se você não reconhece este convite, ignore este email.
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            # Configurar mensagem usando EmailMessage (mais moderna)
            msg = EmailMessage()
            msg['Subject'] = assunto
            msg['From'] = self.sender_email
            msg['To'] = email_convidado
            
            # Definir conteúdo HTML
            msg.set_content(mensagem_html, subtype='html')
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email de convite enviado para: {email_convidado}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            return False

def gerar_token_convite():
    """Gera um token único para o convite"""
    return secrets.token_urlsafe(32)

def calcular_expiracao(dias=7):
    """Calcula data de expiração do convite"""
    return datetime.now() + timedelta(days=dias)