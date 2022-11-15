from typing import List
import re

from django.db.models import F
from django.conf import settings
from rest_framework import serializers
from gtts.tts import gTTS

from .models import Project, Audio


class ProjectSerializer(serializers.ModelSerializer):
    model = Project
    fields = "__all__"


class AudioSerializer(serializers.ModelSerializer):
    model = Audio
    fields = "__all__"


class ProjectCreateReq(serializers.Serializer):
    """
    프로젝트 생성 요청시 데이터의 유효성 검증을 위한 직렬화
    """

    index = serializers.IntegerField()
    project_title = serializers.CharField(max_length=100)
    index = serializers.IntegerField()
    text = serializers.CharField()
    speed = serializers.BooleanField(default=False)


class ProjectService:
    """
    프로젝트(오디오) 생성 및 삭제 기능 클래스
    """

    def __init__(self) -> None:
        pass

    def create_preprocessed_text(
        self,
        text: List[str],
    ) -> List[list]:
        """
        받은 텍스트 데이터를 전처리 작업하는 함수

        문자열 1개를 담은 리스트를 매개변수로 받으면 해당 문자열을 '.!?'를 기준으로 문장을 나눕니다.
        """
        path = settings.MEDIA_URL
        pattern = r"([A-Za-z0-9가-힣][^\.!?]*[\.!?])"
        re_compile = re.compile(pattern)
        res = re_compile.findall(text[0])
        res.append(path)

        return res

    def create_audio_file(
        self,
        project_id: int,
    ) -> List[tuple]:
        """
        전처리된 텍스트와 오디오 파일 저장 경로를 받아 오디오 파일을 만드는 함수
        """
        result_list = []
        audio_list = Audio.objects.filter(project_id=project_id).order_by("index")

        for audio in audio_list:
            audio_info = gTTS(
                text=audio.text,
                lang="ko",
                slow=audio.speed,
            )
            audio_info.save(f"{project_id}({audio.index}).mp3")
            result_list.append((audio.id, audio.text))
        return result_list

    def create_project(
        self,
        index: int,
        title: str,
        text: List[str],
        speed: bool = False,
    ) -> None:
        """
        텍스트 데이터를 받아 각 전처리 과정을 거쳐 프로젝트(오디오)를 만드는 함수
        """

        created = Project.objects.create(
            index=index,
            title=title,
        )

        pre_texts = self.create_preprocessed_text(text=text)

        index = 0
        bulk_list = []
        for pre_text in pre_texts[:-2]:
            bulk_list.append(
                Audio(
                    project_id=created.id,
                    index=index,
                    text=pre_text,
                    speed=speed,
                )
            )
        Audio.objects.bulk_create(bulk_list)

        audio = self.create_audio_file()

        return audio

    def delete_project(
        self,
        title: str,
    ) -> tuple:
        deleted = Project.objects.get(title=title).delete()

        return ProjectSerializer(data=deleted).data


class AudioService:
    """
    프로젝트 텍스트의 CRUD 기능 클래스
    """

    def __init__(self) -> None:
        pass

    def get_project_text(
        self,
        project_id: int,
        page: int,
    ) -> list:
        audios = Audio.objects.filter(project_id=project_id).order_by("index")
        offset = (page - 1) * 10

        result = [audio for audio in audios[offset : offset + 10]]

        return AudioSerializer(data=result).data

    def update_project_text(
        self,
        project_id: int,
        index: int,
        text: str,
        speed: bool = False,
    ) -> dict:
        updated = Audio.objects.filter(project_id=project_id, index=index).update(
            index=index,
            text=text,
            speed=speed,
        )

        return AudioSerializer(data=updated).data

    def transmit_audio_file(
        self,
    ):
        pass

    def insert_project_text(
        self,
        project_id: int,
        index: int,
        text: str,
        speed: bool = False,
    ) -> dict:
        project_audios = Audio.objects.filter(project_id=project_id, index__gte=index)
        if project_audios:
            project_audios.index = F("index") + 1
            project_audios.save
        Audio.objects.create(project_id=project_id, index=index, text=text, speed=speed)
        return AudioSerializer(data=Audio.objects.all()).data

    def delete_project_text(
        self,
        project_id: int,
        index: int,
    ) -> dict:
        project_audios = Audio.objects.filter(project_id=project_id, index__gt=index)
        if project_audios:
            project_audios.index = F("index") - 1
            project_audios.save
        Audio.objects.get(project_id=project_id, index=index).delete()
        return AudioSerializer(data=Audio.objects.all()).data
