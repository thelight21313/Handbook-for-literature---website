from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from django.contrib.auth import views as auth_views
from .views import WriterViewSet, WorksViewSet, FactsViewSet, CreateQuiz, TestsViewSet

router = DefaultRouter()
router.register(r'writers', WriterViewSet)
router.register(r'works', WorksViewSet)
router.register(r'facts', FactsViewSet)
router.register(r'tests', TestsViewSet)

urlpatterns = [
    path('login/',
         auth_views.LoginView.as_view(
             template_name='Litra/login.html',
             redirect_authenticated_user=True
         ),
         name='login'),
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('writers/', views.writers, name='writers'),
    path('writers/<int:pk>/', views.writers, name='writer_detail'),
    path('works/', views.works, name='works'),
    path('works/<int:pk>/', views.works, name='work_detail'),
    path('facts/', views.facts, name='facts'),
    path('facts/<int:pk>/', views.facts, name='fact_detail'),
    path('tests/', views.tests, name='tests'),
    path('tests/<int:pk>/', views.tests, name='test_detail'),
    path('tests/<int:pk>/result/', views.tests, name='test_result'),
    path('search/', views.search, name="search"),
    path("about/", views.about, name="about"),
    path("exit/", views.exit, name="exit"),
    path("create_writer/", views.create_writer, name="create_writer"),
    path("create_work/", views.create_work, name="create_work"),
    path('api/', include(router.urls)),
    path("quiz_create/", views.create_test, name="quiz_create"),
    path('api/quizzes/create/', CreateQuiz.as_view(), name='quiz_create_api'),
    path('create_fact', views.create_fact, name='create_fact'),
    path('ai-assistant/', views.ai_assistant, name='ai-assistant'),
    path('ai_assistant/', views.ai_assistant, name='ai_assistant')
]