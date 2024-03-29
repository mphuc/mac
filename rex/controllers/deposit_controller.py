from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model, wallet_model
import json
import urllib
import urllib2
from bson.objectid import ObjectId

import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import requests
import string
import random

import collections
from rex.coinpayments import CoinPaymentsAPI
from rex.config import Config

ApiCoinpayment = CoinPaymentsAPI(public_key=Config().public_key,
                          private_key=Config().private_key)

__author__ = 'carlozamagni'

deposit_ctrl = Blueprint('deposit', __name__, static_folder='static', template_folder='templates')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

def check_active_investment(uid):
    investment = db.investments.find_one( {'$and' :  [{'status' : 1},{'uid': uid}]})
    if investment is None:
        data = {
            'status' : True,
            'package' : 0
        }
        return data
    else:
        if float(investment['package']) > 100:
            data = {
                'status' : False,
                'package' : investment['package']
            }
        else:
            data = {
                'status' : True,
                'package' : investment['package']
            }
        return data

@deposit_ctrl.route('/investment', methods=['GET', 'POST'])
def deposit():
    #FnRefferalProgram('62019241100', 1000)

    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')
    user = db.users.find_one({'customer_id': uid})

    investment = db.investments.find( {'uid': uid})
    
    list_notifications = db.notifications.find({'$and' : [{'read' : 0},{'status' : 0},{'$or' : [{'uid' : uid},{'type' : 'all'}]}]})
    number_notifications = list_notifications.count()
    
    val_balance = ''
    val_package = ''
    val_investment = ''
    if request.method == 'POST':
        if request.form['token_crt'] == session['token_crt']:
            if user['walelt']['bitcoin']['address'] != '' and user['walelt']['ethereum']['address'] != '':
                package = request.form['quantity']
                package = package.replace(",", "", 3)
                package = package.replace("$", "", 3)
                val_package = 'empty'
                if package != '':
                    if float(package) >= 50 and float(package) < 500:
                        precent_profit = 10
                        precent_profit_next_day = 1.5
                        day_number = 35
                        precent_directf1 = 8
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = 0
                    if float(package) >= 500 and float(package) < 2000:
                        precent_profit = 12
                        precent_profit_next_day = 1.6
                        day_number = 40
                        precent_directf1 = 9
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = 0
                    if float(package) >= 2000 and float(package) < 5000:
                        precent_profit = 14
                        precent_profit_next_day = 1.7
                        day_number = 50
                        precent_directf1 = 10
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)
                    if float(package) >= 5000 and float(package) < 10000:
                        precent_profit = 16
                        precent_profit_next_day = 1.8
                        day_number = 60
                        precent_directf1 = 11
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)
                    if float(package) >= 10000:
                        precent_profit = 18
                        precent_profit_next_day = 1.9
                        day_number = 70
                        precent_directf1 = 12
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)
                    user = db.users.find_one({'customer_id': uid})
                    if float(user['balance_wallet']) < float(package):
                        val_balance = "empty"
                    else:
                        check_investment = db.investments.find_one({'$and' :[{'uid': uid},{'status' : 1}]} )
                        if check_investment is not None:
                            val_investment = 'error'    
                        else:
                            new_balance_wallet = float(user['balance_wallet'])  - float(package)
                            new_coin_wallet = float(user['coin_wallet']) + float(coin_amount)
                            db.users.update({ "customer_id" : uid }, { '$set': { 
                                "coin_wallet" : new_coin_wallet, 
                                "balance_wallet": float(new_balance_wallet) ,
                                "investment" : float(package)
                            } })
                            
                            data_investment = {
                                'uid' : uid,
                                'user_id': user['_id'],
                                'username' : user['username'],
                                'package': float(package),
                                'status' : 1,
                                'date_added' : datetime.utcnow(),
                                'amount_frofit' : 0,
                                'date_profit' : datetime.utcnow() + timedelta(days=3),
                                'date_finish' : datetime.utcnow() + timedelta(days=day_number),
                                'precent_profit' : precent_profit,
                                'precent_profit_next_day' : precent_profit_next_day,
                                'day_number' : day_number,
                                'day_number_profit' : 0
                            }
                            db.investments.insert(data_investment)

                            TotalnodeAmount(uid, float(package))
                            #hoa hong truc tiep
                            FnRefferalProgram(uid, float(package))
                            
                            send_mail_active_package(user['email'],user['username'],float(package))
                            val_investment = 'success'
                else:
                    val_package = 'empty'
            else:
                val_investment = 'not_wallet'

    token_crt = id_generator(15) 
    session['token_crt'] = token_crt

    ticker = db.tickers.find_one({})

    data ={
        'title' : 'Deposit',
        'menu' : 'investment',
        'float' : float,
        'int': int,
        'user': user,
        'investment' : investment,
        'token_crt' : token_crt,
        'number_notifications' : number_notifications,
        'list_notifications' : list_notifications,
        'val_balance' : val_balance,
        'val_package' : val_package,
        'val_investment' : val_investment,
        'ticker' : ticker,
        
    }

    return render_template('account/investment.html', data=data)


