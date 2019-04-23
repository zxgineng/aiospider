from typing import Optional, Dict


class Response:
    def __init__(self, url: str, status: Optional[int], content: Optional[bytes], exception: Optional[Exception],
                 meta: Dict):
        self.status = status
        self.url = url
        self.content = content
        self.exception = exception
        self.meta = meta

        if status == 200:
            self.success = True
        else:
            self.success = False
