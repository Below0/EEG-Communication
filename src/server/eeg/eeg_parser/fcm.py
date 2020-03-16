import requests
import json

# with open("./config.json") as f:
#     secrets = json.loads(f.read())


def send_fcm_notification(ids, title, body):
    url = 'https://fcm.googleapis.com/fcm/send'

    # 인증 정보(서버 키)를 헤더에 담아 전달
    headers = {
        'Authorization': '', ## need Firebase KEY
        'Content-Type': 'application/json; UTF-8',
    }

    # 보낼 내용과 대상을 지정
    content = {
        'registration_ids': ids,
        'notification': {
            'title': title,
            'body': body
        }
    }

    requests.post(url, data=json.dumps(content), headers=headers)
