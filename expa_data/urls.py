from django.urls import path

from .views import sync_signups_to_podio, sync_expa_data, funnel_dashboard, sync_signup_people, sync_expa_opportunities



urlpatterns = [

    path('sync-podio/', sync_signups_to_podio, name='sync_signups_to_podio'),

    path('sync-applications/', sync_expa_data, name='sync_expa_data'),

    path('funnel/', funnel_dashboard, name='funnel_dashboard'),

    path('sync-signups/', sync_signup_people, name='sync_signup_people'),

    path('sync-opportunities/', sync_expa_opportunities, name='sync_expa_opportunities'),

]