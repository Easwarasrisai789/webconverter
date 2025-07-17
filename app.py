# app.py
from flask import Flask, render_template, request, send_file, redirect, url_for
import qrcode
import os
from pytube import YouTube
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# QR Code Generator
@app.route('/qr', methods=['GET', 'POST'])
def qr():
    if request.method == 'POST':
        data = request.form['data']
        img = qrcode.make(data)
        path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'qr_code.png')
        img.save(path)
        return send_file(path, as_attachment=True)
    return render_template('qr.html')

# YouTube Downloader
@app.route('/youtube', methods=['GET', 'POST'])
def youtube():
    if request.method == 'POST':
        link = request.form['link']
        yt = YouTube(link)
        stream = yt.streams.get_highest_resolution()
        path = os.path.join(app.config['DOWNLOAD_FOLDER'], secure_filename(yt.title) + ".mp4")
        stream.download(filename=path)
        return send_file(path, as_attachment=True)
    return render_template('youtube.html')

# PDF Merger & Splitter
@app.route('/pdf', methods=['GET', 'POST'])
def pdf():
    if request.method == 'POST':
        action = request.form['action']
        files = request.files.getlist('pdf_files')
        filenames = []
        for f in files:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            filenames.append(filepath)

        if action == 'merge':
            merger = PdfMerger()
            for pdf in filenames:
                merger.append(pdf)
            merged_path = os.path.join(app.config['DOWNLOAD_FOLDER'], 'merged.pdf')
            merger.write(merged_path)
            merger.close()
            return send_file(merged_path, as_attachment=True)

        elif action == 'split' and len(filenames) == 1:
            reader = PdfReader(filenames[0])
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f'page_{i+1}.pdf')
                with open(output_path, 'wb') as f:
                    writer.write(f)
            return redirect(url_for('download_split'))
    return render_template('pdf.html')

@app.route('/download_split')
def download_split():
    files = os.listdir(app.config['DOWNLOAD_FOLDER'])
    pdfs = [f for f in files if f.startswith("page_")]
    return render_template('download_split.html', files=pdfs)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
