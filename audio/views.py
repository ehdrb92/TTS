from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from .serializers import ProjectCreateReq, AudioCreateUpdateReq, ProjectRepo, AudioRepo

project_repository = ProjectRepo()
audio_repository = AudioRepo()


class ProjectAPI(APIView):
    def post(self, request):
        params = request.data
        serializer = ProjectCreateReq(data=params)
        serializer.is_valid()
        project_repository.create_project(**serializer.data)
        return JsonResponse({"status": status.HTTP_201_CREATED})

    def delete(self, request):
        params = request.data
        project_repository.delete_project(project_id=params["project_id"])
        return JsonResponse({"status": status.HTTP_200_OK})


class AudioAPI(APIView):
    def post(self, request, project_id):
        params = request.data
        serizlizer = AudioCreateUpdateReq(data=params)
        serizlizer.is_valid()
        audio_repository.insert_text(project_id=project_id, **serizlizer.data)
        return JsonResponse({"status": status.HTTP_201_CREATED})

    def get(self, request):
        project_id = int(request.GET.get("project_id"))
        page = int(request.GET.get("page", 1))
        data = audio_repository.get_project_text(project_id=project_id, page=page)
        return JsonResponse({"res": data, "status": status.HTTP_200_OK})

    def put(self, request, project_id, index):
        params = request.data
        serizlizer = AudioCreateUpdateReq(data=params)
        serizlizer.is_valid()
        audio_repository.update_project_text(project_id=project_id, index=index, **serizlizer.data)
        return JsonResponse({"status": status.HTTP_200_OK})

    def delete(self, request, project_id, index):
        audio_repository.delete_project_text(project_id=project_id, index=index)
        return JsonResponse({"status": status.HTTP_200_OK})
