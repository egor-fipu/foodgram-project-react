from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from foodgram.pagination import CustomPageNumberPaginator
from .models import Follow
from .serializers import FollowSerializer, ReadyFollowSerializer

User = get_user_model()


class FollowApiView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, pk):
        serializer = FollowSerializer(
            data={'user': request.user.id, 'following': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        get_object_or_404(
            Follow, user=request.user, following=get_object_or_404(User, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListFollowViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ReadyFollowSerializer
    pagination_class = CustomPageNumberPaginator

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
