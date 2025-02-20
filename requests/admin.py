from django.contrib import admin
from .models import Form, Question, Answer, Submit


class AnswerFilter(admin.SimpleListFilter):
    title = 'Answer'
    parameter_name = 'answer'

    def lookups(self, request, model_admin):
        answers = Answer.objects.all()
        return [(answer.id, answer.answer) for answer in answers]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(answers__contains=self.value())
        return queryset


class SubmitAdmin(admin.ModelAdmin):
    list_display = ('user', 'form', 'created_at')
    search_fields = ('user__username', 'form__name')
    list_filter = (AnswerFilter,)


admin.site.register(Form)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Submit, SubmitAdmin)