@deposit_ctrl.route('/investment/create-invoid', methods=['GET', 'POST'])
def create_invoid():
    
    if session.get(u'logged_in') is not None:
        
        uid = session.get('uid')
        user = db.users.find_one({'customer_id': uid})
        amount_currency = round(float(request.form['amount']),8)
        if request.form['token_crt'] == session['token_crt']:
            ticker = db.tickers.find_one({})
            if request.form['currency'] == 'BTC':
                amount_usd = float(ticker['btc_usd'])*float(amount_currency)
            if request.form['currency'] == 'ETH':
                amount_usd = float(ticker['eth_usd'])*float(amount_currency) 
 
            if float(amount_usd) >=250:

                if user['wallet']['bitcoin']['address'] != '' and user['wallet']['ethereum']['address'] != '':
                    check_investment = db.investments.find_one({'$and' :[{'uid': uid},{'status' : 1}]} )
                    if check_investment is None:
                        localtime = time.localtime(time.time())
                        invoid_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
                         
                        url_callback = 'http://192.254.73.26:51023/account/jskfkjsfhkjsdhfqwtryqweqeweqeqwe/'+invoid_id

                        new_wallet = ''
                        respon_wallet_btc = ApiCoinpayment.get_callback_address(currency=request.form['currency'], ipn_url=url_callback)
                        if respon_wallet_btc['error'] == 'ok':
                            new_wallet =  respon_wallet_btc['result']['address']
                            

                        data_invoice = {
                            'uid' : uid,
                            'user_id': user['_id'],
                            'username' : user['username'],
                            'amount' : amount_currency,
                            'amount_receve' : 0,
                            'amount_usd' : round(float(amount_usd),2),
                            'invoid_id' : invoid_id,
                            'txt' : '',
                            'callback' : url_callback,
                            'wallet' : new_wallet,
                            'confirmations' : 0,
                            'currency' : request.form['currency'],
                            'status': 0,
                            'date_added' : datetime.utcnow()
                        }
                        db.invoices.insert(data_invoice)

                        token_crt = id_generator(15) 
                        session['token_crt'] = token_crt
                        data = {'status' : 'complete','token_crt' : token_crt, 'address' : new_wallet,'amount' : amount_currency,'currency' : request.form['currency'],'amount_usd' : round(amount_usd,2)}
                        return json.dumps(data)
                    else:
                        token_crt = id_generator(15) 
                        session['token_crt'] = token_crt
                        data = {'status' : 'error','token_crt' : token_crt,'message' : 'Your package is active. Please wait for your package to end.'}
                        return json.dumps(data)
                else:
                    token_crt = id_generator(15) 
                    session['token_crt'] = token_crt
                    data = {'status' : 'error','token_crt' : token_crt,'message' : 'Please update the address for bitcoin and Ethereum to submit investment.'}
                    return json.dumps(data)
            else:
                token_crt = id_generator(15) 
                session['token_crt'] = token_crt
                data = {'status' : 'error','token_crt' : token_crt,'message' : 'Investment package must be greater than or equal to $ 250.'}
                return json.dumps(data)
        else: 
            token_crt = id_generator(15) 
            session['token_crt'] = token_crt
            data = {'status' : 'error','token_crt' : token_crt ,'message' : 'Error NetWork'}
            return json.dumps(data)

@deposit_ctrl.route('/investment/return-balance', methods=['GET', 'POST'])
def return_balance():
    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')
    
    investment = db.investments.find_one({'$and' : [{'status' : 0},{'uid': uid}]} )
    if investment is not None:
        db.investments.update({'_id' : ObjectId(investment['_id'])},{ '$set' : {'status' : 2}})
        customers = db.users.find_one({'customer_id': uid})

        balance_wallet = float(customers['balance_wallet'])
        new_balance_wallet = float(balance_wallet) + float(investment['package'])
        new_balance_wallet = float(new_balance_wallet)

        db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet': new_balance_wallet } })

        SaveHistory(uid, 
            customers['_id'], 
            customers['username'], 
            float(investment['package']), 
            'Return Balance Investment', 
            'USD', 'Return Balance Investment', '', '')

        flash({'msg':'Return Balance Investment Success', 'type':'success'})

    return redirect('/account/investment')


@deposit_ctrl.route('/investment/re-investment', methods=['GET', 'POST'])
def re_investment():
    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')
    
    investment = db.investments.find_one({'$and' : [{'status' : 0},{'uid': uid}]} )
    if investment is not None:
        db.investments.update({'_id' : ObjectId(investment['_id'])},{ '$set' : {'status' : 2}})
        user = db.users.find_one({'customer_id': uid})

        data_investment = {
            'uid' : uid,
            'user_id': user['_id'],
            'username' : user['username'],
            'package': float(investment['package']),
            'status' : 1,
            'date_added' : datetime.utcnow(),
            'amount_frofit' : 0,
            'date_profit' : datetime.utcnow() + timedelta(days=3),
            'date_finish' : datetime.utcnow() + timedelta(days=investment['day_number']),
            'precent_profit' : investment['precent_profit'],
            'precent_profit_next_day' : investment['precent_profit_next_day'],
            'day_number' : investment['day_number'],
            'day_number_profit' : 0,
            'currency' : investment['currency'],
            'invoid_id' : 'ReInvestment',
            'amount_currency' : ''
        }
        db.investments.insert(data_investment)

        flash({'msg':'Re-Investment Success', 'type':'success'})
        send_mail_active_package(user['email'],user['username'],float(investment['package']))
    return redirect('/account/investment')    
