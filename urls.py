from django.conf.urls import url

from django_girosolution.views import NotifyGirosolutionView, GirosolutionReturnView

urlpatterns = [
    url(r'^notify/$', NotifyGirosolutionView.as_view(), name='notifiy'),
    url(r'^return/$', GirosolutionReturnView.as_view(), name='return'),
]
