from django.conf.urls import include, url
from .views import MessengerBot
urlpatterns = [
    url(r'^502ed0d70ad531c20d318106aaddf284cdf08ed367002db13f/?$',MessengerBot.as_view())
]
