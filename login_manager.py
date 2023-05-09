from flask import Flask, render_template, request, redirect, session



def login_required(mycursor):
    user = session.get('user')
    if user:
        mycursor.execute("SELECT * FROM users WHERE user_id = %s", (user[0],))
        user_data = mycursor.fetchone()

        return user_data
    else:
        return None