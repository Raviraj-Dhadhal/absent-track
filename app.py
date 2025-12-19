from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for session management

# Load the student master list (Render-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
master_df = pd.read_excel(os.path.join(BASE_DIR, "students.xlsx"))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form.get('date')
        lecture = request.form.get('lecture')
        roll_numbers = request.form.get('roll_numbers')

        entered_rolls = [r.strip() for r in roll_numbers.split(',') if r.strip()]
        absent_df = master_df[
            master_df['Roll Number'].astype(str).isin(entered_rolls)
        ].copy()

        absent_df['Date'] = date
        absent_df['Lecture'] = lecture

        if 'absentees' not in session:
            session['absentees'] = []
        session['absentees'].extend(absent_df.to_dict(orient='records'))
        session['date'] = date

        if 'next' in request.form:
            return redirect('/')
        elif 'finish' in request.form:
            return redirect('/finish')

    return render_template('index.html', date=session.get('date', ''))

@app.route('/finish', methods=['GET'])
def finish():
    absentees = session.get('absentees', [])
    grouped = {}

    for record in absentees:
        lecture = record['Lecture']
        name = f"{record['Roll Number']} {record['Name']}"
        grouped.setdefault(lecture, []).append(name)

    date_title = session.get('date', 'N/A')

    session.pop('absentees', None)
    session.pop('date', None)

    return render_template('result.html', grouped=grouped, date_title=date_title)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
