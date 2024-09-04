from passkey_generator import Passkey
from bson import ObjectId
from datetime import datetime

def register_model(data):
    return {
        '_id': ObjectId(),
        'roll_number': data['roll_number'].upper(),
        'passkey': Passkey(10).passkey,
        'timestamp': datetime.now()
    }

def score_model(data):
    return {
        '_id': ObjectId(),
        'roll_number': data['roll_number'].upper(),
        'qno': data['qno'],
        'score': data['score'],
    }

def ques_model(data):
    return {
        'qno': data['qno'],
        'qn': data['qn'],
    }

def user_profile_model(data):
    return {
        '_id': ObjectId(),
        'roll_number': data['roll_number'].upper(),
        'qno': data['qno'],
        'ans': data['ans'],
        'timestamp': datetime.now()
    }