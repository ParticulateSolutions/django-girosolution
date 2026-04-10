from django.conf.urls import url

from django_girosolution.views import NotifyGirosolutionView, GirosolutionReturnView, NotifyPaypageView, PaypageReturnView

urlpatterns = [
    url(r'^notify/$', NotifyGirosolutionView.as_view(), name='notifiy'),
    url(r'^return/$', GirosolutionReturnView.as_view(), name='return'),
    url(r'^paypage/notify/$', NotifyPaypageView.as_view(), name='paypage_notify'),
    url(r'^paypage/return/$', PaypageReturnView.as_view(), name='paypage_return'),
]