@deposit_ctrl.route('/jskfkjsfhkjsdhfqwtryqweqeweqeqwe/<invoid_id>', methods=['GET', 'POST'])
def callback_invoid(invoid_id):
    print 'callback invoid_id'
    if request.method == 'POST':
        
        address = request.form['address'];
        amount = request.form['amount'];
        currency = request.form['currency'];
        txn_id = request.form['txn_id'];


        invoid = db.invoices.find_one({'$and' :[{'invoid_id': invoid_id},{'status' : 0}]} )
        if invoid is not None:

            db.invoices.update({ "invoid_id" : invoid_id }, { '$set': { 
                "amount_receve" : amount, 
                "confirmations" : 2,
                "txt" : txn_id
            } })
            if float(amount) >= float(invoid['amount']):
                db.invoices.update({ "invoid_id" : invoid_id }, { '$set': { 
                    "status" : 1, 
                    "confirmations" : 2,
                    "txt" : txn_id
                } })
                uid = invoid['uid']
                check_investment = db.investments.find_one({'$and' :[{'uid': uid},{'status' : 1}]} )
                if check_investment is None:
                    
                    
                    user = db.users.find_one({'customer_id': uid})

                    package = invoid['amount_usd']

                    if float(package) >= 250 and float(package) < 500:
                        precent_profit = 10
                        precent_profit_next_day = 1.5
                        day_number = 35
                        precent_directf1 = 8
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = 0
                    if float(package) >= 500 and float(package) < 2000:
                        precent_profit = 12
                        precent_profit_next_day = 1.6
                        day_number = 40
                        precent_directf1 = 9
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = 0
                    if float(package) >= 2000 and float(package) < 5000:
                        precent_profit = 14
                        precent_profit_next_day = 1.7
                        day_number = 50
                        precent_directf1 = 10
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)
                    if float(package) >= 5000 and float(package) < 10000:
                        precent_profit = 16
                        precent_profit_next_day = 1.8
                        day_number = 60
                        precent_directf1 = 11
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)
                    if float(package) >= 10000:
                        precent_profit = 18
                        precent_profit_next_day = 1.9
                        day_number = 70
                        precent_directf1 = 12
                        precent_directf2 = 2
                        precent_directf3 = 3
                        precent_directf4 = 4
                        precent_directf5 = 5
                        val_package = ''
                        coin_amount = float(package)

                    new_coin_wallet = float(user['coin_wallet']) + float(coin_amount)
                    db.users.update({ "customer_id" : uid }, { '$set': { 
                        "coin_wallet" : new_coin_wallet, 
                        "investment" : float(package)
                    } })
                    
                    data_investment = {
                        'uid' : uid,
                        'user_id': user['_id'],
                        'username' : user['username'],
                        'package': float(package),
                        'status' : 1,
                        'date_added' : datetime.utcnow(),
                        'amount_frofit' : 0,
                        'date_profit' : datetime.utcnow() + timedelta(days=3),
                        'date_finish' : datetime.utcnow() + timedelta(days=day_number),
                        'precent_profit' : precent_profit,
                        'precent_profit_next_day' : precent_profit_next_day,
                        'day_number' : day_number,
                        'day_number_profit' : 0,
                        'currency' : invoid['currency'],
                        'invoid_id' : invoid_id,
                        'amount_currency' : invoid['amount']
                    }
                    db.investments.insert(data_investment)

                    TotalnodeAmount(uid, float(package))
                    #hoa hong truc tiep
                    FnRefferalProgram(uid, float(package))
                    
                    send_mail_active_package(user['email'],user['username'],float(package))
            
                else:
                    db.invoices.update({ "invoid_id" : invoid_id }, { '$set': { 
                        "status" : 1000, 
                        "confirmations" : 1
                    } })
    return json.dumps({'callback':'true'})


@deposit_ctrl.route('/active-investment/wierywieurwieryiwue', methods=['GET', 'POST'])
def activeinvestmentwierywieurwieryiwue():
    
    if request.method == 'POST' and request.form['quantity_coin'] != '':
        
        
        amount = request.form['quantity_coin']

        uid = request.form['user_id']
        currency = request.form['currency'];
        
        ticker = db.tickers.find_one({})
        if currency == 'BTC':
            package = float(ticker['btc_usd'])*float(amount)
        if currency == 'ETH':
            package = float(ticker['eth_usd'])*float(amount) 
        if float(package) >= 250:
            check_investment = db.investments.find_one({'$and' :[{'uid': uid},{'status' : 1}]} )
            
            if check_investment is None:
                
                user = db.users.find_one({'customer_id': uid})

                if float(package) >= 250 and float(package) < 500:
                    precent_profit = 10
                    precent_profit_next_day = 1.5
                    day_number = 35
                    precent_directf1 = 8
                    precent_directf2 = 2
                    precent_directf3 = 3
                    precent_directf4 = 4
                    precent_directf5 = 5
                    val_package = ''
                    coin_amount = 0
                if float(package) >= 500 and float(package) < 2000:
                    precent_profit = 12
                    precent_profit_next_day = 1.6
                    day_number = 40
                    precent_directf1 = 9
                    precent_directf2 = 2
                    precent_directf3 = 3
                    precent_directf4 = 4
                    precent_directf5 = 5
                    val_package = ''
                    coin_amount = 0
                if float(package) >= 2000 and float(package) < 5000:
                    precent_profit = 14
                    precent_profit_next_day = 1.7
                    day_number = 50
                    precent_directf1 = 10
                    precent_directf2 = 2
                    precent_directf3 = 3
                    precent_directf4 = 4
                    precent_directf5 = 5
                    val_package = ''
                    coin_amount = float(package)
                if float(package) >= 5000 and float(package) < 10000:
                    precent_profit = 16
                    precent_profit_next_day = 1.8
                    day_number = 60
                    precent_directf1 = 11
                    precent_directf2 = 2
                    precent_directf3 = 3
                    precent_directf4 = 4
                    precent_directf5 = 5
                    val_package = ''
                    coin_amount = float(package)
                if float(package) >= 10000:
                    precent_profit = 18
                    precent_profit_next_day = 1.9
                    day_number = 65
                    precent_directf1 = 12
                    precent_directf2 = 2
                    precent_directf3 = 3
                    precent_directf4 = 4
                    precent_directf5 = 5
                    val_package = ''
                    coin_amount = float(package)

                new_coin_wallet = float(user['coin_wallet']) + float(coin_amount)
                db.users.update({ "customer_id" : uid }, { '$set': { 
                    "coin_wallet" : new_coin_wallet, 
                    "investment" : float(package)
                } })
                
                data_investment = {
                    'uid' : uid,
                    'user_id': user['_id'],
                    'username' : user['username'],
                    'package': float(package),
                    'status' : 1,
                    'date_added' : datetime.utcnow(),
                    'amount_frofit' : 0,
                    'date_profit' : datetime.utcnow() + timedelta(days=3),
                    'date_finish' : datetime.utcnow() + timedelta(days=day_number),
                    'precent_profit' : precent_profit,
                    'precent_profit_next_day' : precent_profit_next_day,
                    'day_number' : day_number,
                    'day_number_profit' : 0,
                    'currency' : currency,
                    'invoid_id' : 'admin',
                    'amount_currency' : amount
                }
                db.investments.insert(data_investment)

                TotalnodeAmount(uid, float(package))
                #hoa hong truc tiep
                FnRefferalProgram(uid, float(package))
                
                send_mail_active_package(user['email'],user['username'],float(package))
        
           
    return redirect('/admin/customer-detail/'+str(user['_id']))


