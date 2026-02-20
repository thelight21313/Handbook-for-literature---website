from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import WriterFilter, WorksFilter, FactsFilter, TestFilter
from .models import Writers, Works, Facts, Quizz
from rest_framework.views import APIView

from .serializers import WriterSerializer, WorksSerializer, FactsSerializer, FastTest, PropertyTest


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Создаем пользователя
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'Litra/register.html', {'form': form})


def home(request):
    return render(request, "Litra/home.html")


class WriterViewSet(viewsets.ModelViewSet):
    queryset = Writers.objects.all().prefetch_related('favorited_by')
    serializer_class = WriterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WriterFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'writers': serializer.data})

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        work = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        if work.favorited_by.filter(id=user.id).exists():
            work.favorited_by.remove(user)
            return Response({'is_favorite': False})
        elif not work.favorited_by.filter(id=user.id).exists():
            work.favorited_by.add(user)
            return Response({'is_favorite': True})


def writers(request):
    return render(request, "Litra/writers.html")


class WorksViewSet(viewsets.ModelViewSet):
    queryset = Works.objects.select_related('author_name').all()
    serializer_class = WorksSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorksFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'works': serializer.data})

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        work = self.get_object()
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=status.HTTP_401_UNAUTHORIZED)
        if work.favorited_by.filter(id=user.id).exists():
            work.favorited_by.remove(user)
            return Response({'is_favorite': False})
        elif not work.favorited_by.filter(id=user.id).exists():
            work.favorited_by.add(user)
            return Response({'is_favorite': True})


def works(request, pk=None):
    return render(request, "Litra/works.html")


class FactsViewSet(viewsets.ModelViewSet):
    queryset = Facts.objects.all()
    serializer_class = FactsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FactsFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.prefetch_related('likes')
        serializer = self.get_serializer(queryset, many=True)
        return Response({'facts': serializer.data})

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        fact = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Авторизуйтесь"}, status=401)

        if user in fact.likes.all():
            fact.likes.remove(user)
            is_liked = False
        else:
            fact.likes.add(user)
            is_liked = True

        return Response({
            'is_liked': is_liked,
            'likes_count': fact.likes.count()
        })


def facts(request):
    return render(request, "Litra/facts.html")


class Tests(viewsets.ModelViewSet):
    queryset = Quizz.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TestFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return FastTest
        return PropertyTest


def tests(request):
    return render(request, 'Litra/test.html')


def ai():
    pass


def search():
    pass


def about():
    pass


def exit(request):
    logout(request)
    return redirect('login')


def create_writer(request):
    is_manager = request.user.groups.filter(name='seller').exists()
    is_admin = request.user.is_superuser
    if not is_manager and not is_admin:
        return redirect('home')
    if request.method == "POST":
        birth_year = request.POST.get("birth_year")
        new_writer = Writers.objects.create(
            full_name=request.POST.get("full_name"),
            birth_year=birth_year,
            death_year=request.POST.get("death_year"),
            genre=request.POST.get("genre"),
            biography=request.POST.get("biography"),
            quote=request.POST.get("quote"),
            image_url=request.POST.get("image_url"),
            century=(int(birth_year)-1)//100 + 1
        )
    return render(request, "Litra/create_writer.html")


def create_work(request):
    is_manager = request.user.groups.filter(name='seller').exists()
    is_admin = request.user.is_superuser
    if not is_manager and not is_admin:
        return redirect('home')
    if request.method == "POST":
        birth_year = request.POST.get("birth_year")
        new_work = Works.objects.create(
            title=request.POST['title'],
            author_name_id=request.POST['author_name'],
            period=request.POST['period'],
            publication_year=request.POST['publication_year'],
            genre=request.POST['genre'],
            description=request.POST['description'],
            cover_image=request.POST['cover_image']
        )
        return redirect('works')
    writers = Writers.objects.all().order_by('full_name')
    return render(request, "Litra/create_works.html", {'writers': writers})


def writers(request, writer_id=None):
    return render(request, 'Litra/writers.html')