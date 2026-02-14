from huey.contrib.djhuey import task
from django.core.mail import send_mail
from django.conf import settings

from apps.verifications.models import SuspiciousReport

@task()
def send_report_notification(report_id: str):
    """
    Asynchronously sends an email notification to admins about a new suspicious report.
    """
    try:
        report = SuspiciousReport.objects.get(id=report_id)
        subject = f"New Suspicious Document Report: {report.get_report_type_display()}"
        message = f"""
        A new suspicious document report has been submitted.

        Document Hash: {report.document_hash}
        Report Type: {report.get_report_type_display()}
        Reason: {report.reason}
        Reporter Email: {report.reporter_email or 'N/A'}

        Please review the report in the admin dashboard.
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL], # Assumes ADMIN_EMAIL is in settings
            fail_silently=False,
        )
    except SuspiciousReport.DoesNotExist:
        # Handle case where report is deleted before task runs
        pass
