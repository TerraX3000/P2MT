from flask import render_template, redirect, url_for, flash, Blueprint
from P2MT_App import db

schoolCalendar_bp = Blueprint("schoolCalendar_bp", __name__)
