from datetime import datetime
from pathlib import Path
import unittest

from docx import Document
from django.core.management import BaseCommand, CommandError
from django.test.runner import DiscoverRunner


class RecordingTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = []
        self.test_records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)
        self.test_records.append((test.id(), "Успешно"))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_records.append((test.id(), "Ошибка проверки"))

    def addError(self, test, err):
        super().addError(test, err)
        self.test_records.append((test.id(), "Ошибка выполнения"))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.test_records.append((test.id(), f"Пропущен: {reason}"))

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.test_records.append((test.id(), "Ожидаемая ошибка"))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.test_records.append((test.id(), "Неожиданный успех"))


class RecordingDiscoverRunner(DiscoverRunner):
    def get_resultclass(self):
        return RecordingTestResult

    def run_suite(self, suite, **kwargs):
        self.recorded_result = super().run_suite(suite, **kwargs)
        return self.recorded_result


class Command(BaseCommand):
    help = "Запускает Django-тесты и сохраняет протокол в Word (.docx)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="reports/django-tests.docx",
            help="Путь для Word-документа (по умолчанию: reports/django-tests.docx).",
        )
        parser.add_argument(
            "labels",
            nargs="*",
            help="Необязательные метки тестов; без них запускаются все тесты проекта.",
        )

    def handle(self, *labels, output, **options):
        verbosity = options["verbosity"]
        runner = RecordingDiscoverRunner(verbosity=verbosity)
        failed_count = runner.run_tests(list(labels))
        result = runner.recorded_result

        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.write_report(output_path, result)

        self.stdout.write(
            self.style.SUCCESS(
                f"Отчёт записан: {output_path} "
                f"(тестов: {result.testsRun}, ошибок: {failed_count})."
            )
        )
        if failed_count:
            raise CommandError(f"Проверки завершились с ошибками: {failed_count}.")

    @staticmethod
    def write_report(path, result):
        document = Document()
        document.add_heading("Результаты Django-тестов", level=0)
        document.add_paragraph(
            f"Дата запуска: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )
        document.add_paragraph(f"Всего тестов: {result.testsRun}")
        document.add_paragraph(f"Успешно: {len(result.successes)}")
        document.add_paragraph(f"Ошибки проверок: {len(result.failures)}")
        document.add_paragraph(f"Ошибки выполнения: {len(result.errors)}")
        document.add_paragraph(f"Пропущено: {len(result.skipped)}")

        table = document.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        headers = table.rows[0].cells
        headers[0].text = "№"
        headers[1].text = "Тест"
        headers[2].text = "Результат"

        for index, (test_name, status) in enumerate(result.test_records, start=1):
            cells = table.add_row().cells
            cells[0].text = str(index)
            cells[1].text = test_name
            cells[2].text = status

        document.save(path)
