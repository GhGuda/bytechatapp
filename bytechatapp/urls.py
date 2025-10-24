from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("frontpage", views.frontpage, name="frontpage"),
    path("chat/<str:username>/<str:contact>/", views.chat_view, name="chat_view"),
    path("send-message/", views.send_message, name="send_message"),
    path("fetch-messages/<str:contact>/", views.fetch_messages, name="fetch_messages"),
    path("newFriend", views.newFriend, name="newFriend"),
    path("message/edit/<int:msg_id>/", views.edit_message, name="edit_message"),
    path("message/delete/<int:msg_id>/", views.delete_message, name="delete_message"),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
]
