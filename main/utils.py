from django.conf import settings
from django.core.mail import send_mail


def confirmation_email(receiver, name, code):
    subject = f"Hoistflick: Confirmation Code"
    message = ''
    from_email = f'rigantech@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>This is to confirm that you have registered an account on <b>Hoistflick</b>.</p>
    <p>Kindly enter the confirmation code below to verify your email.</p>
    <h1 style="text-align:center;margin:20px;letter-spacing:15px;">{code}</h1>
    <br><br>
    <p>We hope that you enjoy your experience with us.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>Hoistflick.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def confirmation_login(receiver, name, code):
    subject = f"Hoistflick: Login Confirmation Code"
    message = ''
    from_email = f'rigantech@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>This is to confirm that there is a login attempt for account on <b>Hoistflick</b>.</p>
    <p>Kindly enter the confirmation code below to verify your login.</p>
    <h1 style="text-align:center;margin:20px;letter-spacing:15px;">{code}</h1>
    <br><br>
    <p>If this login attempt is not you, kindly ignore this message as no further action is required.</p>
    <p>You are getting this email because this email is registered with us.</p>
    <p>We hope that you enjoy your experience with us.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>Hoistflick.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_password_email(receiver, name, new_password):
    subject = f"Hoistflick: Password Reset Request"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>You have requested a password reset. your new temporary password is <span style="color:blue;font-weight:600">{new_password}</span></p>
    <p>Kindly change your password after logging in.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>Hoistflick.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

    subject = f"Rigan API Confirm Email"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:center; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>This is to confirm that you have registered an account on <b>Rigan API</b>.</p>
    <br><br>
    <p>We hope that you enjoy your experience with us.</p><br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)



def send_contact_message(receiver, admin_name, name, sender, mssg):
    subject = f"New Message Alert"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {admin_name},<h4><br><br>
    <p>You have a new message alert from <a href="mailto:{sender}" style="color:blue;font-weight:600">{name}: {sender}</a></p>
    <p><span style="color:blue;font-weight:600">Message:</span> {mssg}</p><br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_sub_comment(receiver, name, project, comment):
    subject = f"Rigan Tech: Project Submission Review"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear {name},<h4><br><br>
    <p>Review of your submission on the project: <span style="color:blue;font-weight:600">{project}</span></p>
    <div>{comment}</div><br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_sub_submission(name, project, type):
    subject = f"Hackode Project Submission: {type}"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = ['rigantech@gmail.com']  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear Rigan,<h4><br><br>
    <p>{name} has made a submission on the project: <span style="color:blue;font-weight:600">{project}</span></p>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_activation_key(receiver, key, id):
    subject = f"Rigan PyEditor Activation Key"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = [receiver]  # List of recipient emails
    html_message = f"""
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear Customer,<h4><br><br>
    <p>This is to confirm that you have purchased an activation key for <b>Rigan PyEditor</b>.</p>
    <br><br>
    <p><b style="color:blue">Payment Reference: </b><b>{id}</b></p>
    <p><b style="color:blue">Your Activation Key: </b><b>{key}</b></p>
    <p>We hope that you enjoy your experience with us.</p><br><br>
    <p>For any enquiry or complaint, kindly <a href="https://wa.me/2347011978058">Message us on whatsApp</a> or <a href="mailto:rigantech@gmail.com">Send us an Email</a>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_feedback(email, subject, message):
    subject = f"{subject}"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = ['rigantech@gmail.com']  # List of recipient emails
    html_message = f"""
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear WhizzyDoc,<h4><br><br>
    <p>You have a new message alert from <a href="mailto:{email}" style="color:blue;font-weight:600">{email}</a></p>
    <p><span style="color:blue;font-weight:600">Message:</span></p>
    <div>{message}</div>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_schedule_notification(receiver, date, venue, description, course, url):
    subject = f"Rigan Tech: Lecture Schedule Notification"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = receiver  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear user,<h4><br><br>
    <p>This is to notify you that a class has been scheduled for you as follows:</p>
    <p><b>Course:</b> {course}</p>
    <p><b>Date:</b> {date}</p>
    <p><b>Venue:</b> {venue}</p>
    <p><b>Link:</b> {url}</p>
    <p><b>Description:</b></p>
    <div>{description}</div>
    <br>
    <p>Kindly visit the RigLearn app to join the class when its time.</p>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_project_notification(receiver, date, title, course):
    subject = f"Rigan Tech: Project Assignment Notification"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = receiver  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear user,<h4><br><br>
    <p>This is to notify you that you have been assigned a project as follows:</p>
    <p><b>Course:</b> {course}</p>
    <p><b>Title:</b> {title}</p>
    <p><b>Deadline:</b> {date}</p>
    <br>
    <p>Kindly visit the RigLearn app to see more details about the project.</p>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_video_notification(receiver, course, title):
    subject = f"Rigan Tech: New Video Notification"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = receiver  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear user,<h4><br><br>
    <p>This is to notify you that a new video has been uploaded for a skill you registered for:</p>
    <p><b>Course:</b> {course}</p>
    <p><b>Title:</b> {title}</p>
    <br>
    <p>Kindly visit the RigLearn app to see more details about the video.</p>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_material_notification(receiver, course, title):
    subject = f"Rigan Tech: New Course Material Notification"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = receiver  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear user,<h4><br><br>
    <p>This is to notify you that a course material has been uploaded for a skill you registered for:</p>
    <p><b>Course:</b> {course}</p>
    <p><b>Topic:</b> {title}</p>
    <br>
    <p>Kindly visit the RigLearn app to read more on the material.</p>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

def send_quiz_notification(receiver, course, title):
    subject = f"Rigan Tech: New Quiz Notification"
    message = ''
    from_email = 'encrane04@gmail.com'  # Sender's email
    recipient_list = receiver  # List of recipient emails
    html_message = f"""
    <center>
    <img src="https://riganapi.pythonanywhere.com/media/hackode/logo.png" alt="" style="width: 150px;height:auto;" />
    </center>
    <div style="text-align:left; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;">
    <h4>Dear user,<h4><br><br>
    <p>This is to notify you that a Quiz has been unlocked for a course you registered for:</p>
    <p><b>Course:</b> {course}</p>
    <p><b>Quiz Title:</b> {title}</p>
    <br>
    <p>Kindly visit the RigLearn app to attempt the quiz and test your understanding of the course.</p>
    <br><br>
    <h4>Best Regards,<h4>
    <h4>Rigan Tech.</h4>
    </div>
    """
    fail_silently = False
    send_mail(subject, message, from_email, recipient_list, fail_silently, html_message=html_message)

