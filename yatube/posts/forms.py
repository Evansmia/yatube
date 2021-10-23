from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': ('Текст поста'),
                  'group': ('Группа')}
        help_texts = {'text':
                      ('Введите текст, '
                       'который будет отображаться на странице пользователя.'),
                      'group':
                      ('Выберете группу, '
                       'в которой будет отображаться этот пост.'), }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': ('Комментарий')}
