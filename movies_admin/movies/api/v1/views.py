from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields.array import ArrayField
from django.db.models import Q, Value
from django.db.models.fields import CharField
from django.db.models.functions.comparison import Coalesce
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        movies = self.model.objects.annotate(
            genres_list=ArrayAgg(
                'genres__name', distinct=True
            ),
            actors=Coalesce(
                ArrayAgg(
                    'persons__full_name', distinct=True, filter=Q(personfilmwork__role='actor')
                ),
                Value([], output_field=ArrayField(CharField()))
            ),
            directors=Coalesce(
                ArrayAgg(
                    'persons__full_name', distinct=True, filter=Q(personfilmwork__role='director')
                ),
                Value([], output_field=ArrayField(CharField()))
            ),
            writers=Coalesce(
                ArrayAgg(
                    'persons__full_name', distinct=True, filter=Q(personfilmwork__role='writer')
                ),
                Value([], output_field=ArrayField(CharField()))
            )
        ).values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'genres_list',
            'actors',
            'directors',
            'writers'
        )

        return movies

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        # Получение и обработка данных
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get(self, request, *args, **kwargs):
        # Получение и обработка данных
        return self.render_to_response(self.get_context_data())

    def get_object(self):
        movie_uuid = self.kwargs['pk']
        queryset = self.get_queryset().filter(id=movie_uuid)  # применяем ваш queryset с аннотациями
        return queryset.get()

    def get_context_data(self, **kwargs):
        movie = self.get_object()
        return movie
