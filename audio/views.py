from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView

from .serializers import ProjectCreateReq, ProjectService

project_service = ProjectService()


class ProjectAPI(APIView):
    def post(self, request):
        params = request.data
        serializer = ProjectCreateReq(data=params)
        serializer.is_valid()
        created = project_service.create_project(**serializer.data)
        return JsonResponse({"res": created, "status": status.HTTP_201_CREATED})

    def delete(self, request):
        params = request.data
        deleted = project_service.delete_project(project_id=params["project_id"])
        return JsonResponse({"res": deleted, "status": status.HTTP_200_OK})


class AudioAPI(APIView):
    def post(request):
        pass

    def get(request):
        pass

    def put(request):
        pass

    def delete(request):
        pass
