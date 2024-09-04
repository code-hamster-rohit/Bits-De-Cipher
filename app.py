from connection import db
from models import register_model, score_model, ques_model, user_profile_model
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = 'Bits-de-Cipher#2024@GFG_RGIPT'
app.permanent_session_lifetime = timedelta(hours=48)

# Global dictionary to store user progress
user_progress = {}

def register_user(data):
    collection_registeration_creds = db['registration_creds']
    if collection_registeration_creds.find_one({'roll_number': data['roll_number'].upper()}):
        return block_user()
    else:
        collection_registeration_creds.insert_one(register_model(data))
        create_user_profile(data)
        # Initialize user progress
        user_progress[data['roll_number'].upper()] = {'last_updated': datetime.now()}
        return {'status': 200, 'message': f'{data["roll_number"]} registered successfully'}

def create_user_profile(data):
    user_name = data['roll_number'].upper()
    if user_name not in db.list_collection_names():
        db.create_collection(user_name)

def load_user_progress(roll_number):
    collection_registeration_creds = db['registration_creds']
    if not collection_registeration_creds.find_one({'roll_number': roll_number}):
        return {'status': 300, 'message': 'User not registered'}
    else:
        collection_score_card = db['score_card']
        user_data = collection_score_card.find_one({'roll_number': roll_number}, sort=[('qno', -1)])
        
        if user_data:
            next_question_number = str(int(user_data['qno']) + 1)
        else:
            next_question_number = '1'

        return fetch_question(next_question_number)

def fetch_question(qno):
    collection_qna_marking_scores = db['qna_marking_scores']
    ques_data = collection_qna_marking_scores.find_one({'qno': qno})
    return {'status': 200, 'message': 'Progress loaded', 'data': ques_model(ques_data)}

def calculate_score(base_marks, dynamic_reduction, number_of_submissions):
    return base_marks - (base_marks * dynamic_reduction * number_of_submissions * 0.01)

def update_score(data, correct=True):
    collection_score_card = db['score_card']
    if correct:
        number_of_submissions = collection_score_card.count_documents({'qno': data['qno']})
        scoring_info = get_scoring_info(data['qno'])
        data['score'] = calculate_score(float(scoring_info['bse_maks']), float(scoring_info['dyn_red']), float(number_of_submissions))
        collection_score_card.insert_one(score_model(data))
        collection_profile = db[data['roll_number'].upper()]
        collection_profile.insert_one(user_profile_model(data))
        return {'status': 200, 'message': 'Correct answer!'}
    else:
        collection_profile = db[data['roll_number'].upper()]
        collection_profile.insert_one(user_profile_model(data))
        return {'status': 200, 'message': 'Incorrect answer!'}

def get_scoring_info(qno):
    collection_qna_marking_scores = db['qna_marking_scores']
    return collection_qna_marking_scores.find_one({'qno': qno})

def give_hint(qno, hint_no):
    collection_qna_marking_scores = db['qna_marking_scores']
    hint = collection_qna_marking_scores.find_one({'qno': qno})['hints'][hint_no]
    return {'status': 200, 'message': hint}

def activate_hint_for_scheduler():
    for roll_number, progress in user_progress.items():
        collection_profile = db[roll_number]
        
        # Fetch the latest question based on timestamp
        latest_question_docs = collection_profile.find().sort('timestamp', -1).limit(1)
        latest_question_doc = list(latest_question_docs)
        
        if not latest_question_doc:
            continue
        
        latest_question = latest_question_doc[0]['qno']
        
        # Get the start time of the latest question
        question_data = collection_profile.find_one({'qno': latest_question})
        if not question_data:
            continue
        
        start_time = question_data['timestamp']
        time_span = timedelta(seconds=180)
        
        elapsed_time = datetime.now() - start_time
        
        # Determine which hint to give based on elapsed time
        hint_to_give = None
        if elapsed_time > time_span:
            hint_to_give = give_hint(latest_question, 2)
        elif elapsed_time > time_span * 2 / 3:
            hint_to_give = give_hint(latest_question, 1)
        elif elapsed_time > time_span / 3:
            hint_to_give = give_hint(latest_question, 0)
        
        if hint_to_give:
            # Log hints or send notifications to the user
            print(f"Hint for {roll_number}: {hint_to_give['message']}")


def check_answer(data):
    collection_qna_marking_scores = db['qna_marking_scores']
    correct_answer = collection_qna_marking_scores.find_one({'qno': data['qno']})['ans']
    if str(data['ans']) == correct_answer:
        return update_score(data, correct=True)
    else:
        return update_score(data, correct=False)

def block_user():
    return {'status': 500, 'message': 'Contest has ended. Thank you for participating!'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    result = register_user(data)
    if result['status'] == 200:
        roll_number = data['roll_number'].upper()
        session['roll_number'] = roll_number
        user_progress[roll_number] = {'last_updated': datetime.now()}  # Initialize user progress
    return jsonify(result)

@app.route('/load_progress', methods=['GET'])
def load_progress():
    roll_number = session.get('roll_number')
    result = load_user_progress(roll_number)
    return jsonify(result)

@app.route('/get_hint', methods=['GET'])
def get_hint():
    roll_number = session.get('roll_number')
    if not roll_number:
        return jsonify({'status': 500, 'message': 'Please login to continue'})
    
    collection_profile = db[roll_number]
    
    # Fetch the latest question based on timestamp
    latest_question_docs = collection_profile.find().sort('timestamp', -1).limit(1)
    latest_question_doc = list(latest_question_docs)
    
    if not latest_question_doc:
        return jsonify({'status': 500, 'message': 'No questions answered yet'})
    
    latest_question = latest_question_doc[0]['qno']
    
    # Get the start time of the latest question
    question_data = collection_profile.find_one({'qno': latest_question})
    if not question_data:
        return jsonify({'status': 500, 'message': 'No questions answered yet'})
    
    start_time = question_data['timestamp']
    time_span = timedelta(seconds=180)
    
    elapsed_time = datetime.now() - start_time
    
    # Determine which hint to give based on elapsed time
    if elapsed_time > time_span:
        hint = give_hint(latest_question, 2)
        return jsonify({'status': 200, 'message': hint['message']})
    elif elapsed_time > time_span * 2 / 3:
        hint = give_hint(latest_question, 1)
        return jsonify({'status': 200, 'message': hint['message']})
    elif elapsed_time > time_span / 3:
        hint = give_hint(latest_question, 0)
        return jsonify({'status': 200, 'message': hint['message']})
    else:
        return jsonify({'status': 200, 'message': 'No hints to give yet'})
    
@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    roll_number = session.get('roll_number')
    if roll_number:
        data['roll_number'] = roll_number
        result = check_answer(data)
        return jsonify(result)
    else:
        return jsonify({'status': 500, 'message': 'Please login to continue'})

@app.route('/logout')
def logout():
    roll_number = session.pop('roll_number', None)
    if roll_number in user_progress:
        del user_progress[roll_number]
    return jsonify({'status': 200, 'message': 'Logged out successfully'})

# Schedule the hint system
scheduler = BackgroundScheduler()
scheduler.add_job(func=activate_hint_for_scheduler, trigger="interval", seconds=30)
scheduler.start()

if __name__ == '__main__':
    app.run()