from flask import Flask, render_template, request, send_file
import os
from parser import run_parser  # Импортируем функцию парсера

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        city = request.form['city']
        vacancy = request.form['vacancy']
        
        # Запуск парсера
        run_parser(city, vacancy)
        
        return render_template('result.html', city=city, vacancy=vacancy)
    return render_template('form.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

if __name__ == '__main__':
    app.run(debug=True)
