import uuid, OpenSSL

from bson import ObjectId
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

LIMIT_DEFAULT = 50
PAGE_DEFAULT = 1

app = Flask(__name__)

# app.config['MONGO_DBNAME'] = 'bankacc'
# app.config['MONGO_USERNAME'] = 'admin'
# app.config['MONGO_PASSWORD'] = '123456'
app.config['MONGO_URI'] = 'mongodb://sangnd:ali33team@ds123182.mlab.com:23182/bankacc'
mongo = PyMongo(app)


# get list accounts after login
# @params  jsessionid (require), limit, page, search (option)
@app.route('/accounts', methods=['GET'])
def get_account():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})

    limit = get_string_param('limit')
    page = get_string_param('page')
    search = get_string_param('search')
    if limit is None:
        limit = LIMIT_DEFAULT
    if page is None:
        page = PAGE_DEFAULT

    int_limit = get_int_limit(limit)
    int_page = get_int_page(page)
    skip_number = get_skip_number(int_limit, int_page)
    acounts = mongo.db.acounts

    if not (search is None):
        search_dict = {"$or": [
            # {"account_number": {'$regex': search}},
            # {"balance": float(search)},
            {"firstname": {'$regex': search}},
            {"lastname": {'$regex': search}},
            # {"age": {'$regex': search}},
            {"gender": {'$regex': search}},
            {"address": {'$regex': search}},
            {"employer": {'$regex': search}},
            {"email": {'$regex': search}},
            {"city": {'$regex': search}},
            {"state": {'$regex': search}},
        ]}
        accounts = acounts.find(search_dict).skip(skip_number).limit(int_limit)
        list_accounts = []
        for acc in accounts:
            account = {'_id': str(acc['_id']), 'account_number': acc['account_number'], 'balance': acc['balance'],
                       'firstname': acc['firstname'], 'lastname': acc['lastname'], 'age': acc['age'],
                       'gender': acc['gender'], 'address': acc['address'], 'employer': acc['employer'],
                       'email': acc['email'], 'city': acc['city'], 'state': acc['state']
                       }
            list_accounts.append(account)
        total = accounts.count()
        return jsonify(
            {'result': {'message': 'return list account', 'status': 'OK', 'page': 'page', 'limit': limit,
                        'search': search,
                        'total': total,
                        'accounts': list_accounts,
                        'user': {'_id': str(user['_id']), 'username': user['username'],
                                 'firstname': user['firstname'],
                                 'lastname': user['lastname'], 'email': user['email'],
                                 'jsessionid': jsessionid,
                                 'role': user['role']}}})
    else:
        accounts = acounts.find().skip(skip_number).limit(int_limit)
        list_accounts = []
        for acc in accounts:
            account = {'_id': str(acc['_id']), 'account_number': acc['account_number'], 'balance': acc['balance'],
                       'firstname': acc['firstname'], 'lastname': acc['lastname'], 'age': acc['age'],
                       'gender': acc['gender'], 'address': acc['address'], 'employer': acc['employer'],
                       'email': acc['email'], 'city': acc['city'], 'state': acc['state']
                       }
            list_accounts.append(account)
        total = accounts.count()
        return jsonify({'result': {'message': 'return list account', 'status': 'OK', 'page': 'page', 'limit': limit,
                                   'search': search,
                                   'total': total,
                                   'accounts': list_accounts,
                                   'user': {'_id': str(user['_id']), 'username': user['username'],
                                            'firstname': user['firstname'],
                                            'lastname': user['lastname'], 'email': user['email'],
                                            'jsessionid': jsessionid,
                                            'role': user['role']}}})


# get details info of account by id
# params jsessionid, _id (required)
@app.route('/details', methods=['GET'])
def get_details_account():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})

    _id = get_string_param('_id')
    accounts = mongo.db.acounts
    account = accounts.find_one({'_id': ObjectId(_id)})

    if account is None:
        return jsonify({'result': {'message': 'Can not found', 'status': 'NG'}})
    else:

        acc = {'_id': str(account['_id']), 'account_number': account['account_number'], 'balance': account['balance'],
               'firstname': account['firstname'], 'lastname': account['lastname'], 'age': account['age'],
               'gender': account['gender'], 'address': account['address'], 'employer': account['employer'],
               'email': account['email'], 'city': account['city'], 'state': account['state']
               }

        return jsonify({'result': {'message': 'ok', 'status': 'OK', 'account': acc,
                                   'user': {'_id': str(user['_id']), 'username': user['username'],
                                            'firstname': user['firstname'],
                                            'lastname': user['lastname'], 'email': user['email'],
                                            'jsessionid': jsessionid,
                                            'role': user['role']}}})


# delete an account
# params jsessionid, _id (required)
@app.route('/delete', methods=['POST'])
def delete_account():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    elif user['role'] == 2:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    else:
        _id = get_string_param('_id')
        accounts = mongo.db.acounts
        account = accounts.find({'_id': ObjectId(_id)})
        if account is None:
            return jsonify({'result': {'message': 'Can not found account', 'status': 'NG'}})
        else:
            try:
                accounts = mongo.db.acounts
                result = accounts.remove({'_id': ObjectId(_id)})
                return jsonify({'result': result, 'user': {'_id': str(user['_id']), 'username': user['username'],
                                                           'firstname': user['firstname'],
                                                           'lastname': user['lastname'], 'email': user['email'],
                                                           'jsessionid': jsessionid,
                                                           'role': user['role']}})
            except:
                return jsonify({'result': {'message': 'Can not insert', 'status': 'NG'}})


