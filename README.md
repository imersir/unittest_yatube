# Unittest для проекта Yatube
### Написание кода, для тестирования моделей, urls, views, forms в проекте Yatube.
Для запуска тестов
- Клонируй репозиторий на свой ПК (git clone https://github.com/imersir/unittest_yatube.git);
- Открой проект и создай виртуальное окружение (pyhton -m venv venv);
- Активируй виртуальное окружение (venv\Scripts\activate или source venv/bin/activate (Linux));
- Установи все зависимости (pip install -r requirements);
- Перейди в приложении yatube (cd yatube);
- Запусти тесты (python manage.py test)
- Флажок -v(--verbosity)(со значением от 0-3) выдаст более детализированный отчет о тестах (python manage.py test -v 1);
- Можно протестировать каждый тест-файл отдельно (python manage.py test yatube.tests.__имя файла для теста___).
