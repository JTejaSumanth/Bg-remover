from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
import time
from rembg import remove

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/remove_background', methods=['POST'])
def remove_background():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            new_filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename_parts = new_filename.rsplit('.', 1)
            filename = f"{filename_parts[0]}_{timestamp}.{filename_parts[1]}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.split('.')[0]}_output.png")

            with open(filepath, 'rb') as f:
                with open(output_path, 'wb') as output:
                    output.write(remove(f.read()))

            output_filename = f"{filename.split('.')[0]}_output.png"
            return redirect(url_for('output', filename=output_filename))
        except Exception as e:
            flash('An error occurred while processing the image. Please try again.')
            return redirect(url_for('index'))
    else:
        flash('Invalid file format. Please upload a JPG, JPEG, or PNG file.')
        return redirect(url_for('index'))

@app.route('/output/<filename>')
def output(filename):
    return render_template('result.html', filename=filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
