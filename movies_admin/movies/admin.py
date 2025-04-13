from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Genre, Filmwork, GenreFilmwork, PersonFilmwork, Person


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork

    autocomplete_fields = ('genre', 'film_work')


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork

    autocomplete_fields = ('person', 'film_work')


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    # Отображение полей в списке
    list_display = ('title', 'type', 'get_genres', 'creation_date', 'rating', 'created', 'modified')

    # Фильтрация в списке
    list_filter = ('type', 'creation_date', 'rating')

    # Поиск по полям
    search_fields = ('title', 'description', 'id', 'creation_date', 'rating')

    list_prefetch_related = ('genres',)

    def get_queryset(self, request):
        queryset = (
            super()
            .get_queryset(request)
            .prefetch_related(*self.list_prefetch_related)
        )
        return queryset

    def get_genres(self, obj):
        return ','.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = _('film_genres')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)

    # Отображение полей в списке
    list_display = ('name', 'created', 'modified')

    # Фильтрация в списке
    list_filter = ('name',)

    # Поиск по полям
    search_fields = ('name', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmworkInline,)

    # Отображение полей в списке
    list_display = ('full_name', 'created', 'modified')

    # Фильтрация в списке
    list_filter = ('full_name',)

    # Поиск по полям
    search_fields = ('full_name', 'id')
