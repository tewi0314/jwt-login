import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
import time
from datetime import timedelta
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken



User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_signup_success(api_client):
    url = reverse('signup')  
    data = {
        "username": "testuser",
        "password": "12341234",
        "nickname": "테스트닉"
    }
    response = api_client.post(url, data, format='json')
    print("응답 데이터:", response.data)  
    assert response.status_code == 201
    assert response.data["username"] == "testuser"

@pytest.mark.django_db
def test_signup_duplicate_username(api_client):
    User.objects.create_user(username="testuser", password="12341234", nickname="기존닉")
    url = reverse('signup')
    data = {
        "username": "testuser",  # 중복
        "password": "12341234",
        "nickname": "중복닉"
    }
    response = api_client.post(url, data, format='json')
    print("응답 데이터:", response.data)  
    assert response.status_code == 400
    assert response.data["error"]["code"] == "USER_ALREADY_EXISTS"

@pytest.mark.django_db
def test_login_success(api_client):
    User.objects.create_user(username="loginuser", password="12345678", nickname="로그인닉") 
    url = reverse('login')
    data = {
        "username": "loginuser",
        "password": "12345678"
    }
    response = api_client.post(url, data, format='json')
    print("응답 데이터:", response.data)  
    assert response.status_code == 200
    assert "token" in response.data

@pytest.mark.django_db
def test_login_fail(api_client):
    User.objects.create_user(username="loginuser", password="12345678", nickname="로그인닉") 
    url = reverse('login')
    data = {
        "username": "loginuser",
        "password": "wrongpass"
    }
    response = api_client.post(url, data, format='json')
    print("응답 데이터:", response.data)  
    assert response.status_code == 401
    assert "error" in response.data


@pytest.mark.django_db
def test_token_not_found(api_client):
    url = reverse("profile")

    response = api_client.get(url)
    print("응답 데이터:", response.data)  
    assert response.status_code == 401
    assert response.data == {
        "error": {
            "code": "TOKEN_NOT_FOUND",
            "message": "토큰이 없습니다."
        }
    }

@pytest.mark.django_db
def test_invalid_token(api_client):
    url = reverse("profile")

    api_client.credentials(HTTP_AUTHORIZATION="Bearer fake.token.wrong")

    response = api_client.get(url)
    print("응답 데이터:", response.data)  
    assert response.status_code == 401
    assert response.data == {
    "error": {
        "code": "INVALID_TOKEN",
        "message": "토큰이 유효하지 않습니다."
    }
}

@pytest.mark.django_db
def test_token_expired(api_client):
    user = User.objects.create_user(username="expireuser", password="12345678")

    # 직접 만료된 토큰 생성
    token = AccessToken.for_user(user)
    token.set_exp(lifetime=timedelta(seconds=1))  # 짧은 만료 설정

    time.sleep(2)  # 만료될 때까지 대기

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    url = reverse("profile")
    response = api_client.get(url)

    print("응답 데이터:", response.data)
    assert response.status_code == 401
    assert response.data == {
        "error": {
            "code": "INVALID_TOKEN",
            "message": "토큰이 유효하지 않습니다."
        }
    }