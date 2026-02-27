from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from google import genai
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F, Count
from .filters import WriterFilter, WorksFilter, FactsFilter, TestFilter
from .models import Writers, Works, Facts, Quizz, Question, Answer, Chats, Message
from rest_framework.views import APIView
from django.contrib.auth.decorators import user_passes_test
from .serializers import WriterSerializer, WorksSerializer, FactsSerializer, FastTest, PropertyTest, ChatSerializer, \
    MessageSerializer
from rest_framework.permissions import IsAdminUser


def is_staff_or_moderator(user):
    return user.is_staff or user.groups.filter(name='seller').exists()


class ListMixin():
    response_key = 'result'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.prefetch_related('favorited_by')
        serializer = self.get_serializer(queryset, many=True)
        return Response({self.response_key: serializer.data})


class FavoriteMixin():
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


class WriterViewSet(ListMixin, FavoriteMixin, viewsets.ModelViewSet):
    queryset = Writers.objects.all().prefetch_related('favorited_by')
    serializer_class = WriterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WriterFilter
    response_key = 'writers'


class WorksViewSet(ListMixin, FavoriteMixin, viewsets.ModelViewSet):
    queryset = Works.objects.select_related('author_name').all()
    serializer_class = WorksSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorksFilter
    response_key = 'works'


def works(request, pk=None):
    return render(request, "Litra/works.html")


class FactsViewSet(ListMixin, viewsets.ModelViewSet):
    queryset = Facts.objects.all()
    serializer_class = FactsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FactsFilter
    response_key = 'facts'

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


def facts(request, pk=None):
    return render(request, "Litra/facts.html")


class TestsViewSet(viewsets.ModelViewSet):
    queryset = Quizz.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TestFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'quizzes': serializer.data})

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.select_related('work', 'writer').annotate(question_count=Count('questions'))
        elif self.action == 'retrieve':
            return qs.select_related('work', 'writer').prefetch_related('questions', 'questions__options')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return FastTest
        return PropertyTest

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        quiz = self.get_object()
        Quizz.objects.filter(pk=pk).update(times_taken=F('times_taken') + 1)
        answers = request.data.get('answers', [])
        print('answers:', answers)
        answer_map = {a['question_id']: a['option_id'] for a in answers}
        print('answer_map:', answer_map)

        question = Question.objects.filter(quiz_id=pk).prefetch_related('options').order_by('order')
        score = 0
        results = []
        for q in question:
            correct_option = None
            correct_option_text = None
            opt_text = None
            selected_id = answer_map.get(q.id)
            for opt in q.options.all():
                if opt.is_correct:
                    correct_option = opt.id
                    correct_option_text = opt.text
                if opt.id == selected_id:
                    opt_text = opt.text
            is_correct = False
            if selected_id == correct_option:
                is_correct = True
                score +=1
            results.append({
                'question_id': q.id,
                'question_text': q.text,
                'is_correct': is_correct,
                'selected_option_id': selected_id,
                'selected_option_text': opt_text,
                'correct_option_id': correct_option,
                'correct_option_text': correct_option_text
            })
        total = len(results)
        percentage = (score / total) * 100
        if percentage >= 90:
            grade = 'excellent'
        elif percentage >= 70:
            grade = 'good'
        elif percentage >= 50:
            grade = 'okay'
        else:
            grade = 'poor'
        return Response(
            {
                'score': score,
                'total':total,
                'percentage': percentage,
                'grade': grade,
                'results': results
            }
        )


def tests(request, pk=None):
    return render(request, 'Litra/test.html')


def search():
    pass


def about():
    pass


def exit(request):
    logout(request)
    return redirect('login')


@user_passes_test(is_staff_or_moderator)
def create_writer(request):
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


@user_passes_test(is_staff_or_moderator)
def create_work(request):
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


@user_passes_test(is_staff_or_moderator)
def create_test(request):
    writer = Writers.objects.all().order_by('full_name')
    work = Works.objects.all().order_by('title')
    return render(request, 'Litra/create_test.html', {
        'writers': writer,
        'works': work
    })


class CreateQuiz(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        data = request.data
        quiz = Quizz.objects.create(
            title=data['title'],
            description=data['description'],
            writer_id=data.get('writer'),
            work_id=data.get('work'),
            difficulty=data.get('difficulty')
        )

        for i, q_data in enumerate(data['questions'], start=1):
            question = Question.objects.create(
                quiz=quiz,
                text=q_data['text'],
                order=i
            )
            Answer.objects.bulk_create(
                [
                    Answer(
                        question=question,
                        text=opt['text'],
                        is_correct=opt['is_correct'],
                        order=i
                    ) for i, opt in enumerate(q_data['options'], start=1)
                ]
            )
        return Response({'id': quiz.id}, status=201)


@user_passes_test(is_staff_or_moderator)
def create_fact(request):
    if request.method == 'POST':
        Facts.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            category=request.POST['category'],
            period=request.POST.get('period') or None,
            writer_id=request.POST.get('writer') or None,
            work_id=request.POST.get('work') or None,
            image_url=request.POST.get('image_url', ''),
            source=request.POST.get('source', ''),
            is_featured=bool(request.POST.get('is_featured'))
        )
        return redirect('facts')

    writers = Writers.objects.all().order_by('full_name')
    works = Works.objects.all().order_by('title')
    return render(request, 'Litra/create_fact.html', {
        'writers': writers,
        'works': works
    })


def ai_assistant(request):
    return render(request, 'Litra/ai-assistant.html')


class ChatsViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'messages':
            return MessageSerializer
        return ChatSerializer

    def get_queryset(self):
        if self.action == 'messages':
            chat_id = self.kwargs['pk']
            return Message.objects.filter(chat_id=chat_id)
        return Chats.objects.filter(user=self.request.user)

    @action(methods=['get', 'post'], detail=True, url_path='messages')
    def messages(self, request, pk=None):
        if request.method=='GET':
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        content = request.data['content']
        Message.objects.create(chat_id=pk, role='user', content=content)
        client = genai.Client()
        chat = self.get_object()
        history = Message.objects.filter(chat_id=pk).order_by('created_at')
        contents = [{'role': m.role, 'parts': [m.content]} for m in history]
        response = client.models.generate_content(
            model="gemini-3-flash-preview", contents=contents
        )
        Message.objects.create(chat_id=pk, role='assistant', content=response.text)

        return Response({'reply': response.text,
                         'chat_title': chat.title})


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


