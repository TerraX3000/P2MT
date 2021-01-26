from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import login_required
from P2MT_App import db
from P2MT_App.models import (
    DailyAttendanceLog,
    ClassAttendanceLog,
    ClassSchedule,
    Student,
)
from P2MT_App.main.utilityfunctions import printLogEntry
from P2MT_App.dailyAttendance.dailyAttendance import downloadDailyAttendanceLog

dailyAttendance_bp = Blueprint("dailyAttendance_bp", __name__)


@dailyAttendance_bp.route("/dailyattendancelog")
@login_required
def displayDailyAttendanceLogs():
    printLogEntry("displayDailyAttendanceLogs() function called")
    DailyAttendanceLogs = DailyAttendanceLog.query.order_by(
        DailyAttendanceLog.absenceDate.desc()
    )
    return render_template(
        "dailyattendancelog.html",
        title="Absence Log",
        DailyAttendanceLogs=DailyAttendanceLogs,
    )


@dailyAttendance_bp.route("/dailyattendancelog/<int:log_id>/delete", methods=["POST"])
@login_required
def delete_DailyAttendanceLog(log_id):
    log = DailyAttendanceLog.query.get_or_404(log_id)
    LogDetails = f"{(log_id)} {log.chattStateANumber} {log.staffID}"
    printLogEntry("Running delete_DailyAttendanceLog(" + LogDetails + ")")
    db.session.delete(log)
    db.session.commit()
    flash("Daily attendance log has been deleted!", "success")
    return redirect(url_for("dailyAttendance_bp.displayDailyAttendanceLogs"))


@dailyAttendance_bp.route("/dailyattendancelog/download")
@login_required
def download_DailyAttendanceLog():
    printLogEntry("download_DailyAttendanceLog() function called")
    return downloadDailyAttendanceLog()


@dailyAttendance_bp.route("/classabsencelog")
@login_required
def displayClassAbsenceLog():
    printLogEntry("displayClassAbsenceLog() function called")
    ClassAbsenceLogs = DailyAttendanceLog.query.order_by(
        DailyAttendanceLog.absenceDate.desc()
    )

    classAttendanceFixedFields = (
        ClassAttendanceLog.query.filter(ClassAttendanceLog.attendanceCode == "U")
        .join(ClassSchedule)
        .join(ClassSchedule.Student)
        .order_by(
            ClassAttendanceLog.classDate.desc(),
            Student.lastName,
            ClassSchedule.className,
        )
        .all()
    )

    return render_template(
        "classabsencelog.html",
        title="Class Absence Log",
        DailyAttendanceLogs=ClassAbsenceLogs,
        classAttendanceFixedFields=classAttendanceFixedFields,
    )
