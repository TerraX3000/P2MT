from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Blueprint,
    send_file,
)
from flask_login import login_required
from P2MT_App import db
from P2MT_App.scheduleAdmin.forms import (
    uploadClassScheduleForm,
    propagateClassAttendanceLogsForm,
    deleteClassScheduleForm,
    downloadClassScheduleForm,
    downloadClassAttendanceForm,
    addSingleClassSchedule,
)
from P2MT_App.main.referenceData import (
    getTeachers,
    getClassNames,
    getSchoolYear,
    getSemester,
    getStudents,
    getCampusChoices,
    getYearOfGraduation,
)
from P2MT_App.scheduleAdmin.ScheduleAdmin import (
    propagateClassSchedule,
    uploadSchedules,
    deleteClassSchedule,
    downloadClassSchedule,
    downloadClassAttendanceLog,
    addClassSchedule,
    getDuplicateSchedule,
)
from P2MT_App.main.utilityfunctions import save_File
from P2MT_App.main.utilityfunctions import printLogEntry, printFormErrors
from P2MT_App.main.setupFunctions import extendSchoolCalendarIfNecessary

scheduleAdmin_bp = Blueprint("scheduleAdmin_bp", __name__)

# Route for direct download from templates folder
@scheduleAdmin_bp.route("/templates/class_schedule_template")
@login_required
def downloadClassScheduleTemplate():
    try:
        return send_file(
            "static/templates/class_schedule_template.csv",
            attachment_filename="class_schedule_template.csv",
            as_attachment=True,
            cache_timeout=0,
        )
    except Exception as e:
        return str(e)