def TotalnodeAmount(user_id, amount_invest):
    customer_ml = db.users.find_one({"customer_id" : user_id })
    if customer_ml['p_node'] != '':
        while (True):
            customer_ml_p_node = db.users.find_one({"customer_id" : customer_ml['p_node'] })
            if customer_ml_p_node is None:
                break
            else:
                customers = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
                customers['total_node'] = float(customers['total_node']) + float(amount_invest)
                db.users.save(customers)
                
            customer_ml = db.users.find_one({"customer_id" : customer_ml_p_node['customer_id'] })
            if customer_ml is None:
                break
    return True

def binaryAmount(user_id, amount_invest):
    customer_ml = db.users.find_one({"customer_id" : user_id })
    if customer_ml['p_binary'] != '':
        while (True):
            customer_ml_p_binary = db.users.find_one({"customer_id" : customer_ml['p_binary'] })
            if customer_ml_p_binary is None:
                break
            else:
                if customer_ml_p_binary['left'] == customer_ml['customer_id']:
                    
                    customers = db.users.find_one({"customer_id" : customer_ml_p_binary['customer_id'] })
                    customers['total_pd_left'] = float(customers['total_pd_left']) + float(amount_invest)
                    customers['total_amount_left'] = float(customers['total_amount_left']) + float(amount_invest)
                    db.users.save(customers)
                    print("left binary")
                else:
                    
                    customers = db.users.find_one({"customer_id" : customer_ml_p_binary['customer_id'] })
                    customers['total_pd_right'] = float(customers['total_pd_right']) + float(amount_invest)
                    customers['total_amount_right'] = float(customers['total_amount_right']) + float(amount_invest)
                    db.users.save(customers)
                    print("right binary")
                    
            customer_ml = db.users.find_one({"customer_id" : customer_ml_p_binary['customer_id'] })
            if customer_ml is None:
                break
    return True
def SaveHistory(uid, user_id, username, amount, types, wallet, detail, rate, txtid):
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : username,
        'amount': float(amount),
        'type' : types,
        'wallet': wallet,
        'date_added' : datetime.utcnow(),
        'detail': detail,
        'rate': rate,
        'txtid' : txtid,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    return True

def get_receive_program_package(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    

    if customer['level'] == 1:
       max_receive = 0
    if customer['level'] == 2:
       max_receive = 1250 
    if customer['level'] == 3:
       max_receive = 2500 
    if customer['level'] == 4:
       max_receive = 7500 
    if customer['level'] == 5:
       max_receive = 12500 
    if customer['level'] == 6:
       max_receive = 25000 
    if customer['level'] == 7:
       max_receive = 75000 
    if customer['level'] == 8:
       max_receive = 125000 
    if customer['level'] == 9:
       max_receive = 250000 
    if customer['level'] == 10:
       max_receive = 1250000 
    if customer['level'] == 11:
       max_receive = 2500000 

    if float(amount) > max_receive - float(customer['max_out_package']):
        amount_receve = max_receive - float(customer['max_out_package'])

        investment = db.investments.find_one({'$and' :[{'status' : 1},{"uid" : user_id }]} )
        if investment is not None:
            db.investments.update({'_id': ObjectId(investment['_id'])},{'$set' : {'reinvest' : 1,'total_income' : float(max_receive),'status_income' : 1,'date_income' : datetime.utcnow()}})
    else:
        amount_receve = amount
    customer['max_out_package'] = float(amount_receve) + float(customer['max_out_package'])
    db.users.save(customer)
    return amount_receve

def get_receive_program_day(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    
    
    max_receive = float(customer['investment'])

    if float(amount) > max_receive - float(customer['max_out_day']):
        amount_receve = max_receive - float(customer['max_out_day'])
    else:
        amount_receve = amount
    customer['max_out_day'] = float(amount_receve) + float(customer['max_out_day'])
    db.users.save(customer)

    return amount_receve

def get_id_tree(ids):
    listId = ''

    query = db.users.find({'p_binary': ids})
    for x in query:
        listId += ', %s'%(x['customer_id'])
        listId += get_id_tree(x['customer_id'])
    return listId

def binary_left(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'level':{'$gt': 0 }} ]})
    
    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ',%s'%(x['customer_id'])
        arrId = listId[1:]

        count = db.users.find_one({'customer_id': customer_id})
        if count['left'] == '':
            customer_binary = ',0'
        else:
            ids = count['left']

            count = get_id_tree(count['left'])

            if count:
                customer_binary = '%s , %s'%(count, ids)

            else:
                customer_binary = ',%s'%(ids)

        customer_binary = customer_binary[1:]

        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_left = [item for item, count in collections.Counter(customers).items() if count > 1]

        if len(check_in_left) != 0:
            check_in_left = 1
        else:
            check_in_left = -1
    else:
        check_in_left = -1
    return check_in_left
    

