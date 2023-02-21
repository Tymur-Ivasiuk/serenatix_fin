from django.urls import path

from .views import *

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('verify/<email_code>/', verify, name='verify'),

    path('generate/', GenerateView.as_view(), name='generate'),
    path('questions/', QuestionsView.as_view(), name='questions'),
    # path('generating-process/', generate_process, name='generating'),
    path('content/<int:content_id>', ContentView.as_view(), name='content'),
    path('change/<int:content_id>', change_questions, name='change_questions'),
    path('archive/', ArchiveView.as_view(), name='archive'),

    path('contact/', ContactView.as_view(), name='contact'),

    # account
    path('account/', AccountView.as_view(), name='account'),
    path('logout/', logout_user, name='logout'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # passwords
    path('password_reset/', ChangePasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', ChangePasswordResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ChangePasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', ChangePasswordResetComplete.as_view(), name='password_reset_complete'),

    # transaction
    path('complete-transation', completeTransation, name='completeTransation'),

    # emails send
    path('send-to-my-email/<int:content_id>', send_to_my_email, name='send_to_my_email'),
    path('send-to-partner-email/<int:content_id>', send_to_partner_email, name='send_to_partner_email'),
]
