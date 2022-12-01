import json
from photo import Dict2Photo
from redis import Redis
import rq
from tasks import Train, download_photo

queue = rq.Queue('list0', connection=Redis.from_url('redis://'))
args = []
job = queue.enqueue(download_photo, "https://cdn.pixabay.com/photo/2020/02/06/09/39/summer-4823612_960_720.jpg", job_timeout=3000)


json_string = """[
    {
        "id": 55,
        "project": null,
        "image": "/media/1645439140321.jpg",
        "description": "описание",
        "status": "b",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 54,
        "project": null,
        "image": "/media/1645094634920_2a8nLj8.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 53,
        "project": null,
        "image": "/media/1645094861693_VZduW3e.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 52,
        "project": null,
        "image": "/media/1645094870660_LMdd9BR.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 51,
        "project": null,
        "image": "/media/1645342524209_UcqWCqU.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 50,
        "project": null,
        "image": "/media/1645376089971_rT2T9S3.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    },
    {
        "id": 49,
        "project": null,
        "image": "/media/1645428439862_udUZbXT.jpg",
        "description": "",
        "status": "n",
        "created_at": "21.02.2022 13:25",
        "is_ai_tag": false,
        "user": 13
    }
]"""

output = json.loads(json_string)
photo_list = list()
for obj in output:
    photo = Dict2Photo(obj)
    print(photo.image)
    photo_list.append(photo)

print(*photo_list)