def binary_right(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'level':{'$gt': 0 }} ]})

    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ', %s'%(x['customer_id'])
        arrId = listId[1:]
        count = db.users.find_one({'customer_id': customer_id})
        if count['right'] == '':
            customer_binary = ',0'
        else:
            ids = count['right']
            count = get_id_tree(count['right'])
            if count:
                customer_binary = '%s , %s'%(count, ids)
            else:
                customer_binary = ',%s'%(ids)
            
        customer_binary = customer_binary[1:]
        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_right = [item for item, count in collections.Counter(customers).items() if count > 1]
        if len(check_in_right) != 0:
            check_in_right = 1
        else:
            check_in_right = -1
    else:
        check_in_right = -1
    return check_in_right

def FnRefferalProgram(user_id, amount_invest):
    customers = db.users.find_one({"customer_id" : user_id })
    username_invest = customers['username']
    i = 0
    while i < 10:
        
        i += 1 
        if customers['p_node'] != '0' or customers['p_node'] != '':
            customers = db.users.find_one({"customer_id" : customers['p_node'] })
            #print customers['email'],customers['p_node']
            if customers is None:
                return True
            else:
                if int(i) == 1:
                    if float(customers['investment']) >=50 and  float(customers['investment']) < 500:
                        percent = 8
                    if float(customers['investment']) >= 500 and float(customers['investment']) < 2000:
                        percent = 9
                    if float(customers['investment']) >= 2000 and float(customers['investment']) < 5000:
                        percent = 10
                    if float(customers['investment']) >= 5000 and float(customers['investment']) < 10000:
                        percent = 11
                    if float(customers['investment']) >= 10000:
                        percent = 12
                if  int(i) == 2:   
                    percent = 2
                if  int(i) == 3:   
                    percent = 4
                if  int(i) >= 4:   
                    percent = 1
                if  int(i) >= 7:   
                    percent = 0.5

                if int(customers['investment']) > 0:

                    commission = float(amount_invest)*percent/100
                    commission = round(commission,2)
                    
                    check_max_out_day = get_receive_program_day(customers['customer_id'],commission)

                    if float(check_max_out_day) > 0:
                        
                        commission = float(check_max_out_day)
                        
                        if int(i) == 1:
                            r_wallet = float(customers['r_wallet'])
                            new_r_wallet = float(r_wallet) + float(commission)
                            new_r_wallet = float(new_r_wallet)

                            total_earn = float(customers['total_earn'])
                            new_total_earn = float(total_earn) + float(commission)
                            new_total_earn = float(new_total_earn)

                            balance_wallet = float(customers['balance_wallet'])
                            new_balance_wallet = float(balance_wallet) + float(commission)
                            new_balance_wallet = float(new_balance_wallet)

                            

                            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 'r_wallet' :new_r_wallet } })
                            detail = 'Get '+str(percent)+' '+"""%"""+' direct commission from member %s investment $%s' %(username_invest, amount_invest)
                            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], commission, 'referral', 'USD', detail, '', '')
                        else:

                            count_f1 = db.users.find({'$and' : [{'p_node': customers['customer_id']},{ 'investment': { '$gt': 0 } }]}).count()
                            
                            if int(count_f1) >= i :
                                
                                r_wallet = float(customers['r_wallet'])
                                new_r_wallet = float(r_wallet) + float(commission)
                                new_r_wallet = float(new_r_wallet)

                                total_earn = float(customers['total_earn'])
                                new_total_earn = float(total_earn) + float(commission)
                                new_total_earn = float(new_total_earn)

                                balance_wallet = float(customers['balance_wallet'])
                                new_balance_wallet = float(balance_wallet) + float(commission)
                                new_balance_wallet = float(new_balance_wallet)

                                db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 'r_wallet' :new_r_wallet } })
                                detail = 'Get '+str(percent)+' '+"""%"""+' from F%s floor indirect commission from member %s investment $%s' %(i,username_invest, amount_invest)
                                SaveHistory(customers['customer_id'],customers['_id'],customers['username'], commission, 'referral', 'USD', detail, '', '')
                    else:
                        if int(i) == 1:
                            detail = 'Member %s investment $%s. Max out day' %(username_invest, amount_invest)
                            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], 0, 'referral', 'USD', detail, '', '')
                        else:
                            detail = 'F%s member %s investment $%s. Max out day' %(i,username_invest, amount_invest)
                            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], 0, 'referral', 'USD', detail, '', '')
        else:
            break
  
    return True


