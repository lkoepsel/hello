from flask import Flask, request, render_template

app = Flask(__name__)

# List to store dictionaries of received texts and IP addresses
received_data = []


@app.route('/receive', methods=['POST'])
def receive_text():
    global received_data
    text = request.form['text']
    ip = request.remote_addr
    received_data.append({'text': text, 'ip': ip})
    print(f"Received text: {text} from IP: {ip}")
    return 'Data received successfully', 200


@app.route('/', methods=['GET'])
def display_text():
    return render_template('index.html', received_data=received_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
