from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ConfirmacaoEmailTokenGenerator(PasswordResetTokenGenerator):
    """Token temporário invalidado quando a conta é ativada."""

    def _make_hash_value(self, user, timestamp):
        valor_base = super()._make_hash_value(user, timestamp)
        return f"{valor_base}{user.is_active}"


confirmacao_email_token = ConfirmacaoEmailTokenGenerator()