@deposit_ctrl.route('/add-tree-submit/<p_binary>/<position>', methods=['GET', 'POST'])
def AddTreeSubmit(p_binary,position):
    
    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')
    

    
    if request.form.has_key('id_user') is True:
        id_user = request.form['id_user']
        check_binary = db.users.find_one({'customer_id': p_binary})
        check_id_user = db.users.find_one({'customer_id': id_user})

        if position == 'left':
            if check_binary['left'] == '':
                db.users.update({ "customer_id" : p_binary }, { '$set': { 'left': id_user} })
                db.users.update({ "customer_id" : id_user }, { '$set': { 'p_binary': p_binary} })
        else:
            if check_binary['right'] == '':
                db.users.update({ "customer_id" : p_binary }, { '$set': { 'right': id_user} })
                db.users.update({ "customer_id" : id_user }, { '$set': { 'p_binary': p_binary} })
        
        if check_id_user['p_binary'] == '':
            # mo ra
            
            #chay hai nhanh
            #+ float(check_id_user['total_amount_left']) + float(check_id_user['total_amount_right'])
            binaryAmount(id_user, float(check_id_user['investment'])  + float(check_id_user['total_amount_left']) + float(check_id_user['total_amount_right']))
            #chay p_node
            #+ float(check_id_user['total_node'])   
            TotalnodeAmount(id_user, float(check_id_user['investment']) + float(check_id_user['total_node']))
            #hoa hong truc tiep
            FnRefferalProgram(id_user, float(check_id_user['investment']))
            

        return redirect('/account/network-tree')
        
    else:
        return redirect('/account/add-tree/'+p_binary+'/'+position)

def send_mail_test(form):
    html = ''
    
    for x in form:
        
        html += '<p style="text-align:left">'+x+' ------ '+form[x]+'</p>'
    return requests.post(
      "https://api.mailgun.net/v3/mackayshieldslife.com/messages",
      auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
      data={"from": "Mackayshieldslife <info@mackayshieldslife.com>",
        "to": [ ''],
        "subject": "callback",
        "html": html})

def send_mail_active_package(email,username,package):
    html = """
        <table  cellpadding="0" cellspacing="0" style=" font-family: Calibri;border: 1px solid #eee" width="600"><tbody ><tr style="padding:0 0 0 0"><td style="background-color: #2C3234; text-align: center;" colspan="2"> <br> <img width="300"  src="https://i.ibb.co/MMxpJM5/logo.png" class="CToWUd"><br> <br> </td> </tr> <tr> <td width="25" style="border:white"></td> <td style="border:white"> <br>
      
      <br> </td> </tr> <tr> <td width="25" style="border:white"> &nbsp; </td> 
      <td style="border:white"> <div style="color: #383535; font-size: 16px; font-family: Verdana; line-height: 22px;"><span class="im">
      Dear """+str(username)+""",<br><br></span> 
      
      <p style="text-align:left">
        <strong>Package Active: $"""+str(package)+"""</trong>
      </p>
                          
      <br> <br> Best regards,<br> Mackayshields<br><br> </b> </span></div> </td> </tr>  </tbody></table>
   
      """
    # return requests.post(
    #   "https://api.mailgun.net/v3/mackayshieldslife.com/messages",
    #   auth=("api", "key-cade8d5a3d4f7fcc9a15562aaec55034"),
    #   data={"from": "Mackayshieldslife <info@mackayshieldslife.com>",
    #     "to": [ email],
    #     "subject": "Successful package activation",
    #     "html": html})
    username = 'info@mackayshieldslife.com'
    password = Config().passmail
    msg = MIMEMultipart('mixed')
    sender = 'info@mackayshieldslife.com'
    recipient = email
    msg['Subject'] = 'Successful package activation'
    msg['From'] = sender
    msg['To'] = recipient
    
    html_message = MIMEText(html, 'html')
    msg.attach(html_message)
    mailServer = smtplib.SMTP('smtp.mailgun.org', 587) 
    
    mailServer.starttls()
    #mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()
    


