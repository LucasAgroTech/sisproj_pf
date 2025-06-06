# Auth Controller.Py
from models.user_model import authenticate
from utils.session import Session
from utils.logger import log_action
from tkinter import messagebox


def login(username, password, on_success, on_failure):
    """
    Realiza o login do usuário no sistema

    Args:
        username (str): Nome do usuário
        password (str): Senha do usuário
        on_success: Callback para login bem-sucedido
        on_failure: Callback para falha no login
    """
    user = authenticate(username, password)
    if user:
        Session.login(user)
        log_action(username, "Login realizado")
        on_success()
    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")
        on_failure()
