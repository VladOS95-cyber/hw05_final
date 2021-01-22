from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Класс для создания новой публикации пользователем."""
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    """Класс для написания комментариев к постам."""
    class Meta:
        model = Comment
        fields = ('text',)