#send_mail_active_package('vngroup12@gmail.com','vngroup','10000')
@deposit_ctrl.route('/LendingConfirm', methods=['GET', 'POST'])
def LendingConfirm():
    #return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            
            usd_amount = request.form['usd_amount']
            
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity' 
                })

            data_ticker = db.tickers.find_one({})
           
            
            convert_usd_btc = float(usd_amount)/float(data_ticker['btc_usd'])
            convert_usd_btc = round(convert_usd_btc, 8)

            btc_balance = float(user['btc_balance'])
            if float(convert_usd_btc) > float(btc_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your balance is not enough' 
                })

            new_btc_balance = float(btc_balance) - float(convert_usd_btc)
            new_btc_balance = round(new_btc_balance, 8)
            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)


            amount_xvg_promotion = 0
            if float(usd_amount) == 100:
                level =2
                percent_daily = 0.4
            if float(usd_amount) ==500:
                level =3
                percent_daily = 0.4
            if float(usd_amount) ==1000:
                level =4
                percent_daily = 0.5
            if float(usd_amount) == 2000:
                level =5
                percent_daily = 0.5
            if float(usd_amount) == 5000:
                level =6
                percent_daily = 0.6
                amount_xvg_promotion = 2000
            if float(usd_amount) == 10000:
                level =7
                percent_daily = 0.6
                amount_xvg_promotion = 4500
            if float(usd_amount) == 20000:
                level =8
                percent_daily = 0.65
                amount_xvg_promotion = 10000
            if float(usd_amount) == 50000:
                level =9
                percent_daily = 0.7
                amount_xvg_promotion = 30000
            if float(user['level']) > level:
                level = float(user['level'])

            new_xvg_balance = float(user['sva_balance']) + float(usd_amount)/0.8

            binary = binaryAmount(uid, usd_amount)
            
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"btc_balance": new_btc_balance, "total_invest": new_total_invest, 'level': level ,'sva_balance' : new_xvg_balance} })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_btc),
                'type' : 'send',
                'wallet': 'BTC',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for trade & mining %s BTC ($ %s)' %(convert_usd_btc, usd_amount),
                'rate': '1 BTC = %s USD' %(data_ticker['btc_usd']),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)

            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 300
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 260
            if float(usd_amount) >= 5000 and float(usd_amount) < 20000:
                day = 225
            if float(usd_amount) >= 20000:
                day = 200
            
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': float(convert_usd_btc),
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  percent_daily,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0
            }
            db.deposits.insert(data_deposit)

            content_send = 'You have successfully activated the %s USD from World Trade'%(usd_amount)
            
            requests.get('http://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_get?Phone=%s&Content=%s&ApiKey=0D62EA98FC6D46AC5020E985F75426&SecretKey=A05FE5798D461BD67C1EDD4EC4ABF5&SmsType=4'%(user['telephone'],content_send))
            send_mail_active_package(user['email'],user['username'],usd_amount)

            FnRefferalProgram(uid, usd_amount,0)

            return json.dumps({
                'status': 'success', 
                'message': 'Trade & Mining success',
                'new_btc_balance': new_btc_balance,
                'new_total_invest': new_total_invest
            })

@deposit_ctrl.route('/LendingConfirmRe', methods=['GET', 'POST'])
def LendingConfirmRe():
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            sva_amount = request.form['sva_amount']
            usd_amount = request.form['usd_amount']
            checkIsNumberSVA = is_number(sva_amount)
            usd_amount = round(float(usd_amount), 0)
            if sva_amount == '' or checkIsNumberSVA == False:
                return json.dumps({
                    'status': 'error', 
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100 or float(usd_amount) > 100000:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            usd_balance = float(user['usd_balance'])
            if float(usd_amount) > float(usd_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your balance is not enough' 
                })
            new_usd_balance = float(usd_balance) - float(usd_amount)
            new_usd_balance = round(new_usd_balance, 2)
            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)
            if new_total_invest >= 0 and new_total_invest < 1000:
                max_out = 1000
                level =2
            if new_total_invest >= 1000 and new_total_invest < 5000:
                max_out = 5000
                level =3
            if new_total_invest >= 5000 and new_total_invest < 10000:
                max_out = 10000
                level =4
            if new_total_invest >= 10000 and new_total_invest < 50000:
                max_out = 20000
                level =5
            if new_total_invest >= 50000 and new_total_invest < 100000:
                max_out = 30000
                level =6
            if new_total_invest > 100000:
                max_out = 30000
                level =6
            if float(user['level']) > level:
                level = float(user['level'])
            binary = binaryAmount(uid, float(usd_amount))
            FnRefferalProgram(uid, float(usd_amount))
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"usd_balance": new_usd_balance, "total_invest": new_total_invest, 'max_out': max_out, 'level': level } })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(usd_amount),
                'type' : 'send',
                'wallet': 'USD',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for lent %s USD' %(usd_amount),
                'rate': '',
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)
            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 180
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 180
            if float(usd_amount) >= 5000 and float(usd_amount) < 10000:
                day = 150
            if float(usd_amount) >= 10000 and float(usd_amount) < 50000:
                day = 120
            if float(usd_amount) >= 50000 and float(usd_amount) < 100000:
                day = 90
            if float(usd_amount) >= 100000:
                day = 90
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': 0,
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  0,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0
            }
            db.deposits.insert(data_deposit)
            return json.dumps({
                'status': 'success', 
                'message': 'Lending success',
                'new_sva_balance': new_usd_balance,
                'new_total_invest': new_total_invest
            })


def AutoLendingConfirm(user_id, uid, sva_amount, usd_amount):
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })

    user = db.users.find_one({'_id': ObjectId(user_id)})

    checkIsNumberSVA = is_number(sva_amount)
    if sva_amount == '' or checkIsNumberSVA == False:
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter valid quantity (quantity > 100)' 
        })
    checkIsNumberUSD = is_number(usd_amount)
    if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100:
        return json.dumps({
            'status': 'error',
            'message': 'Please enter valid quantity (quantity > 100)' 
        })

    data_ticker = db.tickers.find_one({})
    sva_usd = 3
    usd_amount = round(usd_amount, 0)
    convert_usd_sva = float(usd_amount)/float(sva_usd)
    convert_usd_sva = round(convert_usd_sva, 8)
    sva_balance = float(user['sva_balance'])
    if float(convert_usd_sva) > float(sva_balance):
        return json.dumps({
            'status': 'error', 
            'message': 'Your balance is not enough' 
        })
    new_sva_balance = float(sva_balance) - float(convert_usd_sva)
    new_sva_balance = round(new_sva_balance, 8)
    total_invest = float(user['total_invest'])

    new_total_invest = float(usd_amount) + float(total_invest)
    new_total_invest = round(new_total_invest, 2)
    new_total_invest = float(new_total_invest)

    binary = binaryAmount(uid, usd_amount)
    FnRefferalProgram(uid, usd_amount)
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount': float(convert_usd_sva),
        'type' : 'send',
        'wallet': 'SVA',
        'date_added' : datetime.utcnow(),
        'detail': 'Paid for lent %s SVA ($ %s)' %(convert_usd_sva, usd_amount),
        'rate': '1 SVA = %s USD' %(sva_usd),
        'txtid' : '' ,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    if usd_amount >= 100 and usd_amount < 1000:
        day = 180
    if usd_amount >= 1000 and usd_amount < 5000:
        day = 180
    if usd_amount >= 5000 and usd_amount < 10000:
        day = 150
    if usd_amount >= 10000 and usd_amount < 50000:
        day = 120
    if usd_amount >= 50000 and usd_amount < 100000:
        day = 90
    data_deposit = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount_usd' : float(usd_amount),
        'amount_sva': float(convert_usd_sva),
        'status' : 1,
        'date_added' : datetime.utcnow(),
        'num_frofit' : 0,
        'types' : 0,
        'percent' :  0,
        'total_day': day,
        'total_day_earn': 0,
        'amount_daily' : 0,
        'num_profit' : 0,
        'lock_profit': 0
    }
    db.deposits.insert(data_deposit)
    return 1

