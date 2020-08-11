from flask import render_template, flash, request, Blueprint
from P2MT_App import db
from P2MT_App.main.utilityfunctions import printLogEntry
from P2MT_App.models import Student, ClassSchedule, ClassAttendanceLog
from P2MT_App.classAttendance.forms import (
    updateClassAttendanceForm,
    updateStudentAttendanceForm,
)
from P2MT_App.tmiTeacherReview.forms import updateTmiTeacherReviewForm
from P2MT_App.main.referenceData import getTeachers, getClassNames
from datetime import date
from P2MT_App.tmiTeacherReview.tmiTeacherReview import test_setAttendanceForTmiTesting

tmiTeacherReview_bp = Blueprint("tmiTeacherReview_bp", __name__)


@tmiTeacherReview_bp.route("/tmiteacherreview", methods=["GET", "POST"])
def displayTmiTeacherReview():
    printLogEntry("Running displayTmiTeacherReview()")
    test_setAttendanceForTmiTesting(date(2020, 8, 5), date(2020, 8, 11))
    tmiTeacherReviewForm = updateTmiTeacherReviewForm()
    tmiTeacherReviewForm.teacherName.choices = getTeachers()

    print(
        "tmiTeacherReviewForm.updateFiltersFlag.data =",
        tmiTeacherReviewForm.updateFiltersFlag.data,
    )

    print("request.method =", request.method)

    if tmiTeacherReviewForm.validate_on_submit():
        print(
            "tmiTeacherReviewForm.validate_on_submit() =",
            tmiTeacherReviewForm.validate_on_submit(),
        )
    print("tmiTeacherReviewForm.errors =", tmiTeacherReviewForm.errors)

    if request.method == "GET":

        tmiTeacherReviewForm.teacherName.default = tmiTeacherReviewForm.teacherName.data
        tmiTeacherReviewForm.updateFiltersFlag.data = ""

    if tmiTeacherReviewForm.validate_on_submit():

        # Update default values for teacher name and class name
        tmiTeacherReviewForm.teacherName.default = tmiTeacherReviewForm.teacherName.data

        print(
            "tmiTeacherReviewForm.updateFiltersFlag.data =",
            tmiTeacherReviewForm.updateFiltersFlag.data,
        )

        # Update database with attendance updates
        if (
            tmiTeacherReviewForm.classMembers
            and tmiTeacherReviewForm.updateFiltersFlag.data != "updated"
        ):
            print("Class attendance submitted")
            print(len(tmiTeacherReviewForm.classMembers.data))
            for studentForm in tmiTeacherReviewForm.classMembers.data:
                if studentForm["updateFlag"] == "updated":
                    log_id = studentForm["log_id"]
                    print("log_id = ", log_id)
                    classAttendanceLog = ClassAttendanceLog.query.get_or_404(log_id)
                    classAttendanceLog.attendanceCode = studentForm["attendanceCode"]
                    classAttendanceLog.comment = studentForm["comment"]
                    if classAttendanceLog.attendanceCode == "P":
                        classAttendanceLog.assignTmi = False
                    if classAttendanceLog.attendanceCode == "E":
                        classAttendanceLog.assignTmi = studentForm["assignTmi"]
                    if classAttendanceLog.attendanceCode == "T":
                        classAttendanceLog.assignTmi = True
                    if classAttendanceLog.attendanceCode == "U":
                        classAttendanceLog.assignTmi = True
                    if classAttendanceLog.attendanceCode == "Q":
                        classAttendanceLog.assignTmi = True
                    db.session.commit()

        # Need to run the next statement [classAttendanceForm.process()]
        # or the updated values for the studentAttendanceForm won't display
        tmiTeacherReviewForm.process()

    # Retrive updated fixed-value attendance fields from database
    tmiStartDate = date(2020, 8, 5)
    tmiEndDate = date(2020, 8, 11)
    classAttendanceFixedFields = (
        ClassAttendanceLog.query.filter(
            ClassAttendanceLog.classDate >= tmiStartDate,
            ClassAttendanceLog.classDate <= tmiEndDate,
        )
        .filter(
            (ClassAttendanceLog.attendanceCode == None)
            | (ClassAttendanceLog.attendanceCode != "P")
        )
        .join(ClassSchedule)
        .join(ClassSchedule.Student)
        .filter(
            ClassSchedule.teacherLastName == tmiTeacherReviewForm.teacherName.default
        )
        .order_by(ClassAttendanceLog.classDate)
        .order_by(Student.lastName)
        .all()
    )

    # Retrieve updated student attendance fields from database
    for studentAttendance in classAttendanceFixedFields:
        studentAttendanceForm = updateStudentAttendanceForm()
        studentAttendanceForm.log_id = studentAttendance.id
        studentAttendanceForm.attendanceCode = studentAttendance.attendanceCode
        studentAttendanceForm.comment = studentAttendance.comment
        studentAttendanceForm.assignTmi = studentAttendance.assignTmi
        studentAttendanceForm.updateFlag = ""
        print(
            "ROSTER ",
            studentAttendanceForm.log_id,
            studentAttendance.ClassSchedule.className,
            studentAttendance.ClassSchedule.startTime,
            studentAttendance.ClassSchedule.endTime,
            studentAttendance.ClassSchedule.Student.firstName,
            studentAttendance.ClassSchedule.Student.lastName,
            studentAttendanceForm.attendanceCode,
            studentAttendanceForm.comment,
            studentAttendanceForm.assignTmi,
        )
        tmiTeacherReviewForm.classMembers.append_entry(studentAttendanceForm)

    # Reset the updateFiltersFlag before rendering page
    tmiTeacherReviewForm.updateFiltersFlag.data = ""

    return render_template(
        "tmiteacherreview.html",
        title="TMI Teacher Review",
        classAttendanceForm=tmiTeacherReviewForm,
        classAttendanceFixedFields=classAttendanceFixedFields,
    )
