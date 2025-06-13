from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

class SignupView(APIView):
    @swagger_auto_schema(
        request_body=SignupSerializer,
        responses={201: "회원가입 성공", 400: "입력값 오류"}
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "username": user.username,
                "nickname": user.nickname,
            }, status=status.HTTP_201_CREATED)
         # 사용자 중복 같은 에러 발생 시 응답 통일
         
        if "username" in serializer.errors:
            return Response({
                "error": {
                    "code": "USER_ALREADY_EXISTS",
                    "message": "이미 가입된 사용자입니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # 그 외 일반 에러
        return Response({
            "error": {
                "code": "SIGNUP_FAILED",
                "message": "회원가입에 실패했습니다."
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: "로그인 성공", 400: "로그인 실패"}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "token": str(refresh.access_token)
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        return Response({
            "username": request.user.username,
            "nickname": request.user.nickname,
        })
