from django.db import models
from django.contrib.auth.models import User


class Writers(models.Model):

    full_name = models.CharField(max_length=200)
    image_url = models.URLField()
    birth_year = models.IntegerField()
    death_year = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=100)  # кто он: писатель, поэт, драмматург и тд
    quote = models.CharField(max_length=200)  # известная цитата
    biography = models.TextField()
    century = models.IntegerField()
    favorited_by = models.ManyToManyField(User, related_name='favorite_writers', blank=True, default=None)

    def __str__(self):
        return self.full_name


class Works(models.Model):
    genre = models.CharField(max_length=200)
    period = models.CharField(max_length=200)
    cover_image = models.URLField()
    title = models.CharField(max_length=200)
    author_name = models.ForeignKey(
        Writers,
        on_delete=models.PROTECT,
        related_name='works'
    )
    publication_year = models.IntegerField()
    description = models.TextField()
    favorited_by = models.ManyToManyField(User, related_name='favorite_books', blank=True, default=None)

    def __str__(self):
        return self.title


class Facts(models.Model):
    title = models.CharField(max_length=250, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание факта")
    writer = models.ForeignKey(Writers, on_delete=models.CASCADE, related_name='facts', blank=True, null=True)
    work = models.ForeignKey(Works, on_delete=models.CASCADE, related_name='facts', blank=True, null=True)
    CATEGORY_CHOICES = [
        ('biography', 'Биография'),
        ('creative', 'Творчество'),
        ('trivia', 'Интересное'),
        ('history', 'Исторический контекст'),
        ('influence', 'Влияние и наследие'),
        ('general', 'Общая литература')
    ]
    PERIOD_CHOICES = [
        ('17', 'XVII век'),
        ('18', 'XVIII век'),
        ('19', 'XIX век'),
        ('20', 'XX век'),
        ('21', 'XXI век')
    ]
    period = models.CharField(choices=PERIOD_CHOICES, blank=True, max_length=2, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50, default='trivia')
    image_url = models.URLField()
    source = models.CharField(max_length=300, blank=True)
    favorited_by = models.ManyToManyField(User, related_name='favorite_facts')
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_facts', blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Факт"
        verbose_name_plural = "Факты"

    def __str__(self):
        return self.title

    @property
    def related_to(self):
        if self.work:
            return self.work
        elif self.writer:
            return self.writer
        else:
            return "Общий факт о литературе"


class Quizz(models.Model):
    title = models.CharField(max_length=200, verbose_name='Test-name')
    description = models.TextField()
    writer = models.ForeignKey(Writers, on_delete=models.PROTECT, related_name='Quizzes', null=True, blank=True)
    work = models.ForeignKey(Works, on_delete=models.PROTECT, related_name='Quizzes', null=True, blank=True)

    DIF_CHOICES = [
        ('easy', 'Лёгкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    difficulty = models.CharField(choices=DIF_CHOICES, max_length=50)
    times_taken = models.IntegerField(default=0)


class Question(models.Model):
    quiz = models.ForeignKey(Quizz, on_delete=models.PROTECT, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']


class Chats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    ROLES = [('user', 'пользователь'),
             ('assistant', 'ассистент')]
    chat = models.ForeignKey(Chats, on_delete=models.PROTECT, related_name='messages')
    role = models.CharField(choices=ROLES, max_length=10)
    content = models.TextField()




