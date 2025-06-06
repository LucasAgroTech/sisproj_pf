# Session.Py
class Session:
    """Classe para gerenciar a sessão do usuário"""

    current_user = None

    @classmethod
    def login(cls, user):
        """
        Define o usuário logado

        Args:
            user: Dados do usuário
        """
        cls.current_user = user

    @classmethod
    def logout(cls):
        """Finaliza a sessão do usuário"""
        cls.current_user = None

    @classmethod
    def get_user(cls):
        """
        Retorna o usuário atual

        Returns:
            Dados do usuário logado ou None
        """
        return cls.current_user
