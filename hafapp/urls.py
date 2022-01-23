from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
path('', views.index),
path('register', views.register),
path('history', views.history),
path('processregister', views.processregister),
path('login', views.login),
path('logout', views.logout),
path('profile', views.profile),
path('managefriends', views.editfriends),
path('addfriend', views.addfriend),
path('removefriend/<int:friend_id>', views.removefriend),
path('ordersetup2/<int:fooditems>', views.ordersetup2),
path('processresults', views.processresults),
path('results', views.results),
path('order/<int:order_id>', views.editorder),
path('update/<int:order_id>', views.editorder),
path('updateorder/<int:order_id>', views.updatedresults),
path('processupdated/<int:order_id>', views.processupdated),

]