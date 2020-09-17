from flask import render_template, redirect, url_for, flash, Blueprint
from sqlalchemy import and_, not_
from P2MT_App import db
from P2MT_App.models import InterventionLog
from P2MT_App.main.utilityfunctions import printLogEntry
from P2MT_App.main.referenceData import getInterventionId
from P2MT_App.interventionInfo.interventionInfo import downloadInterventionLog
from P2MT_App.learningLab.learningLab import deleteLearningLabFromGoogleCalendar

interventionInfo_bp = Blueprint("interventionInfo_bp", __name__)


@interventionInfo_bp.route("/interventionlog")
def displayInterventionLogs():
    printLogEntry("Running displayInterventionLogs()")
    InterventionLogs = InterventionLog.query.filter(
        InterventionLog.parentNotification != None
    ).order_by(InterventionLog.endDate.desc())

    return render_template(
        "interventionlog.html",
        title="Intervention Log",
        InterventionLogs=InterventionLogs,
    )


@interventionInfo_bp.route("/interventionlog/<int:log_id>/delete", methods=["POST"])
def delete_InterventionLog(log_id):
    log = InterventionLog.query.get_or_404(log_id)
    LogDetails = f"{(log_id)} {log.chattStateANumber} {log.staffID}"
    printLogEntry("Running delete_InterventionLog(" + LogDetails + ")")
    # Note: deleting learning lab interventions also deletes all associated class attendance logs
    # and learning lab class schedules from their respective tables
    # However, it doesn't automatically delete learning lab events from Google Calendar
    # In order to delete learning labs from Google Calendar:
    # Check whether the intervention is a learning lab
    # If so, delete the learning lab from the schedule in Google Calendar
    learningLabInterventionID = getInterventionId("Academic Behavior")
    if log.intervention_id == learningLabInterventionID:
        deleteLearningLabFromGoogleCalendar(log.id)
    db.session.delete(log)
    db.session.commit()
    flash("Intervention log has been deleted!", "success")
    return redirect(url_for("interventionInfo_bp.displayInterventionLogs"))


@interventionInfo_bp.route("/interventionlog/download")
def download_InterventionLog():
    printLogEntry(
        "download_Daildownload_InterventionLogyAttendanceLog() function called"
    )
    return downloadInterventionLog()
