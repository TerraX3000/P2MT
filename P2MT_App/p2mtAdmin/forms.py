from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField, HiddenField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired
from P2MT_App.main.referenceData import getHouseNames


class addStudentForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    chattStateANumber = StringField("Chatt State A Number", validators=[DataRequired()])
    yearOfGraduation = StringField(
        "Year of Graduation (YYYY)", validators=[DataRequired()]
    )
    house = SelectField("House", validators=[DataRequired()], choices=getHouseNames())
    googleCalendarId = StringField(
        "Google Calendar ID (Use TBD if unknown)", validators=[DataRequired()]
    )
    submitAddStudent = SubmitField("Add Student")


class selectStudentToEditForm(FlaskForm):
    studentName = SelectField("Student Name", validators=[DataRequired()])
    submitStudentToEdit = SubmitField("Edit Student")


class updateStudentForm(FlaskForm):
    student_id = HiddenField()
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    chattStateANumber = StringField("Chatt State A Number", validators=[DataRequired()])
    yearOfGraduation = StringField(
        "Year of Graduation (YYYY)", validators=[DataRequired()]
    )
    house = SelectField("House", validators=[DataRequired()], choices=getHouseNames())
    googleCalendarId = StringField(
        "Google Calendar ID (Use TBD if unknown)", validators=[DataRequired()]
    )
    submitUpdateStudent = SubmitField("Update Student Info")


class uploadStudentListForm(FlaskForm):
    csvStudentListFile = FileField(
        "Student List (*.csv format)",
        validators=[FileAllowed(["csv"]), FileRequired()],
    )
    submitUploadStudentList = SubmitField("Upload Student List")


class deleteStudentForm(FlaskForm):
    studentName = SelectField("Student Name", validators=[DataRequired()])
    confirmDeleteStudent = StringField(
        "Type DELETE to confirm", validators=[DataRequired()]
    )
    submitDeleteStudent = SubmitField("Delete Student")


class addStaffForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    position = StringField("Position", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    phoneNumber = StringField("Phone Number (Optional)")
    chattStateANumber = StringField("Chatt State A Number (Optional)")
    myersBriggs = StringField("Myers Briggs Personality Type (Optional)")
    house = SelectField("House (Optional)", choices=getHouseNames())
    houseGrade = SelectField(
        "House Grade (for House Teachers) (Optional)",
        choices=[("", ""), ("12", "12"), ("11", "11"), ("10", "10"), ("9", "9")],
    )
    twitterAccount = StringField(
        "Twitter Account (Optional)", render_kw={"placeholder": "@"}
    )
    submitAddStaff = SubmitField("Add Staff")


class uploadStaffListForm(FlaskForm):
    csvStaffListFile = FileField(
        "Staff List (*.csv format)", validators=[FileAllowed(["csv"]), FileRequired()],
    )
    submitUploadStaffList = SubmitField("Upload Staff List")


class deleteStaffForm(FlaskForm):
    staffName = SelectField("Staff Name", coerce=int, validators=[DataRequired()])
    confirmDeleteStaff = StringField(
        "Type DELETE to confirm", validators=[DataRequired()]
    )
    submitDeleteStaff = SubmitField("Delete Staff Member")
