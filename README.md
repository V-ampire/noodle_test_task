## Запуск сервиса

### Установить переменные окружения в файле `.env`:
```
PROJECT_DIR=/app
DEBUG=
VK_ACCESS_TOKEN=
DATABASE=postgres
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LOG_LEVEL=ERROR
```

### Выполнить:
```
$ make build
$ make up
```

## Запустить интерфейс для тестирования
```
$ locust
```

## Информация о группе
```
/vk/group/<group_id>/
```

## Регулярное обновление
Информация о сохраненных группах обновляется раз в сутки (реализовано с помощью `Celery Beat`)


![image](https://github.com/V-ampire/noodle_test_task/blob/master/test.png)

