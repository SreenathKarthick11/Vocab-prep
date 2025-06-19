from flask import Flask, render_template, request, jsonify
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
app = Flask(__name__, static_folder='static', template_folder='templates')

def create_google_creds():
    creds_path = "google_credentials.json"
    if not os.path.exists(creds_path):
        creds_json = os.environ.get("GOOGLE_CREDENTIALS")
        with open(creds_path, "w") as f:
            f.write(creds_json)
    return creds_path

def get_sheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_file = create_google_creds()
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Grewords").sheet1 
    data = sheet.get_all_records()
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-quiz', methods=['POST'])
def get_quiz():
    try:
        num_questions = int(request.json['num_questions'])
        data = get_sheet_data()
        if num_questions > len(data):
            num_questions = len(data)

        questions = random.sample(data, num_questions)
        quiz = []

        for q in questions:
            meaning = q['Meaning']
            correct_word = q['Word']
            distractors = random.sample(
                [d['Word'] for d in data if d['Word'] != correct_word],
                3
            )
            options = distractors + [correct_word]
            random.shuffle(options)
            quiz.append({
                "meaning": meaning,
                "options": options,
                "answer": correct_word
            })

        return jsonify(quiz)
    except Exception as e:
        print("\n💥 ERROR in /get-quiz route:", e, "\n")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