@scheduleAdmin_bp.route("/scheduleadmin", methods=["GET", "POST"])
@login_required
def displayScheduleAdmin():
    printLogEntry("Running displayScheduleAdmin()")
    extendSchoolCalendarIfNecessary()
    uploadClassScheduleFormDetails = uploadClassScheduleForm()
    propagateClassAttendanceLogsFormDetails = propagateClassAttendanceLogsForm()
    propagateClassAttendanceLogsFormDetails.schoolYear.choices = getSchoolYear()
    propagateClassAttendanceLogsFormDetails.semester.choices = getSemester()
    deleteClassScheduleFormDetails = deleteClassScheduleForm()
    deleteClassScheduleFormDetails.schoolYear.choices = getSchoolYear()
    deleteClassScheduleFormDetails.semester.choices = getSemester()
    deleteClassScheduleFormDetails.yearOfGraduation.choices = getYearOfGraduation()
    downloadClassScheduleFormDetails = downloadClassScheduleForm()
    downloadClassScheduleFormDetails.schoolYear.choices = getSchoolYear()
    downloadClassScheduleFormDetails.semester.choices = getSemester()
    downloadClassAttendanceFormDetails = downloadClassAttendanceForm()
    downloadClassAttendanceFormDetails.schoolYear.choices = getSchoolYear()
    downloadClassAttendanceFormDetails.semester.choices = getSemester()
    downloadClassAttendanceFormDetails.teacherName.choices = getTeachers()
    addSingleClassScheduleDetails = addSingleClassSchedule()
    addSingleClassScheduleDetails.schoolYear.choices = getSchoolYear()
    addSingleClassScheduleDetails.semester.choices = getSemester()
    addSingleClassScheduleDetails.teacherName.choices = getTeachers()
    addSingleClassScheduleDetails.studentName.choices = getStudents()
    addSingleClassScheduleDetails.campus.choices = getCampusChoices()
    addSingleClassScheduleDetails.className.choices = getClassNames()
    addSingleClassScheduleDetails.classDays.choices = [
        ("M", "M"),
        ("T", "T"),
        ("W", "W"),
        ("R", "R"),
        ("F", "F"),
    ]
    if request.method == "POST":
        printLogEntry("form= " + str(request.form))

    if "submitUploadClassSchedule" in request.form:
        if uploadClassScheduleFormDetails.validate_on_submit():
            printLogEntry("Upload Form Submitted")
            if uploadClassScheduleFormDetails.csvClassScheduleFile.data:
                uploadedScheduleFile = save_File(
                    uploadClassScheduleFormDetails.csvClassScheduleFile.data,
                    "Uploaded_Schedule_File.csv",
                )
                uploadSchedules(uploadedScheduleFile)
                return redirect(url_for("scheduleAdmin_bp.displayScheduleAdmin"))
    printFormErrors(uploadClassScheduleFormDetails)
    if "submitPropagatelassAttendanceLogs" in request.form:
        if propagateClassAttendanceLogsFormDetails.validate_on_submit():
            printLogEntry("Propagate Form Submitted")
            schoolYear = int(propagateClassAttendanceLogsFormDetails.schoolYear.data)
            semester = propagateClassAttendanceLogsFormDetails.semester.data
            startDate = propagateClassAttendanceLogsFormDetails.startDate.data
            endDate = propagateClassAttendanceLogsFormDetails.endDate.data
            print(
                "schoolYear=",
                schoolYear,
                "semester=",
                semester,
                "startDate=",
                startDate,
                "endDate=",
                endDate,
            )
            propagateClassSchedule(startDate, endDate, schoolYear, semester)
            return redirect(url_for("scheduleAdmin_bp.displayScheduleAdmin"))
    printFormErrors(propagateClassAttendanceLogsFormDetails)
    if "submitDeleteClassScheduleForm" in request.form:
        if deleteClassScheduleFormDetails.validate_on_submit():
            if (
                deleteClassScheduleFormDetails.confirmDeleteClassSchedule.data
                == "DELETE"
            ):
                printLogEntry("Delete Class Schedule Form Submitted")
                schoolYear = deleteClassScheduleFormDetails.schoolYear.data
                semester = deleteClassScheduleFormDetails.semester.data
                yearOfGraduation = deleteClassScheduleFormDetails.yearOfGraduation.data
                print(
                    "SchoolYear=", schoolYear, " Semester=", semester, yearOfGraduation,
                )
                deleteClassSchedule(schoolYear, semester, yearOfGraduation)
                deleteClassScheduleFormDetails.confirmDeleteClassSchedule.data = ""
                # deleteClassScheduleFormDetails.process()
                return redirect(url_for("scheduleAdmin_bp.displayScheduleAdmin"))
            else:
                deleteClassScheduleFormDetails.confirmDeleteClassSchedule.data = ""
                printLogEntry("Type DELETE in the text box to confirm delete")
    if "submitAddSingleClassSchedule" in request.form:
        if addSingleClassScheduleDetails.validate_on_submit():
            printLogEntry("Add Single Class Schedule submitted")
            schoolYear = addSingleClassScheduleDetails.schoolYear.data
            semester = addSingleClassScheduleDetails.semester.data
            chattStateANumber = addSingleClassScheduleDetails.studentName.data
            teacherLastName = addSingleClassScheduleDetails.teacherName.data
            className = addSingleClassScheduleDetails.className.data
            classDaysList = addSingleClassScheduleDetails.classDays.data
            classDays = ""
            for classDay in classDaysList:
                classDays = classDays + classDay
            startTime = addSingleClassScheduleDetails.startTime.data
            endTime = addSingleClassScheduleDetails.endTime.data
            online = addSingleClassScheduleDetails.online.data
            indStudy = addSingleClassScheduleDetails.indStudy.data
            comment = addSingleClassScheduleDetails.comment.data
            googleCalendarEventID = (
                addSingleClassScheduleDetails.googleCalendarEventID.data
            )
            campus = "STEM School"
            staffID = None
            interventionLog_id = None
            learningLab = False

            print(
                schoolYear,
                semester,
                chattStateANumber,
                teacherLastName,
                className,
                classDays,
                startTime,
                endTime,
                online,
                indStudy,
                comment,
                googleCalendarEventID,
                interventionLog_id,
                learningLab,
            )
            duplicateSchedule = getDuplicateSchedule(
                schoolYear,
                semester,
                chattStateANumber,
                campus,
                className,
                teacherLastName,
                staffID,
                online,
                indStudy,
                "".join(classDays),
                startTime,
                endTime,
                learningLab,
            )
            if duplicateSchedule:
                print("duplicate learning lab submitted", locals())
                flash("Schedule already exists", "error")
                return redirect(url_for("scheduleAdmin_bp.displayScheduleAdmin"))
            addClassSchedule(
                schoolYear,
                semester,
                chattStateANumber,
                campus,
                className,
                teacherLastName,
                staffID,
                online,
                indStudy,
                classDays,
                startTime,
                endTime,
                comment,
                googleCalendarEventID,
                interventionLog_id,
                learningLab,
            )
            db.session.commit()
            flash("New schedule added for student", "success")
            return redirect(url_for("scheduleAdmin_bp.displayScheduleAdmin"))

    if "submitDownloadClassScheduleForm" in request.form:
        if downloadClassScheduleFormDetails.validate_on_submit():
            schoolYear = downloadClassScheduleFormDetails.schoolYear.data
            semester = downloadClassScheduleFormDetails.semester.data
            printLogEntry("Download Class Schedule Form Submitted")
            print(
                "SchoolYear=", schoolYear, " Semester=", semester,
            )
            return downloadClassSchedule(schoolYear, semester)
    if "submitDownloadClassAttendanceForm" in request.form:
        if downloadClassAttendanceFormDetails.validate_on_submit():
            schoolYear = downloadClassAttendanceFormDetails.schoolYear.data
            semester = downloadClassAttendanceFormDetails.semester.data
            teacherName = downloadClassAttendanceFormDetails.teacherName.data
            startDate = downloadClassAttendanceFormDetails.startDate.data
            endDate = downloadClassAttendanceFormDetails.endDate.data
            printLogEntry("Download Class Attendance Form Submitted")
            print(
                "SchoolYear=",
                schoolYear,
                " Semester=",
                semester,
                " teacherName=",
                teacherName,
                " startDate=",
                startDate,
                " endDate=",
                endDate,
            )
            return downloadClassAttendanceLog(
                schoolYear, semester, teacherName, startDate, endDate
            )
    return render_template(
        "scheduleadmin.html",
        title="Schedule Admin",
        propagateClassAttendanceLogsForm=propagateClassAttendanceLogsFormDetails,
        uploadClassScheduleForm=uploadClassScheduleFormDetails,
        deleteClassScheduleForm=deleteClassScheduleFormDetails,
        downloadClassScheduleForm=downloadClassScheduleFormDetails,
        downloadClassAttendanceForm=downloadClassAttendanceFormDetails,
        addSingleClassSchedule=addSingleClassScheduleDetails,
    )
