from django.contrib import admin

from Litra.models import Writers, Works, Facts, Quizz, Question, Answer

# Register your models here.
admin.site.register(Writers)
admin.site.register(Works)
admin.site.register(Facts)
admin.site.register(Quizz)
admin.site.register(Question)
admin.site.register(Answer)