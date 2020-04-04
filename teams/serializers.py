from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CreateOnlyDefault, CurrentUserDefault
from .models import Team, Tag, Comment
from applications.models import Application

User = get_user_model()


class TeammateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'image')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class ChildCommentSerializer(serializers.ModelSerializer):
    author = TeammateSerializer(default=CreateOnlyDefault(CurrentUserDefault()))

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'team', 'author', 'body', 'created_at', 'updated_at']


class CommentSerializer(ChildCommentSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['child_comments_count'] = serializers.SerializerMethodField()
        self.fields['child_comments'] = self.__class__.__base__(many=True, read_only=True)

    def get_child_comments_count(self, obj):
        return obj.child_comments.count()


class TeamListSerializer(serializers.ModelSerializer):
    leader = TeammateSerializer(default=CreateOnlyDefault(CurrentUserDefault()))
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), pk_field=serializers.CharField(),
                                              required=False)
    likes = TeammateSerializer(read_only=True, many=True)
    image = serializers.ImageField(required=False, use_url=True)
    parent_comments = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id', 'tags', 'likes', 'like_count', 'leader', 'title', 'end_date', 'description', 'image', 'max_personnel',
            'current_personnel', 'comments_count', 'parent_comments', 'created_at', 'updated_at']

    def get_parent_comments(self, obj):
        parent_comments = obj.comments.filter(parent=None)
        serializer = CommentSerializer(parent_comments, many=True)
        return serializer.data

    def get_comments_count(self, obj):
        return obj.comments.count()


class TeamDetailSerializer(TeamListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_applied'] = serializers.SerializerMethodField()
        self.fields['application_status'] = serializers.SerializerMethodField()
        self.fields['chat_url'] = serializers.SerializerMethodField()
        # self.fields['kakao_chat_url'] = serializers.URLField()
        # self.fields['status'] = serializers.SerializerMethodField(method_name="get_status_display")

    def get_is_applied(self, team):
        user = self.context['request'].user
        if user.is_anonymous or not user.applications.filter(team=team).exists():
            return False
        return True

    def get_application_status(self, team):
        user = self.context['request'].user
        if user.is_anonymous:
            return ""
        try:
            return team.applications.get(applicant=user).get_status_display()
        except Application.DoesNotExist:
            return ""

    def get_chat_url(self, team):
        user = self.context['request'].user
        if user.is_anonymous:
            return ""
        if team.leader == user:
            return team.kakao_chat_url
        try:
            application = team.applications.get(applicant=user)
        except Application.DoesNotExist:
            return ""
        if application.status == 'approved':
            return team.kakao_chat_url
        return ""

class TeamListApplicationStatusSerializer(TeamListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application_status'] = serializers.SerializerMethodField()

    def get_application_status(self, team):
        user = self.context['request'].user
        try:
            return team.applications.get(applicant=user).get_status_display()
        except Application.DoesNotExist:
            return Application.STATUS_DEFAULT_DISPLAY
