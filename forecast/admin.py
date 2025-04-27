from django.contrib import admin
from .models import WeatherForecast


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = ('date', 'location', 'temp', 'humidity', 'precipitation', 'description')
    list_display_links = ('date', 'location')  # Кликабельные поля
    list_editable = ('temp', 'humidity')  # Редактируемые прямо в списке

    # Фильтры справа
    list_filter = ('location', 'date')

    # Поиск
    search_fields = ('location', 'description')
    search_help_text = 'Поиск по местоположению или описанию'

    # Разделение на группы в форме редактирования
    fieldsets = (
        ('Основные данные', {
            'fields': ('date', 'location'),
            'description': 'Дата и местоположение прогноза'
        }),
        ('Погодные параметры', {
            'fields': ('temp', 'humidity', 'precipitation'),
            'classes': ('wide',)  # Широкое поле
        }),
        ('Дополнительно', {
            'fields': ('description',),
            'classes': ('collapse',)  # Свертываемая секция
        }),
    )

    # Настройки дат
    date_hierarchy = 'date'

    # Действия над несколькими записями
    actions = ['make_clear_description']

    @admin.action(description="Очистить описания у выбранных прогнозов")
    def make_clear_description(self, request, queryset):
        queryset.update(description='')