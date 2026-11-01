"""Store what an enquiry was about as text rather than a foreign key.

Courses, plans and teachers no longer live in the database, so each
existing enquiry keeps the title of what it pointed at. This has to run
before those tables are dropped; their deletion migrations depend on it.
"""

from django.db import migrations, models


def copy_titles(apps, schema_editor):
    Enquiry = apps.get_model("leads", "Enquiry")
    enquiries = Enquiry.objects.select_related("course", "plan", "teacher")
    for enquiry in enquiries:
        enquiry.course_title = enquiry.course.title if enquiry.course else ""
        enquiry.plan_name = enquiry.plan.name if enquiry.plan else ""
        enquiry.teacher_name = enquiry.teacher.name if enquiry.teacher else ""
        enquiry.save(update_fields=["course_title", "plan_name", "teacher_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0003_course_badge_alter_course_is_featured"),
        ("leads", "0003_phone_required_email_optional"),
        ("pricing", "0002_alter_plan_currency"),
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="enquiry",
            name="course_title",
            field=models.CharField(
                blank=True,
                help_text="Set when the form was submitted from a course page.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="enquiry",
            name="plan_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="enquiry",
            name="teacher_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(copy_titles, migrations.RunPython.noop),
        migrations.RemoveField(model_name="enquiry", name="course"),
        migrations.RemoveField(model_name="enquiry", name="plan"),
        migrations.RemoveField(model_name="enquiry", name="teacher"),
        migrations.RenameField(
            model_name="enquiry", old_name="course_title", new_name="course"
        ),
        migrations.RenameField(
            model_name="enquiry", old_name="plan_name", new_name="plan"
        ),
        migrations.RenameField(
            model_name="enquiry", old_name="teacher_name", new_name="teacher"
        ),
    ]
