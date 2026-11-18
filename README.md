# Замер скорости скачивания

Консольный скрипт на Python скачивает указанный HTTP(S)-адрес **10 раз подряд**. Следующий запрос начинается только после полного чтения ответа на предыдущий. Скрипт считает фактически полученные байты, поэтому заголовок `Content-Length` ему не нужен.

## Требования

Python 3.10 или новее. Сторонние пакеты не нужны.

## Запуск

В PowerShell из папки проекта:

```powershell
python speed_test.py "https://example.com/large-image.jpg"
```

В Bash на Linux или macOS:

```bash
./speed_test.py "https://example.com/large-image.jpg"
```

В Git Bash на Windows можно запустить скрипт через установленный Python:

```bash
python speed_test.py "https://example.com/large-image.jpg"
```

Если в Git Bash доступна команда `python3`, работает и прямой запуск `./speed_test.py`.

При необходимости можно изменить тайм-аут сокета для каждого запроса (по умолчанию 60 секунд):

```powershell
python speed_test.py "https://example.com/large-image.jpg" --timeout 120
```

Пример вывода:

```text
Requests: 10
Average request time: 0.420 s
Downloaded: 104857600 bytes (100.000 MiB)
Download speed: 23.810 MiB/s
```

`Average request time` — среднее время полного запроса. `Downloaded` — общий объём данных за 10 запросов. `Download speed` = общий объём / суммарное время запросов. Скорость выводится в **MiB/s** (мебибайтах в секунду; 1 MiB = 1 048 576 байт). В замер входят подключение и ожидание ответа сервера, поэтому результат зависит также от выбранного адреса и сервера. Если запрос завершится ошибкой, скрипт сообщит её и вернёт ненулевой код выхода.

## Проверка

```powershell
python -m unittest -v
```
