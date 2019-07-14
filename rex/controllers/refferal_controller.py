from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
from bson.objectid import ObjectId
__author__ = 'carlozamagni'

refferal_ctrl = Blueprint('refferal', __name__, static_folder='static', template_folder='templates')

def get_id_tree_node_package(ids):
    listId = 0
    query = db.users.find({'p_node': ids})
    for x in query:
        listId += float(x['investment'])
        listId += get_id_tree_node_package(x['customer_id'])
    return listId

@refferal_ctrl.route('/referrals', methods=['GET', 'POST'])
def refferal():



	if session.get(u'logged_in') is None:
		return redirect('/auth/login')
	uid = session.get('uid')
	
	

	user = db.users.find_one({'customer_id': uid})
	username = user['username']
	
	list_notifications = db.notifications.find({'$and' : [{'read' : 0},{'status' : 0},{'$or' : [{'uid' : uid},{'type' : 'all'}]}]})
	number_notifications = list_notifications.count()

	get_id_tree_package = get_id_tree_node_package(uid)

	f1_noactive = db.User.find({'$and' :[{'p_node': uid},{"level": 0}]})
	f1_active_no_tree = db.User.find({'$and' :[{'p_node': uid},{'p_binary' : ''},{"level": { "$gt": 0 }}]})
	f1_active_tree = db.User.find({'$and' :[{'p_node': uid},{ 'p_binary': {'$ne' : ''}},{"level": { "$gt": 0 }}]})



	data ={
		'f1_noactive' : f1_noactive,
		'f1_active_no_tree' : f1_active_no_tree,
		'f1_active_tree' : f1_active_tree,
		'title': 'my-network',
		'menu' : 'my-network',
		'user': user,
		'uid': uid,
		'get_id_tree_package' : get_id_tree_package,
		'number_notifications' : number_notifications,
	    'list_notifications' : list_notifications
	}
	return render_template('account/refferal.html', data=data)
def de_email(email):
    e = email.split('@')
    if len(e[0]) > 6:
        x_first = str(e[0][:-6])+'******'
    else:
        if len(e[0]) == 6:
            x_first = str(e[0][:-4])+'*****'
        if len(e[0]) == 5:
            x_first = str(e[0][:-3])+'****'
        if len(e[0]) == 4:
            x_first = str(e[0][:-3])+'***'
        if len(e[0]) == 3:
            x_first = str(e[0][:-2])+'**'
        if len(e[0]) == 2:
            x_first = str(e[0][:-1])+'*'
        if len(e[0]) == 1:
            x_first = str(e[0])
    if  len(e[1]) > 6:
        e_last = '******'+str(e[1][6:])
    return str(x_first)+'@'+str(e_last)
def children_tree (json,array,floor):
    customer = db.User.find({'p_node': json['customer_id']}) 
    floor = floor + 1
    for x in customer:
        tree = {
            "customer_id":str(x['customer_id']),
            "email":(str(x['email'])),
            "username":(str(x['username'])),
            "fl":"F"+str(floor),
            "country" : x['country'],
            "investment" : x['investment'],
            "creation":x['creation'],
            "total_node":x['total_node'],
            "children" : []
        }
        count_f1 = db.User.find({'p_node': str(x['customer_id'])}).count()
        sponsor = db.User.find_one({'customer_id': x['p_node']})
        sponsor_name = ''
        if sponsor:
            sponsor_name = sponsor['username']
        
        children = {
            "customer_id":str(x['customer_id']),
            "creation":x['creation'],
            "email":(str(x['email'])),
            "username":(str(x['username'])),
            "level" : str(x['level']),
            "count_f1" : str(count_f1),
            "floor":"F"+str(floor),
            "sponsor" :  (str(sponsor_name)),
            "country" : x['country'],
            "investment" : x['investment'],
            "total_node":x['total_node'],
        }
        array.append(children)
        json['children'].append(tree)
        
        children_tree (tree,array,floor)
@refferal_ctrl.route('/system', methods=['GET', 'POST'])
def system():



    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')

    user = db.User.find_one({'customer_id': uid})


    list_notifications = db.notifications.find({'$and' : [{'read' : 0},{'status' : 0},{'$or' : [{'uid' : uid},{'type' : 'all'}]}]})
    number_notifications = list_notifications.count()
    
    list_member = db.users.find({'p_node': uid})

    data ={
        'list_member':list_member,
        'count_f1' : db.User.find({'$and' : [{'p_node': uid},{ 'investment': { '$gt': 0 } }]}).count(),
        'user' : user,
        'email' : user['username'],
        'number_notifications' : number_notifications
    }
    return render_template('account/system.html', data=data)

@refferal_ctrl.route('/system/<_id>', methods=['GET', 'POST'])
def system_member(_id):



    if session.get(u'logged_in') is None:
        return redirect('/auth/login')
    uid = session.get('uid')

    user = db.User.find_one({'customer_id': uid})


    list_notifications = db.notifications.find({'$and' : [{'read' : 0},{'status' : 0},{'$or' : [{'uid' : uid},{'type' : 'all'}]}]})
    number_notifications = list_notifications.count()
    
    list_member = db.users.find({'p_node': _id})

    data ={
        'list_member':list_member,
        'count_f1' : db.User.find({'$and' : [{'p_node': uid},{ 'investment': { '$gt': 0 } }]}).count(),
        'user' : user,
        'email' : db.User.find_one({'customer_id': _id})['username'],
        'number_notifications' : number_notifications
    }
    return render_template('account/system.html', data=data)