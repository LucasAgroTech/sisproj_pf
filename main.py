# Main.Py
import tkinter as tk
from models.db_manager import init_db
from views.login_view import LoginView
from controllers.auth_controller import login
from views.dashboard_view import DashboardView
from utils.ui_utils import mostrar_mensagem, Estilos, Cores


def on_login_success():
    """Callback quando o login é bem-sucedido"""
    root.destroy()
    main_app()


def on_login_failure():
    """Callback quando o login falha"""
    mostrar_mensagem("Erro", "Usuário ou senha inválidos.", tipo="erro")


def main_app():
    """Inicia a aplicação principal após o login"""
    app = tk.Tk()
    app.title("SISPROJ - PESSOA FÍSICA")
    app.state("zoomed")  # Maximiza a janela no Windows

    # Define tema para a aplicação
    app.configure(background=Cores.BACKGROUND_CLARO)
    Estilos.configurar()

    # Carrega o dashboard
    DashboardView(app)

    app.mainloop()


if __name__ == "__main__":
    # Inicializa o banco de dados
    init_db()

    # Inicia a tela de login
    root = tk.Tk()
    root.configure(background=Cores.BACKGROUND_CLARO)
    Estilos.configurar()

    LoginView(root, lambda u, p: login(u, p, on_login_success, on_login_failure))

    # Centraliza a janela de login
    window_width = 400
    window_height = 450
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    root.mainloop()
