from django.core.exceptions import ObjectDoesNotExist
from rest_auth.views import LoginView
from app.models import UserProfile

class CustomLoginView(LoginView):
    def get_response(self):
        response = super().get_response()
        response.data.update(self.check_user_profile())
        return response

    def check_user_profile(self):
        try:
            print('check_user_profile')
            UserProfile.objects.get(user=self.user)
            return {"is_need_update_profile": False}
        except ObjectDoesNotExist as e:
            return {"is_need_update_profile": True}
