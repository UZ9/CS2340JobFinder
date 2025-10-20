# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_jobapplication_notified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='notified_status',
            field=models.CharField(choices=[('applied', 'Applied'), ('review', 'Under Review'), ('interview', 'Interview'), ('offer', 'Offer Extended'), ('closed', 'Closed'), ('rejected', 'Rejected')], default='applied', help_text='Last status notified to applicant', max_length=20),
        ),
    ]
