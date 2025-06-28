from flask import Flask, request, jsonify
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load credentials from environment variable
try:
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
    creds = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
except Exception as e:
    creds = None
    print(f"❌ Error loading Google credentials: {e}")

def upload_to_drive(filepath, filename):
    if creds is None:
        raise Exception("Google Drive credentials not loaded.")

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return file.get('id')

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

    try:
        file_id = upload_to_drive(filepath, filename)
        return jsonify({'message': 'Uploaded to Google Drive', 'file_id': file_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
