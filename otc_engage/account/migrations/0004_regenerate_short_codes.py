import random
import string
from django.db import migrations


def regenerate_short_codes(apps, schema_editor):
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
        ('account', '0003_profile_checkin_fields'),
    ]

    operations = [
        migrations.RunPython(regenerate_short_codes, migrations.RunPython.noop),
    ]
