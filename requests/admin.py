from django.utils.timezone import is_aware, make_naive
from django.contrib import admin
from django.db.models import Q
from django.contrib.admin import SimpleListFilter
import json
from .models import Form, Question, Answer, Submit, Users
import csv
import json
import pandas as pd
from django.http import HttpResponse


class FormFilter(SimpleListFilter):
    title = 'Form'
    parameter_name = 'form'

    def lookups(self, request, model_admin):
        forms = Form.objects.filter(
            submit__isnull=False
        ).distinct().order_by('name')
        return [(str(f.id), f.name) for f in forms]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(form_id=self.value())


class AnswerFilter(SimpleListFilter):
    title = 'Answers'
    parameter_name = 'answer'

    def lookups(self, request, model_admin):
        form_id = request.GET.get('form')
        if not form_id:
            return []

        try:
            # Get all answers that are actually used in submissions for this form
            used_answers = set()
            for submit in Submit.objects.filter(form=form_id):
                answers = submit.answers
                if isinstance(answers, str):
                    answers = json.loads(answers)
                for answer_id in answers.values():
                    used_answers.add(str(answer_id))

            # Get the answer texts for all used answer IDs
            answers = Answer.objects.filter(
                id__in=used_answers,
                question__form=form_id
            ).distinct().order_by('answer')

            return [(str(a.id), a.answer) for a in answers]
        except (Form.DoesNotExist, ValueError, json.JSONDecodeError):
            return []

    def queryset(self, request, queryset):
        values = request.GET.getlist(self.parameter_name)
        if not values:
            return queryset

        # Build a query that matches any of the selected answers
        answer_queries = Q()
        for value in values:
            answer_queries |= Q(answers__contains=f'"{value}"')

        return queryset.filter(answer_queries)

    def choices(self, changelist):
        # Get current selections
        selected = changelist.params.get(self.parameter_name, [])
        if isinstance(selected, str):
            selected = [selected]
        elif not isinstance(selected, list):
            selected = []
        selected = set(selected)

        # All option
        yield {
            'selected': not selected,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'All'
        }

        # Each answer option
        for lookup, title in self.lookup_choices:
            str_lookup = str(lookup)

            # Handle multiple selection
            if str_lookup in selected:
                # Remove this value if already selected
                new_selected = [v for v in selected if v != str_lookup]
            else:
                # Add this value to existing selections
                new_selected = list(selected) + [str_lookup]

            # Build query string
            query_dict = {
                self.parameter_name: new_selected} if new_selected else {}

            yield {
                'selected': str_lookup in selected,
                'query_string': changelist.get_query_string(query_dict),
                'display': title
            }


class SubmitAdmin(admin.ModelAdmin):
    list_display = ('user', 'form', 'created_at', 'formatted_answers')
    search_fields = ('user__username', 'user__phone_number', 'form__name')
    list_filter = (FormFilter, AnswerFilter, 'created_at')
    list_per_page = 50

    def formatted_answers(self, obj):
        try:
            answers_dict = obj.answers if isinstance(
                obj.answers, dict) else json.loads(obj.answers)
            formatted = []

            # Get questions in order from the form
            questions = list(obj.form.questions.all())

            # Create a cache of answer objects
            answer_ids = set(str(v) for v in answers_dict.values())
            answer_objects = {
                str(a.id): a.answer
                for a in Answer.objects.filter(id__in=answer_ids)
            }

            # Format each answer
            for q_num, answer_id in answers_dict.items():
                q_index = int(q_num) - 1
                if 0 <= q_index < len(questions):
                    question = questions[q_index]
                    answer_text = answer_objects.get(str(answer_id), answer_id)
                    formatted.append(f'{question.title}: {answer_text}')
                else:
                    formatted.append(f'Question {q_num}: {answer_id}')

            return ', '.join(formatted)
        except (json.JSONDecodeError, AttributeError, ValueError):
            return str(obj.answers)
    formatted_answers.short_description = 'Answers'

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            try:
                # Find answers matching the search term
                matching_answers = Answer.objects.filter(
                    answer__icontains=search_term
                ).values_list('id', flat=True)

                # Build query for matching answers
                answer_queries = Q()
                for answer_id in matching_answers:
                    answer_queries |= Q(answers__contains=f'"{answer_id}"')

                # Combine with other search criteria
                queryset |= self.model.objects.filter(
                    Q(form__questions__title__icontains=search_term) |
                    Q(form__name__icontains=search_term) |
                    answer_queries
                )
            except ValueError:
                pass

        return queryset.distinct(), use_distinct


@admin.action(description="Export to Excel")
def export_to_excel(modeladmin, request, queryset):
    filename = "filtered_data.xlsx"
    base_fields = ["id", "form", "created_at"]
    data = []

    for obj in queryset:
        row = {field: getattr(obj, field) for field in base_fields}

        # بررسی اگر created_at زمان با timezone دارد و تبدیل به زمان بدون timezone
        if is_aware(row["created_at"]):
            row["created_at"] = make_naive(row["created_at"])

        try:
            answers_dict = json.loads(obj.answers) if isinstance(
                obj.answers, str) else obj.answers
            if isinstance(answers_dict, dict):
                row.update(answers_dict)
        except json.JSONDecodeError:
            pass

        data.append(row)

    df = pd.DataFrame(data)
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)

    return response


class SubmitAdmin(admin.ModelAdmin):
    list_filter = (FormFilter, AnswerFilter)
    actions = [export_to_excel]


admin.site.register(Form)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Submit, SubmitAdmin)
admin.site.register(Users)
