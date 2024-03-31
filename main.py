import base64
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
import datetime
import jwt
from datetime import datetime, timedelta
from urllib.parse import quote
import requests
import os

# 네이버웍스 API PRIVATE KEY
PRIVATE_KEY = ""

# 네이버 웍스 채널 ID
CHANNEL_ID = ""

# 네이버 웍스 봇 ID
BOT_ID = ""

# 네이버 웍스 Client ID
CLIENT_ID = ""

# 네이버 웍스 Client Secret
CLIENT_SECRET = ""


# 네이버 웍스 API 서버 토큰 발급
def get_server_token():
    headers = {
        "alg": "RS256",
        "typ": "JWT"
    }
    iat = datetime.utcnow()
    exp = iat + timedelta(minutes=10)

    assertion = jwt.encode({
        "iss": "cv821ebW6avTOS7tzMcf",
        "sub": "y3fln.serviceaccount@potatowoong.by-works.com",
        "iat": iat,
        "exp": exp
    }, PRIVATE_KEY, algorithm="RS256", headers=headers)

    return assertion


# 네이버 웍스 API ACCESS TOKEN 발급
def get_access_token():
    access_token_data = {'assertion': get_server_token(),
                         'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                         'client_id': CLIENT_ID,
                         'client_secret': CLIENT_SECRET,
                         'scope': 'bot'}
    req = requests.post('https://auth.worksmobile.com/oauth2/v2.0/token', data=access_token_data)
    return req.json().get('access_token')


# 커밋 메세지 생성
def get_commit_message(arr):
    message = [{
        "type": "text",
        "text": arr[0],
        "weight": "bold",
        "size": "md",
        "align": "start",
        "wrap": True
    }, ]  # 커밋 설명
    if len(arr) > 1:
        for description in arr[2:]:
            message.append({
                "type": "text",
                "text": description,
                "weight": "regular",
                "size": "xs",
                "align": "start",
                "margin": "sm",
                "wrap": True
            })
    return message


# 네이버 웍스 채널 메세지 생성
def get_chat_message(repository, commit_summarize, commit_message, branch_name, pushed_by, commit_sha, commit_link):
    return {
        "content": {
            "type": "flex",
            "altText": f'[{repository}]\n {commit_summarize}',
            "contents": {
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "size": "mega",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": repository,
                                    "size": "lg",
                                    "color": "#00c73c",
                                    "weight": "bold"
                                }
                            ],
                            "backgroundColor": "#ffffff"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": commit_message,
                                    "margin": "xl"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Branch",
                                                    "size": "sm",
                                                    "color": "#858f89",
                                                    "flex": 3,
                                                    "margin": "md"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": branch_name.split('/')[-1],
                                                    "size": "sm",
                                                    "margin": "md",
                                                    "flex": 5
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "layout": "baseline",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "Author",
                                                    "size": "sm",
                                                    "color": "#858f89",
                                                    "flex": 3,
                                                    "margin": "md"
                                                },
                                                {
                                                    "type": "text",
                                                    "text": pushed_by,
                                                    "size": "sm",
                                                    "margin": "md",
                                                    "flex": 5
                                                }
                                            ],
                                            "margin": "sm"
                                        },
                                        {
                                            "layout": "baseline",
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "text": "Commit",
                                                    "type": "text",
                                                    "flex": 3,
                                                    "margin": "md",
                                                    "size": "sm",
                                                    "color": "#858f89"
                                                },
                                                {
                                                    "text": commit_sha,
                                                    "action": {
                                                        "type": "uri",
                                                        "label": "",
                                                        "uri": commit_link,
                                                    },
                                                    "type": "text",
                                                    "flex": 5,
                                                    "margin": "md",
                                                    "size": "sm",
                                                    "decoration": "underline",
                                                }
                                            ],
                                            "margin": "sm"
                                        }
                                    ],
                                    "margin": "xxl",
                                    "width": "260px",
                                    "alignItems": "center",
                                    "paddingAll": "6px"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }


if __name__ == '__main__':
    access_token = get_access_token()  # ACCESS TOKEN

    branch_name = os.environ['BRANCH_NAME']  # 브랜치 이름
    commit_arr = os.environ['COMMIT_MESSAGE'].split('\n')  # 커밋 배열
    commit_message = get_commit_message(commit_arr)  # 커밋 메세지
    pushed_by = os.environ['PUSHED_BY']  # 푸시한 사람
    repository = os.environ['REPOSITORY'].split('/')[-1]  # 레포지토리 이름
    commit_sha = os.environ['COMMIT_SHA'][: 6]  # 커밋 SHA
    commit_link = os.environ['COMMIT_LINK']  # 커밋 링크

    chat_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    chat_data = get_chat_message(repository, commit_arr[0], commit_message, branch_name.split('/')[-1], pushed_by,
                            commit_sha, commit_link)

    # 메세지 전송
    requests.post(f'https://www.worksapis.com/v1.0/bots/{BOT_ID}/channels/{CHANNEL_ID}/messages', headers=chat_headers, json=chat_data)
