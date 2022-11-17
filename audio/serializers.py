from typing import List
import shutil

from django.db.models import F
from django.db import transaction
from django.conf import settings
from rest_framework import serializers

from .models import Project, Audio
from .utils.text_provider import TextPreprocess
from .utils.audio_provider import AudioFile


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = "__all__"


class ProjectCreateReq(serializers.Serializer):
    """
    프로젝트 생성 요청시 데이터의 유효성 검증과정 수행
    """

    index = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    index = serializers.IntegerField()
    text = serializers.CharField()
    speed = serializers.BooleanField(default=False)


class AudioCreateUpdateReq(serializers.Serializer):
    """
    오디오 생성 및 수정 요청시 데이터 유효성 검증과정 수행
    """

    text = serializers.CharField()
    speed = serializers.BooleanField()
    index = serializers.IntegerField()


class ProjectRepo:
    """
    프로젝트(오디오) 생성 및 삭제 기능 클래스
    """

    def __init__(self) -> None:
        self.text_service = TextPreprocess()
        self.audio_service = AudioFile()

    def create_project(
        self,
        index: int,
        title: str,
        text: List[str],
        speed: bool = False,
    ) -> bool:
        """
        텍스트 데이터를 받아 각 전처리 과정을 거쳐 프로젝트를 생성

        1. 데이터베이스에 프로젝트 데이터 생성
        2. 입력받은 텍스트를 전처리과정 수행
        3. 전처리된 텍스트를 문장 단위로 데이터베이스에 오디오 데이터 생성
        4. 생성된 오디오 데이터에 대한 오디오 파일을 생성
        """
        with transaction.atomic():
            created = Project.objects.create(
                index=index,
                title=title,
            )

            pre_texts = self.text_service.create_preprocessed_text(
                text=text,
            )

            audio_index = 0
            bulk_list = []
            for pre_text in pre_texts[:-1]:
                bulk_list.append(
                    Audio(
                        project_id=created.id,
                        index=audio_index,
                        text=pre_text,
                        speed=speed,
                    )
                )
                audio_index += 1
            Audio.objects.bulk_create(bulk_list)

            audio_list = Audio.objects.filter(project_id=created.id).order_by("index")
            self.audio_service.create_audio_file(
                project_id=created.id,
                path=pre_texts[-1],
                audio_list=audio_list,
            )
        return True

    def delete_project(
        self,
        project_id: str,
    ) -> bool:
        """
        프로젝트 삭제

        1. 데이터베이스에 프로젝트 데이터 삭제(해당 프로젝트를 참조하는 오디오 데이터가 함께 삭제)
        2. 프로젝트에 해당하는 오디오 파일 삭제
        """
        with transaction.atomic():
            deleted = Project.objects.get(id=project_id)
            deleted.delete()
            shutil.rmtree(f".{settings.MEDIA_URL}{project_id}")

        return True


class AudioRepo:
    """
    프로젝트 텍스트의 CRUD 기능 클래스
    """

    def __init__(self) -> None:
        self.audio_service = AudioFile()

    def get_project_text(
        self,
        project_id: int,
        page: int,
    ) -> list:
        """
        프로젝트의 페이지에 해당하는 텍스트를 조회

        1. 불러올 오디오 목록의 범위를 생성
        2. 범위에 해당하는 오디오 데이터를 index순으로 정렬하여 쿼리셋 형태로 변수에 저장
        3. 해당 변수를 직렬화하여 응답
        """
        offset = (page - 1) * 10
        audios = Audio.objects.filter(project_id=project_id).order_by("index")[offset : offset + 10]
        return AudioSerializer(audios, many=True).data

    def update_project_text(
        self,
        project_id: int,
        index: int,
        text: str,
        speed: bool = False,
    ) -> bool:
        """
        프로젝트의 텍스트를 수정

        1. 프로젝트에서 클라이언트가 요청하는 index의 데이터베이스 수정
        2. 생성된 오디오 파일 중 수정된 데이터에 해당하는 오디오 파일 수정
        """
        with transaction.atomic():
            Audio.objects.filter(project_id=project_id, index=index).update(
                index=index,
                text=text,
                speed=speed,
            )
            self.audio_service.update_audio_file_text(
                project_id=project_id,
                text=text,
                speed=speed,
                index=index,
            )
        return True

    def insert_text(
        self,
        project_id: int,
        index: int,
        text: str,
        speed: bool = False,
    ) -> bool:
        """
        프로젝트에 텍스트 추가

        1. 텍스트가 삽입될 경우 index값에 변화를 주어야할 데이터들의 index값 수정
        2. 삽입되는 텍스트 데이터 추가
        3. 삽입된 텍스트 데이터에 대한 오디오 파일 추가
        """
        with transaction.atomic():
            project_audios = Audio.objects.filter(project_id=project_id, index__gte=index)
            if project_audios:
                project_audios.index = F("index") + 1
                project_audios.save

            Audio.objects.create(project_id=project_id, index=index, text=text, speed=speed)

            len = Audio.objects.all().count()
            self.audio_service.insert_project_audio_file(
                project_id=project_id,
                index=index,
                text=text,
                speed=speed,
                len=len,
            )
        return True

    def delete_project_text(
        self,
        project_id: int,
        index: int,
    ) -> bool:
        """
        프로젝트의 텍스트를 삭제
        """
        project_audios = Audio.objects.filter(project_id=project_id, index__gt=index)
        if project_audios:
            project_audios.index = F("index") - 1
            project_audios.save
        Audio.objects.get(project_id=project_id, index=index).delete()
        return True
