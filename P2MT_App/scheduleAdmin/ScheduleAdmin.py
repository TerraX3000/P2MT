from flask import send_file, current_app, flash, abort
from P2MT_App import db
from P2MT_App.models import ClassSchedule, ClassAttendanceLog, SchoolCalendar, Student
from P2MT_App.main.utilityfunctions import download_File, printLogEntry
from datetime import datetime, date, time
import re
import os
import csv

print("\n=========", __file__, "=========\n")


def addClassAttendanceLog(classSchedule_id, list_of_dates):
    # Adds entries to class attendance log for a given classSchedule_id and list of dates
    # Ignores classes when inCurrentClassAttendaceLog is true
    printLogEntry("addClassAttendanceLog() function called")
    for classDate in list_of_dates:
        inCurrentClassAttendaceLog = ClassAttendanceLog.query.filter(
            ClassAttendanceLog.classSchedule_id == classSchedule_id,
            ClassAttendanceLog.classDate == classDate,
        ).all()
        # print("inCurrentClassAttendaceLog=", inCurrentClassAttendaceLog)
        if not inCurrentClassAttendaceLog:
            commentTuple = (
                db.session.query(ClassSchedule.comment)
                .filter(ClassSchedule.id == classSchedule_id)
                .first()
            )
            # comment = [item for item in commentTuple]
            classAttendanceLog = ClassAttendanceLog(
                classSchedule_id=classSchedule_id,
                classDate=classDate,
                comment=commentTuple[0],
                # attendanceCode=attendanceCode,
                # assignTmi=assignTmi,
            )
            print(classAttendanceLog)
            db.session.add(classAttendanceLog)
            db.session.commit()


# Add class schedule information to database
def addClassSchedule(
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
):
    classSchedule1 = ClassSchedule(
        schoolYear=schoolYear,
        semester=semester,
        chattStateANumber=chattStateANumber,
        campus=campus,
        className=className,
        teacherLastName=teacherLastName,
        staffID=staffID,
        online=online,
        indStudy=indStudy,
        classDays=classDays,
        startTime=startTime,
        endTime=endTime,
        comment=comment,
        googleCalendarEventID=googleCalendarEventID,
        interventionLog_id=interventionLog_id,
        learningLab=learningLab,
    )
    printLogEntry("addClassSchedule() function called")
    print(classSchedule1)
    print("Learning Lab =", learningLab)
    db.session.add(classSchedule1)
    db.session.commit()
    return classSchedule1


def uploadSchedules(fname):
    printLogEntry("uploadSchedules() function called")
    importCSV = open(fname, "r")
    for row in importCSV:
        print("row=", row)
        column = row.split(",")
        print("column=", column)
        schoolYear = column[0].strip()
        if schoolYear == "year":
            continue
        semester = column[1].strip()
        chattStateANumber = column[2].strip()
        campus = column[7].strip()
        className = column[9].strip()
        teacherLastName = column[11].strip()
        staffID = None
        online = column[12].strip()
        if online == "1":
            online = True
        else:
            online = False
        indStudy = column[13].strip()
        if indStudy == "1":
            indStudy = True
        else:
            indStudy = False
        classDays = column[14].strip()
        print(column[16].strip())
        try:  # %I Hour (12-hour clock) as a zero-padded decimal number.	01, 02, ..., 12
            startTime = datetime.strptime(column[16].strip(), "%I:%M %p").time()
            endTime = datetime.strptime(column[17].strip(), "%I:%M %p").time()
            print("%I worked")
        except:
            try:  # %-I Hour (12-hour clock) as a decimal number.	1, 2, ... 12
                startTime = datetime.strptime(column[16].strip(), "%-I:%M %p").time()
                endTime = datetime.strptime(column[17].strip(), "%-I:%M %p").time()
                print("%-I worked")
            except:
                try:  # %H Hour (24-hour clock) as a zero-padded decimal number.	00, 01, ..., 23
                    startTime = datetime.strptime(column[16].strip(), "%H:%M %p").time()
                    endTime = datetime.strptime(column[17].strip(), "%H:%M %p").time()
                    print("%H worked")
                except:
                    try:  # %-H Hour (24-hour clock) as a decimal number.	0, 1, ..., 23
                        startTime = datetime.strptime(
                            column[16].strip(), "%-H:%M %p"
                        ).time()
                        endTime = datetime.strptime(
                            column[17].strip(), "%-H:%M %p"
                        ).time()
                        print("%-H worked")
                    except Exception as err:
                        print(err)
                        flash("Error processing class time")
                        error = f"""Error processing class time: <br>
                        Submitted: <br>
                        chattStateANumber: {column[2]} <br>
                        startTime: {column[16]} <br>
                        endTime: {column[17]} <br>
                        Failed: %I:%M %p (12-hour clock) as a decimal number.	1, 2, ... 12 <br>
                        Failed: %-I:%M %p (12-hour clock) as a decimal number.	1, 2, ... 12 <br>
                        Failed: %H:%M %p (24-hour clock) as a zero-padded decimal number.	00, 01, ..., 23 <br>
                        Failed: %-H:%M %p (24-hour clock) as a decimal number.	0, 1, ..., 23 <br><br>
                        {err}"""
                        return abort(500, description=error)
        comment = column[18].strip()
        googleCalendarEventID = ""
        interventionLog_id = None
        learningLab = False
        # try:
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
        # try:
        #     ...
        # except Exception as err:
        #     print(err)
        #     error = f"""Error processing schedule: <br>
        #     Processed values when error occurred: <br>
        #     schoolYear: {schoolYear} <br>
        #     semester: {semester} <br>
        #     chattStateANumber: {chattStateANumber} <br>
        #     campus: {campus} <br>
        #     className: {className} <br>
        #     teacherLastName: {teacherLastName} <br>
        #     staffID: {staffID} <br>
        #     online: {online} <br>
        #     indStudy: {indStudy} <br>
        #     classDays: {classDays} <br>
        #     startTime: {startTime} <br>
        #     endTime: {endTime} <br>
        #     comment: {comment} <br>
        #     googleCalendarEventID: {googleCalendarEventID} <br>
        #     interventionLog_id: {interventionLog_id} <br>
        #     learningLab: {learningLab} <br>
        #     <br><br>
        #     {err}"""
        #     return abort(500, description=error)
        return True


