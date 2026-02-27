import django_filters
from django.db.models import Q

from Litra.models import Writers, Works, Facts, Quizz, Chats


class BaseCSVFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class WriterFilter(django_filters.FilterSet):
    century = BaseCSVFilter(field_name='century', lookup_expr='in')
    genre = django_filters.BaseInFilter(field_name='genre', lookup_expr='in')
    favorites = django_filters.BooleanFilter(method='favorites_filter')

    class Meta:
        model = Writers
        fields = ['century', 'genre']

    def favorites_filter(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorited_by=self.request.user).distinct()
            else:
                return queryset.none()
        return queryset


class WorksFilter(django_filters.FilterSet):
    period = BaseCSVFilter(field_name='period', lookup_expr='in')
    genre = django_filters.BaseInFilter(field_name='genre', lookup_expr='in')
    favorites = django_filters.BooleanFilter(method='favorites_filter')

    class Meta:
        model = Works
        fields = ['period', 'genre']

    def favorites_filter(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(favorited_by=self.request.user).distinct()
            else:
                return queryset.none()
        return queryset


class FactsFilter(django_filters.FilterSet):
    period = BaseCSVFilter(field_name='period', lookup_expr='in')
    category = django_filters.BaseInFilter(field_name='category', lookup_expr='in')
    liked = django_filters.BooleanFilter(method='likes_filter')
    type = django_filters.CharFilter(method='type_filter')
    search = django_filters.CharFilter(method='search_filter')
    featured = django_filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = Facts
        fields = ['type', 'category', 'period', 'search', 'featured', 'liked']

    def likes_filter(self, queryset, name, value):
        if value:
            if self.request.user.is_authenticated:
                return queryset.filter(likes=self.request.user).distinct()
            else:
                return queryset.none()
        return queryset

    def type_filter(self, queryset, name, value):
        types = value.split(',')
        q = Q()
        if 'writer' in types:
            q |= Q(writer__isnull=False)
        if 'work' in types:
            q |= Q(work__isnull=False)
        if 'general' in types:
            q |= Q(work__isnull=True, writer__isnull=True)
        if not q:
            return queryset
        return queryset.filter(q)

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(content__icontains=value) |
            Q(writer__full_name__icontains=value) |
            Q(work__title__icontains=value)
        )


class TestFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(method='get_type')
    difficulty = django_filters.BaseInFilter(field_name='difficulty', lookup_expr='in')
    search = django_filters.CharFilter(method='search_filter')

    class Meta:
        model = Quizz
        fields = ['type', 'difficulty', 'search']

    def get_type(self, queryset, name, value):
        types = value.split(',')
        q = Q()
        if 'writer' in types:
            q |= Q(writer__isnull=False)
        if 'work' in types:
            q |= Q(work__isnull=False)
        if 'general' in types:
            q |= Q(work__isnull=True, writer__isnull=True)
        if not q:
            return queryset
        return queryset.filter(q)

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(writer__full_name__icontains=value) |
            Q(work__title__icontains=value)
        )


