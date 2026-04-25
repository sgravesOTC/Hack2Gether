import uuid
from django.db import migrations, models


def assign_tokens(apps, schema_editor):
    Profile = apps.get_model('account', 'Profile')
    for profile in Profile.objects.all():
        profile.checkin_token = uuid.uuid4()
        profile.save(update_fields=['checkin_token'])


def populate_short_codes(apps, schema_editor):
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    Profile = apps.get_model('account', 'Profile')
    used = set()
    for profile in Profile.objects.all():
        code = ''.join(random.choices(chars, k=8))
        while code in used:
            code = ''.join(random.choices(chars, k=8))
        used.add(code)
        profile.short_code = code
        profile.save(update_fields=['short_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_profile_image'),
    ]

    operations = [
        # Add checkin_token without unique so SQLite doesn't collide on existing rows
        migrations.AddField(
            model_name='profile',
            name='checkin_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        # Give each existing profile its own unique UUID
        migrations.RunPython(assign_tokens, migrations.RunPython.noop),
        # Now safe to enforce uniqueness and remove null
        migrations.AlterField(
            model_name='profile',
            name='checkin_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        # Add short_code without unique first
        migrations.AddField(
            model_name='profile',
            name='short_code',
            field=models.CharField(blank=True, default='', max_length=8),
            preserve_default=False,
        ),
        migrations.RunPython(populate_short_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='profile',
            name='short_code',
            field=models.CharField(blank=True, max_length=8, unique=True),
        ),
    ]
