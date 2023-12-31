# Generated by Django 3.0.7 on 2023-10-03 10:24

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('messenger', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('slug', models.SlugField(default=uuid.uuid1)),
                ('content', models.TextField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('msg_type', models.CharField(blank=True, choices=[('text', 'text'), ('image', 'image'), ('video', 'video'), ('audio', 'audio')], max_length=50)),
                ('is_archived', models.BooleanField(default=False)),
                ('read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver_msg', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender_msg', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
