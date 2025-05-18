import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Session, Message, Priority
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)

# Update the database connection URL to use environment variable (for deployment)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/mydb')  # Fallback for local development
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Initialize DB session
session = Session()

@app.route('/')
def index():
    sort_by = request.args.get('sort', 'timestamp')
    order = request.args.get('order', 'desc')
    status_filter = request.args.get('status', None)
    priority_filter = request.args.get('priority', None)

    query = session.query(Message)
    
    if status_filter:
        query = query.filter(Message.status == status_filter)
    if priority_filter:
        query = query.filter(Message.priority == priority_filter)
    
    if order == 'desc':
        query = query.order_by(desc(getattr(Message, sort_by)))
    else:
        query = query.order_by(getattr(Message, sort_by))
    
    messages = query.all()
    return render_template('index.html', messages=messages, Priority=Priority)

@app.route('/message/<int:id>', methods=['GET', 'POST'])
def message(id):
    message = session.query(Message).filter_by(id=id).first()
    
    if request.method == 'POST':
        response_text = request.form['response']
        priority = request.form.get('priority')
        
        message.response_text = response_text
        message.status = "resolved"
        message.resolved_at = datetime.utcnow()
        message.agent_id = request.form.get('agent_id', 1)
        
        if priority:
            message.priority = priority
            
        session.commit()
        return redirect(url_for('index'))
    
    return render_template('message.html', message=message, Priority=Priority)

@app.route('/update_status', methods=['POST'])
def update_status():
    message_id = request.form.get('message_id')
    new_status = request.form.get('status')
    
    message = session.query(Message).filter_by(id=message_id).first()
    if message:
        message.status = new_status
        if new_status == 'resolved':
            message.resolved_at = datetime.utcnow()
        session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 404

@app.route('/new_message', methods=['POST'])
def new_message():
    customer_id = request.form['customer_id']
    message_text = request.form['message_text']
    
    priority = Priority.MEDIUM
    urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately']
    if any(keyword in message_text.lower() for keyword in urgent_keywords):
        priority = Priority.HIGH
    
    new_msg = Message(
        customer_id=customer_id,
        message_text=message_text,
        priority=priority
    )
    session.add(new_msg)
    session.commit()
    
    return jsonify(success=True)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    
    if not query:
        return redirect(url_for('index'))

    messages = session.query(Message).filter(
        (Message.message_text.ilike(f'%{query}%')) | 
        (Message.customer_id.ilike(f'%{query}%'))
    ).all()
    
    return render_template('index.html', messages=messages, Priority=Priority)

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=True for development
