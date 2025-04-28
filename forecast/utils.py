import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
from .models import WeatherForecast


def process_weather_data(file_path, user):
    # Чтение данных
    df = pd.read_csv(file_path, sep=';', decimal=',')

    # Преобразование данных
    df['Местное время'] = pd.to_datetime(df['Местное время'], format='%d.%m.%Y %H:%M')
    df = df.rename(columns={
        'Местное время': 'date',
        'T': 'temperature',
        'P': 'pressure',
        'U': 'humidity',
        'WW': 'precipitation'
    })

    # Оставляем только нужные колонки
    df = df[['date', 'temperature', 'pressure', 'humidity', 'precipitation']]

    # Сохранение в базу данных
    WeatherForecast.objects.all().delete()
    for _, row in df.iterrows():
        WeatherForecast.objects.create(
            user=user,
            date=row['date'],
            temp=row['temperature'],
            humidity=0,
            precipitation=0,
            location='',
            description='',
        )

    return df


def train_and_predict(df, user):
    # Подготовка данных для моделирования
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Создание признаков
    df['day_of_year'] = df['date'].dt.dayofyear
    df['hour'] = df['date'].dt.hour
    df['month'] = df['date'].dt.month

    # Кодирование осадков
    le = LabelEncoder()
    df['precipitation_encoded'] = le.fit_transform(df['precipitation'].fillna('Нет'))

    # Определение последней даты в данных
    last_date = df['date'].max()
    today = last_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Разделение на обучающую выборку
    train = df[df['date'] <= last_date]

    # Подготовка данных для обучения
    X = train[['day_of_year', 'hour', 'month']]
    y_temp = train['temperature']
    y_pressure = train['pressure']
    y_humidity = train['humidity']
    y_precip = train['precipitation_encoded']

    # Обучение моделей
    model_temp = RandomForestRegressor(n_estimators=100, random_state=42)
    model_temp.fit(X, y_temp)

    model_pressure = RandomForestRegressor(n_estimators=100, random_state=42)
    model_pressure.fit(X, y_pressure)

    model_humidity = RandomForestRegressor(n_estimators=100, random_state=42)
    model_humidity.fit(X, y_humidity)

    model_precip = RandomForestRegressor(n_estimators=100, random_state=42)
    model_precip.fit(X, y_precip)

    # Создание дат для прогноза (6 дней вперед)
    forecast_dates = [today + timedelta(days=i) for i in range(1, 7)]

    # Подготовка данных для прогноза
    forecast_data = []
    for date in forecast_dates:
        for hour in [0, 6, 12, 18]:  # Прогноз на 4 времени дня
            day_of_year = date.dayofyear
            forecast_hour = hour
            month = date.month

            forecast_data.append({
                'date': date.replace(hour=hour),
                'day_of_year': day_of_year,
                'hour': forecast_hour,
                'month': month
            })

    forecast_df = pd.DataFrame(forecast_data)
    X_forecast = forecast_df[['day_of_year', 'hour', 'month']]

    # Прогнозирование
    forecast_df['temperature'] = model_temp.predict(X_forecast)
    forecast_df['pressure'] = model_pressure.predict(X_forecast)
    forecast_df['humidity'] = model_humidity.predict(X_forecast)
    forecast_df['precipitation_encoded'] = model_precip.predict(X_forecast)
    forecast_df['precipitation'] = le.inverse_transform(
        forecast_df['precipitation_encoded'].round().astype(int)
    )

    # Удаляем старые прогнозы
    WeatherForecast.objects.all().delete()

    # Сохраняем новые прогнозы
    for _, row in forecast_df.iterrows():
        WeatherForecast.objects.create(
            user=user,
            forecast_date=row['date'],
            humidity=0,
            temp=row['temperature'],
            pressure=row['pressure'],
            precipitation=0,
            location='',
            description='',
        )

    return forecast_df