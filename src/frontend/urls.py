from django.urls import path, re_path
from .views import StartView, ConfirmView, ChangeView, ContactView, RulesView
from django.views.generic import TemplateView

# todo добавить регулряку для определения адреса вместо цикла как сейчас и ввода параметров cur_from и cur_to
# todo confirm есйчас цепляет и много лишних адресов. Сделать так чтобы этого небыло


urlpatterns = [
    path('', StartView.as_view()),
    path('rules/', RulesView.as_view()),
    # path('rules/', TemplateView.as_view(template_name='rules.html')),
    # path('faq/', TemplateView.as_view(template_name='faq.html', extra_context={'test': 'даже переменную передал'})),
    path('contacts/', ContactView.as_view()),
    # path('contacts/', TemplateView.as_view(template_name='contacts.html', extra_context={'mail': 'info@bitlab.work22'})),
    # path('lk/', TemplateView.as_view(template_name='lk.html')),
    re_path(r'(?P<left>[A-Z]{3,12})/(?P<right>[A-Z]{3,12})/(?P<idfromsite>\w{36})/change/', ChangeView.as_view()),
    re_path(r'(?P<left>[A-Z]{3,12})/(?P<right>[A-Z]{3,12})/(?P<idfromsite>\w{36})/', ConfirmView.as_view()),
]
