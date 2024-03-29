from rest_framework import viewsets, permissions, filters, mixins
from django.shortcuts import get_object_or_404
from posts.models import Post, Group, Follow
from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer,
    FollowSerializer)
from rest_framework.pagination import LimitOffsetPagination
from .permissions import AuthorOrReadOnly


class ListCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        return post.comments.select_related('author').all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        author = self.request.user
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=author, post=post)


class FollowViewSet(ListCreateViewSet):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username', 'user__username')

    def get_queryset(self):
        new_queryset = Follow.objects.select_related(
            'user', 'following').filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
