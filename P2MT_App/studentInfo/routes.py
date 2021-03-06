from flask import render_template, redirect, request, url_for, flash, Blueprint
from flask_login import login_required
from P2MT_App import db
from P2MT_App.models import (
    Student,
    DailyAttendanceLog,
    ClassAttendanceLog,
    ClassSchedule,
    InterventionLog,
    Parents,
)
from P2MT_App.dailyAttendance.dailyAttendance import add_DailyAttendanceLog
from P2MT_App.interventionInfo.interventionInfo import (
    add_InterventionLog,
    sendInterventionEmail,
)
from P2MT_App.interventionInfo.forms import addInterventionLogForm
from P2MT_App.dailyAttendance.forms import addDailyAttendanceForm
from P2MT_App.main.referenceData import getInterventionTypes
from P2MT_App.main.utilityfunctions import printLogEntry
from P2MT_App.p2mtAdmin.p2mtAdmin import downloadStudentList
from datetime import datetime

studentInfo_bp = Blueprint("studentInfo_bp", __name__)


@studentInfo_bp.route("/students/download")
@login_required
def download_StudentList():
    printLogEntry("download_StudentList() function called")
    return downloadStudentList()


@studentInfo_bp.route("/students", methods=["GET", "POST"])
@login_required
def displayStudents():
    printLogEntry("Running displayStudents()")
    dailyAttendanceForm = addDailyAttendanceForm()
    interventionForm = addInterventionLogForm()
    interventionForm.interventionType.choices = getInterventionTypes()
    students = Student.query.order_by(
        Student.yearOfGraduation.asc(), Student.lastName.asc()
    )
    if "submitDailyAttendance" in request.form:
        if dailyAttendanceForm.validate_on_submit():
            printLogEntry("Running dailyAttendanceForm")
            add_DailyAttendanceLog(
                dailyAttendanceForm.chattStateANumber.data,
                dailyAttendanceForm.absenceDateStart.data,
                dailyAttendanceForm.absenceDateEnd.data,
                dailyAttendanceForm.attendanceCode.data,
                dailyAttendanceForm.comment.data,
            )
            db.session.commit()
            flash("Daily attendance log has been added!", "success")
            printLogEntry("Completed add_DailyAttendanceLog.  Redirecting to students")
            return redirect(url_for("studentInfo_bp.displayStudents"))

    if "submitIntervention" in request.form:
        if interventionForm.validate_on_submit():
            printLogEntry("Running interventionForm")
            interventionLog = add_InterventionLog(
                interventionForm.chattStateANumber.data,
                int(interventionForm.interventionType.data),
                int(interventionForm.interventionLevel.data),
                interventionForm.startDate.data,
                interventionForm.endDate.data,
                interventionForm.comment.data,
                parentNotification=datetime.utcnow(),
            )
            db.session.commit()
            sendInterventionEmail(
                interventionForm.chattStateANumber.data,
                int(interventionForm.interventionType.data),
                int(interventionForm.interventionLevel.data),
                interventionForm.startDate.data,
                interventionForm.endDate.data,
                interventionForm.comment.data,
            )
            print("new intervention log ID:", interventionLog.id)
            flash("Intervention log has been added!", "success")
            printLogEntry("Completed add_InterventionLog.  Redirecting to students")
            return redirect(url_for("studentInfo_bp.displayStudents"))

    if request.method == "GET":
        return render_template(
            "students.html",
            title="Students",
            students=students,
            dailyAttendanceForm=dailyAttendanceForm,
            interventionForm=interventionForm,
        )


@studentInfo_bp.route("/students/info", methods=["GET", "POST"])
@login_required
def displayStudentInfo():
    """Display student info page with the following info:
    Student name, email, house, year of graduation
    Parent info
    Absences
    Class attendance (when not present)
    Interventions
    Learning labs
    Class schedule
    """
    printLogEntry("Running displayStudentInfo()")
    chattStateANumber = request.args["chattStateANumber"]
    print("chattStateANumber = ", chattStateANumber)

    students = Student.query.filter(
        Student.chattStateANumber == chattStateANumber
    ).order_by(Student.yearOfGraduation.asc(), Student.lastName.asc())

    parents = (
        Parents.query.join(Student)
        .filter(Student.chattStateANumber == chattStateANumber)
        .order_by(Student.lastName.asc())
    )

    DailyAttendanceLogs = DailyAttendanceLog.query.filter(
        DailyAttendanceLog.chattStateANumber == chattStateANumber
    ).order_by(DailyAttendanceLog.absenceDate.desc())

    classAttendanceFixedFields = (
        ClassAttendanceLog.query.filter(ClassAttendanceLog.attendanceCode != "P")
        .filter(ClassSchedule.chattStateANumber == chattStateANumber)
        .join(ClassSchedule)
        .join(ClassSchedule.Student)
        .order_by(
            Student.lastName,
            ClassAttendanceLog.classDate.desc(),
            ClassSchedule.className,
        )
        .all()
    )

    InterventionLogs = InterventionLog.query.filter(
        InterventionLog.parentNotification != None,
        InterventionLog.chattStateANumber == chattStateANumber,
    ).order_by(InterventionLog.endDate.desc())

    ClassSchedules = ClassSchedule.query.filter(
        ClassSchedule.learningLab == False,
        ClassSchedule.chattStateANumber == chattStateANumber,
    ).order_by(ClassSchedule.chattStateANumber.desc())

    LearningLabSchedules = (
        db.session.query(ClassSchedule)
        .join(InterventionLog)
        .join(Student)
        .filter(
            ClassSchedule.learningLab == True,
            ClassSchedule.chattStateANumber == chattStateANumber,
        )
        .order_by(InterventionLog.endDate.desc(), Student.lastName.asc())
    ).all()

    return render_template(
        "studentinfo.html",
        title="Student Info",
        students=students,
        parents=parents,
        DailyAttendanceLogs=DailyAttendanceLogs,
        classAttendanceFixedFields=classAttendanceFixedFields,
        InterventionLogs=InterventionLogs,
        ClassSchedules=ClassSchedules,
        LearningLabSchedules=LearningLabSchedules,
    )