# insert an account
# params jsessionid(required)
# param account_number, balance, firstname, lastname, age, gender, address, employer, email, city, state (option)
@app.route('/insert', methods=['POST'])
def insert_account():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    elif user['role'] == 2:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    else:
        account_number = get_int_param('account_number')
        balance = get_int_param('balance')
        firstname = get_string_param('firstname')
        lastname = get_string_param('lastname')
        age = get_int_param('age')
        gender = get_string_param('gender')
        address = get_string_param('address')
        employer = get_string_param('employer')
        email = get_string_param('email')
        city = get_string_param('city')
        state = get_string_param('state')
        accounts = mongo.db.acounts
        data = {'account_number': account_number, 'firstname': firstname, 'lastname': lastname, 'balance': balance,
                'age': age, 'gender': gender, 'address': address, 'employer': employer, 'email': email,
                'city': city, 'state': state}
        try:
            result = accounts.insert(data)
            data['_id'] = str(result)

            return jsonify({'result': {'message': 'ok', 'status': 'OK', 'account': data,
                                       'user': {'_id': str(user['_id']), 'username': user['username'],
                                                'firstname': user['firstname'],
                                                'lastname': user['lastname'], 'email': user['email'],
                                                'jsessionid': jsessionid,
                                                'role': user['role']}}})
        except:
            return jsonify({'result': {'message': 'Can not insert', 'status': 'NG'}})


# update an account
# params jsessionid, _id (required)
# param account_number, balance, firstname, lastname, age, gender, address, employer, email, city, state (option
@app.route('/update', methods=['POST'])
def update_account():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    elif user['role'] == 2:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    else:
        _id = get_string_param('_id')
        account_number = get_int_param('account_number')
        balance = get_int_param('balance')
        firstname = get_string_param('firstname')
        lastname = get_string_param('lastname')
        age = get_int_param('age')
        gender = get_string_param('gender')
        address = get_string_param('address')
        employer = get_string_param('employer')
        email = get_string_param('email')
        city = get_string_param('city')
        state = get_string_param('state')
        accounts = mongo.db.acounts
        data = {'account_number': account_number, 'firstname': firstname, 'lastname': lastname,
                'balance': balance,
                'age': age, 'gender': gender, 'address': address, 'employer': employer, 'email': email,
                'city': city, 'state': state}
        try:
            result = accounts.update({'_id': ObjectId(_id)}, {'$set': data})
            data['_id'] = _id;
            return jsonify({'result': {'message': result,
                                       'account': data,
                                       'user': {'_id': str(user['_id']), 'username': user['username'],
                                                'firstname': user['firstname'],
                                                'lastname': user['lastname'], 'email': user['email'],
                                                'jsessionid': jsessionid,
                                                'role': user['role']}}})
        except:
            return jsonify({'result': {'message': 'Can not insert', 'status': 'NG'}})


# Login method with 2 params username and password
# If login success, this method will create a jsessionid use for other method, jsessionid exist in 30minutes
# Return user info
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    username = get_string_param('username')
    password = get_string_param('password')
    user = users.find_one({'$and': [{'username': username}, {'password': password}]})

    if not (user is None) and len(user) > 0:
        _id = user['_id']
        jsessionid = gen_session_id()
        users.update({'_id': _id}, {'$set': {'jsessionid': jsessionid}})
        return jsonify(
            {'result': {'message': 'OK',
                        'status': 'OK',
                        'user': {'_id': str(user['_id']), 'username': user['username'],
                                 'firstname': user['firstname'],
                                 'lastname': user['lastname'], 'email': user['email'],
                                 'jsessionid': jsessionid, 'role': user['role']}}})
    else:
        return jsonify(
            {'result': {'message': 'Login fail.', 'status': 'NG'}})


# logout
# remove jsessionid
@app.route('/logout', methods=['POST'])
def logout():
    jsessionid = get_string_param('jsessionid')
    user = check_jsessionid(jsessionid)
    if user is None:
        return jsonify({'result': {'message': 'Permission denied', 'status': 'NG'}})
    else:
        _id = user['_id']
        users = mongo.db.users
        result = users.update({'_id':    ObjectId(_id)}, {'$unset': {'jsessionid': ''}})
        return jsonify({'result': result})


# generate session id
def gen_session_id():
    return uuid.UUID(bytes=OpenSSL.rand.bytes(16))


# check session timeout
def check_session_timeout():
    return True


# Check user permission
def check_jsessionid(jsessionid):
    users = mongo.db.users
    try:
        user = users.find_one({'jsessionid': uuid.UUID(jsessionid)})
    except:
        return None
    if not (user is None) and len(user) > 0:
        return user
    else:
        return None


# Use for logout method
def remove_session(jsessionid):
    users = mongo.db.users
    user = users.find_one({'jsessionid': jsessionid})
    if not (user is None) and len(user) > 0:
        user.update({'$set': {'jsessionid': ''}})
        return True
    else:
        return False


# get offset
def get_skip_number(limit, page):
    return int(limit) * (int(page) - 1);


# get int limit
def get_int_limit(limit):
    try:
        return int(limit)
    except:
        return LIMIT_DEFAULT


# get int page
def get_int_page(page):
    try:
        return int(page)
    except:
        return PAGE_DEFAULT


# get string param method
def get_string_param(name):
    return request.args.get(name)


# get string param method
def get_int_param(name):
    try:
        return float(request.args.get(name))
    except:
        return -1


if __name__ == '__main__':
    app.run(host='0.0.0.0')
