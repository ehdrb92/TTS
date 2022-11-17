from typing import Union, List
import shutil
import os

from django.conf import settings
from django.db.models import QuerySet
from gtts.tts import gTTS

from ..models import Audio


class AudioFile:
    def __init__(self) -> None:
        pass

    def create_audio_file(
        self,
        project_id: int,
        path: str,
        audio_list: Union[QuerySet, List[Audio]],
    ) -> List[tuple]:
        """
        전처리된 텍스트와 오디오 파일 저장 경로를 받아 오디오 파일을 생성

        1. 데이터베이스에서 프로젝트에 해당하는 오디오 데이터 조회
        2. 오디오 파일을 하나씩 생성
        3. 결과 리스트 응답
        """
        self.directory = f".{path}{project_id}/"
        result_list = []
        audio_list = Audio.objects.filter(project_id=project_id).order_by("index")

        for audio in audio_list:
            audio_info = gTTS(
                text=audio.text,
                lang="ko",
                slow=audio.speed,
            )
            audio_info.save(f"{audio.index}.mp3")
            if not os.path.exists(self.directory):
                os.makedirs(self.directory)
            shutil.move(f"{audio.index}.mp3", f".{path}{project_id}/{audio.index}.mp3")
            result_list.append((audio.id, audio.text))
        return result_list

    def update_audio_file_text(
        self,
        project_id: int,
        text: str,
        speed: bool,
        index: int,
    ) -> bool:
        """
        해당하는 프로젝트와 오디오 파일을 찾아 새로운 수정된 오디오 파일로 고치는 작업을 수행

        1. 기존의 인덱스에 해당하는 오디오 파일을 삭제
        2. 해당 인덱스에 해당하는 새로운 오디오 파일 생성
        """
        self.directory = f".{settings.MEDIA_URL}{project_id}/{index}.mp3"
        os.remove(self.directory)

        audio_info = gTTS(
            text=text,
            lang="ko",
            slow=speed,
        )
        audio_info.save(f"{index}.mp3")
        shutil.move(f"{index}.mp3", self.directory)

        return True

    def insert_project_audio_file(
        self,
        project_id: int,
        index: int,
        text: str,
        speed: bool,
        len: int,
    ) -> bool:
        """
        프로젝트에 텍스트 추가 시 오디오 파일을 추가

        1. 생성될 오디오 파일의 인덱스와 이보다 큰 인덱스를 +1 처리(파일 이름 변경)
        2. 클라이언트가 원하는 위치의 인덱스에 오디오 파일 생성
        """
        for i in range(len - 2, index - 1, -1):
            os.rename(
                f".{settings.MEDIA_URL}{project_id}/{i}.mp3",
                f".{settings.MEDIA_URL}{project_id}/{i+1}.mp3",
            )

        audio_info = gTTS(
            text=text,
            lang="ko",
            slow=speed,
        )
        audio_info.save(f".{settings.MEDIA_URL}{project_id}/{index}.mp3")

        return True

    # TODO
    def transmit_audio_file(
        self,
    ):
        """
        생성된 오디오 파일을 전송
        """
        pass
