from django.urls import path, re_path
from .views import StartView, ConfirmView,  ContactView, RulesView

# todo добавить регулряку для определения адреса вместо цикла как сейчас и ввода параметров cur_from и cur_to
# todo confirm есйчас цепляет и много лишних адресов. Сделать так чтобы этого небыло


urlpatterns = [
    path('', StartView.as_view()),
    path('rules/', RulesView.as_view()),
    path('contacts/', ContactView.as_view()),
    re_path(r'(?P<left>[A-Z]{3,12})/(?P<right>[A-Z]{3,12})/(?P<idfromsite>\w{36})/', ConfirmView.as_view()),
]