def deleteClassSchedule(schoolYear, semester, yearOfGraduation):
    printLogEntry("deleteClassSchedule() function called")
    classSchedules = (
        ClassSchedule.query.join(Student)
        .filter(
            ClassSchedule.schoolYear == schoolYear,
            ClassSchedule.semester == semester,
            Student.yearOfGraduation == yearOfGraduation,
        )
        .all()
    )
    for classSchedule in classSchedules:
        db.session.delete(classSchedule)
        db.session.commit()
    return


def downloadClassSchedule(schoolYear, semester):
    printLogEntry("downloadClassSchedule() function called")
    # Create a CSV output file and append with a timestamp
    output_file_path = os.path.join(current_app.root_path, "static/download")
    output_file_path = "/tmp"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csvFilename = output_file_path + "/" + "class_schedule_" + timestamp + ".csv"
    csvOutputFile = open(csvFilename, "w")
    csvOutputWriter = csv.writer(
        csvOutputFile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    # Write header row for CSV file
    csvOutputWriter.writerow(
        [
            "year",
            "semester",
            "Chatt_State_A_Number",
            "CSname",
            "firstName",
            "lastName",
            "HSclass",
            "campus",
            "courseNumber",
            "courseName",
            "sectionID",
            "teacher",
            "online",
            "indStudy",
            "days",
            "times",
            "startTime",
            "endTime",
            "comment",
            "googleCalendarEventID",
        ]
    )
    csvOutputFileRowCount = 0
    # Query the ClassSchedule with a join to include student information
    ClassSchedules = ClassSchedule.query.filter(
        ClassSchedule.schoolYear == schoolYear,
        ClassSchedule.semester == semester,
        ClassSchedule.learningLab == False,
    ).order_by(ClassSchedule.chattStateANumber.desc())
    # Process each record in the query and write to the output file
    for classSchedule in ClassSchedules:
        chattStateANumber = classSchedule.chattStateANumber
        lastName = classSchedule.Student.lastName
        firstName = classSchedule.Student.firstName
        CSname = lastName + " " + firstName
        HSclass = classSchedule.Student.yearOfGraduation
        campus = classSchedule.campus
        courseNumber = ""
        courseName = classSchedule.className
        sectionID = ""
        teacher = classSchedule.teacherLastName
        online = classSchedule.online
        if online:
            online = "1"
        else:
            online = "0"
        indStudy = classSchedule.indStudy
        if indStudy:
            indStudy = "1"
        else:
            indStudy = "0"
        days = classSchedule.classDays
        startTime = classSchedule.startTime
        endTime = classSchedule.endTime
        comment = classSchedule.comment
        googleCalendarEventID = classSchedule.googleCalendarEventID

        csvOutputWriter.writerow(
            [
                str(schoolYear),
                semester,
                chattStateANumber,
                CSname,
                firstName,
                lastName,
                str(HSclass),
                campus,
                courseNumber,
                courseName,
                str(sectionID),
                teacher,
                online,
                indStudy,
                days,
                startTime.strftime("%-I:%M") + " - " + endTime.strftime("%-I:%M"),
                startTime.strftime("%-I:%M %p"),
                endTime.strftime("%-I:%M %p"),
                comment,
                googleCalendarEventID,
            ]
        )
        csvOutputFileRowCount = csvOutputFileRowCount + 1
    csvOutputFile.close()
    return send_file(csvFilename, as_attachment=True, cache_timeout=0)


def downloadClassAttendanceLog(schoolYear, semester, teacherName, startDate, endDate):
    printLogEntry("downloadClassAttendanceLog() function called")
    # Create a CSV output file and append with a timestamp
    output_file_path = os.path.join(current_app.root_path, "static/download")
    output_file_path = "/tmp"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csvFilename = output_file_path + "/" + "class_attendance_" + timestamp + ".csv"
    csvOutputFile = open(csvFilename, "w")
    csvOutputWriter = csv.writer(
        csvOutputFile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    # Write header row for CSV file
    csvOutputWriter.writerow(
        [
            "teacher",
            "className",
            "day",
            "classDate",
            "startTime",
            "endTime",
            "firstName",
            "lastName",
            "attendanceCode",
            "comment",
        ]
    )
    csvOutputFileRowCount = 0
    # Query for class attendance records
    ClassAttendanceLogs = (
        ClassAttendanceLog.query.join(ClassSchedule)
        .join(ClassSchedule.Student)
        .filter(
            ClassSchedule.schoolYear == schoolYear,
            ClassSchedule.semester == semester,
            ClassSchedule.teacherLastName == teacherName,
            ClassAttendanceLog.classDate >= startDate,
            ClassAttendanceLog.classDate <= endDate,
        )
        .order_by(ClassAttendanceLog.classDate)
        .order_by(ClassSchedule.startTime)
        .order_by(ClassSchedule.className)
        .order_by(Student.lastName)
    )
    # Process each record in the query and write to the output file
    for classAttendanceLog in ClassAttendanceLogs:
        csvOutputWriter.writerow(
            [
                classAttendanceLog.ClassSchedule.teacherLastName,
                classAttendanceLog.ClassSchedule.className,
                classAttendanceLog.classDate.strftime("%a"),
                classAttendanceLog.classDate.strftime("%Y-%m-%d"),
                classAttendanceLog.ClassSchedule.startTime.strftime("%-I:%M %p"),
                classAttendanceLog.ClassSchedule.endTime.strftime("%-I:%M %p"),
                classAttendanceLog.ClassSchedule.Student.firstName,
                classAttendanceLog.ClassSchedule.Student.lastName,
                classAttendanceLog.attendanceCode,
                classAttendanceLog.comment,
            ]
        )

        csvElementCounter = 1
        csvOutputFileRowCount = csvOutputFileRowCount + 1
    csvOutputFile.close()
    return send_file(csvFilename, as_attachment=True, cache_timeout=0)


def createListOfDates(SchoolCalendarTableExtract):
    dateList = []
    for day in SchoolCalendarTableExtract:
        dateList.append(day.classDate)
    return dateList


def propagateClassSchedule(startDate, endDate, schoolYear, semester):
    printLogEntry("propagateClassSchedule() function called")
    # Create lists of days to use for propagating class schedule
    schoolCalendar = db.session.query(SchoolCalendar)
    phaseIIDays = schoolCalendar.filter(SchoolCalendar.phaseIISchoolDay)
    dateRange = phaseIIDays.filter(
        SchoolCalendar.classDate >= startDate, SchoolCalendar.classDate <= endDate
    )
    list_of_mondays = createListOfDates(
        dateRange.filter(SchoolCalendar.day == "M").all()
    )
    # print(list_of_mondays)
    list_of_tuesdays = createListOfDates(
        dateRange.filter(SchoolCalendar.day == "T").all()
    )
    # print(list_of_tuesdays)
    list_of_wednesdays = createListOfDates(
        dateRange.filter(SchoolCalendar.day == "W").all()
    )
    list_of_thursdays = createListOfDates(
        dateRange.filter(SchoolCalendar.day == "R").all()
    )
    list_of_fridays = createListOfDates(
        dateRange.filter(SchoolCalendar.day == "F").all()
    )
    # Extract details from class schedule
    classSchedules = (
        ClassSchedule.query.filter(ClassSchedule.semester == semester)
        .filter(
            ClassSchedule.schoolYear == schoolYear,
            ClassSchedule.campus == "STEM School",
        )
        .all()
    )
    print("Total number of rows in classSchedules:", len(classSchedules))
    for classSchedule in classSchedules:
        classSchedule_id = classSchedule.id
        online = classSchedule.online
        indStudy = classSchedule.indStudy
        classDays = classSchedule.classDays
        meetsOnMonday = re.search("[M]", classDays)
        meetsOnTuesday = re.search("[T]", classDays)
        meetsOnWednesday = re.search("[W]", classDays)
        meetsOnThursday = re.search("[R]", classDays)
        meetsOnFriday = re.search("[F]", classDays)
        if meetsOnMonday and not online and not indStudy:
            # print("Monday:", classSchedule_id, classDays)
            addClassAttendanceLog(classSchedule_id, list_of_mondays)
        if meetsOnTuesday and not online and not indStudy:
            # print("Tuesday:", classSchedule_id, classDays)
            addClassAttendanceLog(classSchedule_id, list_of_tuesdays)
        if meetsOnWednesday and not online and not indStudy:
            # print("Wednesday:", classSchedule_id, classDays)
            addClassAttendanceLog(classSchedule_id, list_of_wednesdays)
        if meetsOnThursday and not online and not indStudy:
            # print("Thursday:", classSchedule_id, classDays)
            addClassAttendanceLog(classSchedule_id, list_of_thursdays)
        if meetsOnFriday and not online and not indStudy:
            # print("Friday:", classSchedule_id, classDays)
            addClassAttendanceLog(classSchedule_id, list_of_fridays)
