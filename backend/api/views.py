import os
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Импорт вашей главной функции сравнения (лежит в корне backend)
from run_app_back import user_process_comparison


@csrf_exempt
def compare_documents(request):
    """Принимает файлы от React, запускает пайплайн и возвращает JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается. Используйте POST.'}, status=405)

    old_doc = request.FILES.get('old_doc')
    new_doc = request.FILES.get('new_doc')

    if not old_doc or not new_doc:
        return JsonResponse({'error': 'Оба файла (old_doc и new_doc) обязательны'}, status=400)

    fs = FileSystemStorage(location='tmp_uploads/')
    old_filename = fs.save(old_doc.name, old_doc)
    new_filename = fs.save(new_doc.name, new_doc)

    old_path = fs.path(old_filename)
    new_path = fs.path(new_filename)

    try:
        result = user_process_comparison(old_path, new_path)

        if isinstance(result, dict) and "error" in result:
            return JsonResponse({'error': result["error"]}, status=500)

        return JsonResponse(result, status=200)

    except Exception as e:
        return JsonResponse({'error': f"Ошибка сервера: {str(e)}"}, status=500)

    finally:
        if os.path.exists(old_path):
            os.remove(old_path)
        if os.path.exists(new_path):
            os.remove(new_path)


@csrf_exempt
def download_report(request, filename):
    """Позволяет скачать сгенерированный DOCX-файл."""
    file_path = os.path.join(settings.BASE_DIR, filename)

    if os.path.exists(file_path):
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    raise Http404("Файл отчета не найден")