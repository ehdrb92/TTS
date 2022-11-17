from typing import List
import re

from django.conf import settings


class TextPreprocess:
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
