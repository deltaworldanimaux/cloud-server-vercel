from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    store_id = request.form.get('store_id')
    if not store_id:
        return jsonify({'error': 'No store_id provided'}), 400

    filename = f"{store_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({'message': 'File uploaded successfully', 'file': filename})