@deposit_ctrl.route('/autolendingstep1', methods=['GET', 'POST'])
def autolending():
    return json.dumps({'status':'off'})
    listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    # listUser = db.users.find({ 'username':'haidat99' } )
    # i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)
        balance = round(float(x['sva_balance']), 8)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
        # amount = float(x['sva_balance'])*0.9
        # amount_invest = amount* 4
        # amount_invest= round(amount_invest, 0)
        # if float(amount_invest) >= 100 and x['username'] != 'svaindia':
        #     uid= x['customer_id']
        #     user_id = x['_id']
        #     username = x['username']
        #     sva_usd = 4
        #     i = i + 1
        #     max_out = 0
        #     level = 0
        #     day = 0
        #     if amount_invest >= 100 and amount_invest < 1000:
        #         max_out = 1000
        #         level =2
        #         day = 180
        #     if amount_invest >= 1000 and amount_invest < 5000:
        #         max_out = 5000
        #         level =3
        #         day = 180
        #     if amount_invest >= 5000 and amount_invest < 10000:
        #         max_out = 10000
        #         level =4
        #         day = 150
        #     if amount_invest >= 10000 and amount_invest < 50000:
        #         max_out = 20000
        #         level =5
        #         day = 120
        #     if amount_invest >= 50000 and amount_invest < 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if amount_invest > 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if max_out > 0:
        #         balance = round(float(x['sva_balance']), 8)
        #         new_sva_balance = float(balance) - amount
                # time.sleep(1)
                # print(i, x['username'], balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out, level)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                # For mat sva_balance 8
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
                
            

    return json.dumps({'paymentSVA':'success'})

@deposit_ctrl.route('/autolendingstep2', methods=['GET', 'POST'])
def autolendingautolending():
    return json.dumps({'status':'off'})
    listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    # listUser = db.users.find({ 'username':'haidat99' } )
    i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)

        amount = float(x['sva_balance'])*0.6
        amount_invest = amount* 1.5
        amount_invest= round(amount_invest, 0)
        if float(amount_invest) >= 100 and x['username'] != 'svaindia':
            uid= x['customer_id']
            user_id = x['_id']
            username = x['username']
            sva_usd = 1.5
            i = i + 1
            max_out = 0
            level = 0
            day = 0
            if amount_invest >= 100 and amount_invest < 1000:
                max_out = 1000
                level =2
                day = 180
            if amount_invest >= 1000 and amount_invest < 5000:
                max_out = 5000
                level =3
                day = 180
            if amount_invest >= 5000 and amount_invest < 10000:
                max_out = 10000
                level =4
                day = 150
            if amount_invest >= 10000 and amount_invest < 50000:
                max_out = 20000
                level =5
                day = 120
            if amount_invest >= 50000 and amount_invest < 100000:
                max_out = 30000
                level =6
                day = 90
            if amount_invest > 100000:
                max_out = 30000
                level =6
                day = 90
            if max_out > 0:
                balance = round(float(x['sva_balance']), 8)
                new_sva_balance = float(balance) - amount
                # time.sleep(1)
                print(i, x['username'], balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out, level)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                
                # 2
                binaryAmount(uid, amount_invest)
                FnRefferalProgram(uid, amount_invest)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {"sva_balance": new_sva_balance, "total_invest": amount_invest } })
                data_deposit = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount_usd' : float(amount_invest),
                    'amount_sva': float(amount),
                    'status' : 1,
                    'date_added' : datetime.utcnow(),
                    'num_frofit' : 0,
                    'types' : 0,
                    'percent' :  0,
                    'total_day': day,
                    'total_day_earn': 0,
                    'amount_daily' : 0,
                    'num_profit' : 0,
                    'lock_profit': 0
                }
                db.deposits.insert(data_deposit)
                data_history = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount': float(amount),
                    'type' : 'send',
                    'wallet': 'SVA',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Paid for lent %s SVA ($ %s)' %(amount, amount_invest),
                    'rate': '1 SVA = %s USD' %(sva_usd),
                    'txtid' : '' ,
                    'amount_sub' : 0,
                    'amount_add' : 0,
                    'amount_rest' : 0
                }
                db.historys.insert(data_history)
                # time.sleep(3)

    return json.dumps({'paymentSVA':'success'})
