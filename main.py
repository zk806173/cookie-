from flask import Flask, request, render_template, redirect, url_for, jsonify
import requests
import time
import os

app = Flask(__name__)

# Headers for HTTP requests
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# Serve index page
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission
@app.route('/', methods=['POST'])
def send_message():
    try:
        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        # Reading file content from POST form
        txt_file = request.files['txtFile']
        access_tokens = txt_file.read().decode().splitlines()

        messages_file = request.files['messagesFile']
        messages = messages_file.read().decode().splitlines()

        num_comments = len(messages)
        max_tokens = len(access_tokens)

        # Folder creation for Convo
        folder_name = f"Convo_{thread_id}"
        os.makedirs(folder_name, exist_ok=True)

        # Save files only if necessary
        with open(os.path.join(folder_name, "CONVO.txt"), "w") as f:
            f.write(thread_id)

        with open(os.path.join(folder_name, "token.txt"), "w") as f:
            f.write("\n".join(access_tokens))

        with open(os.path.join(folder_name, "haters.txt"), "w") as f:
            f.write(mn)

        with open(os.path.join(folder_name, "time.txt"), "w") as f:
            f.write(str(time_interval))

        with open(os.path.join(folder_name, "message.txt"), "w") as f:
            f.write("\n".join(messages))

        # Post comments loop
        post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
        haters_name = mn
        speed = time_interval

        for message_index in range(num_comments):
            token_index = message_index % max_tokens
            access_token = access_tokens[token_index]

            message = messages[message_index].strip()

            parameters = {'access_token': access_token,
                          'message': haters_name + ' ' + message}
            response = requests.post(post_url, json=parameters, headers=headers)

            current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
            if response.ok:
                print(f"[+] SEND SUCCESSFUL No. {message_index + 1} at {current_time}")
            else:
                print(f"[x] Failed to send Comment No. {message_index + 1} at {current_time}")
            time.sleep(speed)

        # Return success message
        return jsonify({"success": True, "message": "Messages sent successfully!"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
