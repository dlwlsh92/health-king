from flask import Blueprint, render_template, jsonify, request,Response
from bson.objectid import ObjectId
from app import card_collection
from app.secrets import SECRET_KEY
from functools import wraps
import jwt

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms='HS256')

def login_required(f):      									
    @wraps(f)                   								
    def decorated_function(*args, **kwargs):					
        access_token = request.headers.get('Authorization')
        if access_token is not None:  							
            try:
                payload = decode_token(access_token)
            except jwt.InvalidTokenError:
                payload = None     							

            if payload is None: return Response(status=401)
        else:
            return Response(status = 401)  						

        return f(*args, **kwargs)
    return decorated_function

bp = Blueprint('recruit_card',__name__)


@bp.route('/test', methods=['GET'])
@login_required
def test_token():
    access_token = request.headers.get('Authorization')
    payload = decode_token(access_token)
    print(payload)
    return 'ok'

@bp.route('/recruit_card')
def recruit_card():
    return render_template('index.html')

@bp.route('/main', methods=['GET'])
def listing():

    result = list(card_collection.find({}))
    print(result)
    for i in range(len(result)):
        temp_id = str(result[i]['_id']) 
        del result[i]['_id'] 
        result[i]['_id'] = temp_id 

    return jsonify({'result':'success', 'activities': result})


@bp.route('/main/join', methods=['POST'])
def join():
    userID = "TEMPID2"
    userName = "TEMPNAME2"
    receive_oID = request.form['give_ID']

    bson_id = ObjectId(receive_oID)

    target = card_collection.find_one({'_id':bson_id})

    if userName in target['participant']:
        return jsonify({'result': 'fail'})


    target['participant'].append(userName)
    target['IDs'].append(userID)

    target_name = target['participant']
    target_id = target['IDs']

    card_collection.update_one({'_id':bson_id},{'$set':{'participant':target_name}})
    card_collection.update_one({'_id':bson_id},{'$set':{'IDs':target_id}})
    card_collection.update_one({'_id':bson_id},{'$set':{'numbers':len(target_name)}})

    print(card_collection.find_one({'_id':bson_id}))
    return jsonify({'result': 'success'})


@bp.route('/main/registration', methods=['POST'])
def posting():
    
    token = request.headers.get('access_token')
    token = decode_token(token)
    userID = "TEMPID"
    userName = "TEMPNAME"
    receive_acname = request.form['give_acname']
    receive_acmaxnum = request.form['give_acmaxnum']
    receive_time = request.form['give_time']
    receive_place = request.form['give_place']
    receive_content = request.form['give_content']
    
    participant = [userName]
    IDs = [userID]
    numbers = len(participant)
    print("-" * 20)
    print("dbitems:", receive_acname, receive_acmaxnum, receive_time, receive_place, receive_content, numbers, participant, IDs)
    print("-" * 20)
    doc = {
        'acname' : receive_acname,
        'acmaxnum' : receive_acmaxnum,
        'time' : receive_time,
        'place' : receive_place,
        'content' : receive_content,
        'numbers' : numbers,
        'participant' : participant,
        'IDs' : IDs
        }

    card_collection.insert_one(doc)

    print("doc:",doc)

    return jsonify({'result': 'success'})