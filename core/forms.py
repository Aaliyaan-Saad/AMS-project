from django.contrib.auth.forms import AuthenticationForm


class EmailLoginForm(AuthenticationForm):
    """Login form that labels the identifier field as 'Email'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
