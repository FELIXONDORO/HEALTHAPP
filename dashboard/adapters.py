from django.contrib.auth import get_user_model
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class ApexSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Use a Google email as the username and auto-link accounts for this email-first application."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = (data.get("email") or "").strip().lower()
        if email:
            user.email = email
            user.username = email
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        return user

    def pre_social_login(self, request, sociallogin):
        """If a user already registered with this email, connect the Google login automatically."""
        if sociallogin.is_existing:
            return
        if request.user.is_authenticated:
            return

        email = (sociallogin.account.extra_data.get("email") or "").strip().lower()
        if not email:
            return

        User = get_user_model()
        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user:
            sociallogin.connect(request, existing_user)

