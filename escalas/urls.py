from django.urls import path
from . import views

urlpatterns = [
    path('escala/<int:unidade_id>/<int:mes>/<int:ano>/', views.gerar_escala, name='gerar_escala'),
<<<<<<< HEAD
    path('cadastrar/', views.cadastrar_escala, name='cadastrar_escala'),
    path('escala/<int:unidade_id>/<int:mes>/<int:ano>/', views.gerar_escala, name='escala_detalhe'),
    path('api/funcionarios/', views.get_funcionarios, name='get_funcionarios'),
    path('cobertura/', views.cobertura, name='cobertura'),
    path('ver_escalas/', views.ver_escalas, name='ver_escalas'),
=======
    #path('cadastrar/', views.cadastrar_escala, name='cadastrar_escala'),
    path('escala/<int:unidade_id>/<int:mes>/<int:ano>/', views.gerar_escala, name='escala_detalhe'),
    path('escala/api/funcionarios/', views.get_funcionarios, name='get_funcionarios'),
    path('cobertura/', views.cobertura, name='cobertura'),
    path('ver_escalas/', views.ver_escalas, name='ver_escalas'),

    path('escalas/escala/cadastrar/', views.EscalaCreateView.as_view(), name='cadastrar_escala'),
    path('escalas/escala/api/funcionarios/', views.api_funcionarios, name='api_funcionarios'),
>>>>>>> ba04dbe (Atualiza template escala com totais por período e cálculo de horas)
    
    
]