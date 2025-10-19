from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar
import mysql.connector

task = Blueprint('task', __name__)