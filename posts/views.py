from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer, UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework.response import Response
from rest_framework.views import APIView


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'

    def get_queryset(self):
        queryset = Post.objects.all()
        username = self.request.query_params.get("username")
        if username is not None:
            queryset = queryset.filter(author__username=username)
        return queryset


class UserViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 60 * 2))
    @method_decorator(vary_on_cookie)
    def list(self, request):
        content = {
            "user_feed": request.user.get_user_feed(),
        }
        return Response(content)
    filter_backends = [filters.OrderingFilter]
    permission_classes = [IsAdminUser]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    ordering_fields = ["username"]
    ordering = ["username"]


class CustomSearchFilter(filters.SearchFilter):
    def get_schema_fields(self, view, request):
        if request.query_params.get('title_only'):
            return ["title"]
        return super().get_search_fields(view, request)


class IsAuthorFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(author=request.user)
