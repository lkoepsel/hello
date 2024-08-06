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
            <link rel="stylesheet" type="text/css" href="/static/mvp.css">
            <title>Lab 10C Hostnames</title>
          </head>
          <body>
            <main>
              <h1>Lab 10C Hostnames</h1>
              <h2>Instructions</h2>
              <ol>
              <li>Find your hostname below</li>
              <li>Get the corresponding <em>IP Address</em></li>
              <li>In your terminal window, enter <em>ssh pi10C@IP Address</em></li>
              </ol>
              <table>
                <thead>
                  <tr>
                    <th scope="col">Hostname</th>
                    <th scope="col">IP Address</th>
                  </tr>
                </thead>
                <tbody>
                {% for data in received_data %}
                <tr>
                  <th scope="row">{{ data.text }}</th>
                  <td>{{ data.ip }}</td>
                </tr>
                {% endfor %}
                  </tbody>
                </table>
                <p><strong>Example:</strong> <em>ssh pi10C@172.2.24.210</em></p>
          </main>
          </body>
        </html>
    ''', received_data=received_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
