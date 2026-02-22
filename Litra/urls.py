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
    path('works/', views.works, name='works'),
    path('facts/', views.facts, name='facts'),
    path('tests/', views.tests, name='tests'),
    path('ai-assistant/', views.ai, name='ai_assistant'),
    path('search/', views.search, name="search"),
    path("about/", views.about, name="about"),
    path("exit/", views.exit, name="exit"),
    path("create_writer/", views.create_writer, name="create_writer"),
    path("create_work/", views.create_work, name="create_work"),
    path('api/', include(router.urls)),
    path('writers/<int:writer_id>/', views.writers, name='writer_detail'),
    path("quiz_create/", views.create_test, name="quiz_create"),
    path('api/quizzes/create/', CreateQuiz.as_view(), name='quiz_create_api'),
]