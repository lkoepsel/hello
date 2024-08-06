from flask import Flask, request, render_template_string

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
    return render_template_string('''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Display Text</title>
          </head>
          <body>
            <div style="text-align: left; margin-top: 50px;">
              <h1>Information</h1>
              <p>Find your hostname below to enter <em>ssh pi10C@IP_Address</em> in the terminal on your computer:</p>
              <ul>
                {% for data in received_data %}
                  <li><strong>Hostname:</strong> {{ data.text }} <strong>IP_Address:</strong> {{ data.ip }}</li>
                {% endfor %}
              </ul>
            </div>
          </body>
        </html>
    ''', received_data=received_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000, debug=True)
