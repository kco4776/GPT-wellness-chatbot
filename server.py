import time

import torch
from flask import Flask, render_template, request, Response, make_response
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    GPT2LMHeadModel
)
from queue import Queue, Empty
import threading

requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

U_TKN = '<usr>'
S_TKN = '<sys>'
SENT = '<unused1>'
EOS = '</s>'
PAD = '<pad>'

nlu_tokenizer = AutoTokenizer.from_pretrained('kco4776/soongsil-bert-wellness')
nlu_model = AutoModelForSequenceClassification.from_pretrained('kco4776/soongsil-bert-wellness')
nlg_tokenizer = AutoTokenizer.from_pretrained('kco4776/kogpt-chat')
nlg_model = GPT2LMHeadModel.from_pretrained('kco4776/kogpt-chat')
print('model load!')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
nlu_model.to(device)
nlg_model.to(device)

app = Flask(__name__, template_folder="./templates/")


def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            for req in requests_batch:
                req['output'] = generation(req['input'])


# Thread
threading.Thread(target=handle_requests_by_batch).start()


def generation(seq, max_len=48):
    try:
        seq = seq.strip()

        # NLU
        nlu_ids = nlu_tokenizer.encode(seq, return_tensors='pt').to(device)
        nlu_out = nlu_model(nlu_ids).logits
        prob = torch.softmax(nlu_out, dim=-1)
        nlu_label = torch.argmax(prob).item()

        # NLG
        answer = ""
        count = 0
        while True:
            nlg_ids = nlg_tokenizer.encode(SENT + str(nlu_label) + U_TKN + seq + S_TKN + answer,
                                           return_tensors='pt').to(device)
            nlg_out = torch.argmax(nlg_model(nlg_ids).logits, dim=-1).squeeze()
            gen = nlg_tokenizer.convert_ids_to_tokens(nlg_out)
            if count > max_len or gen[-1] == EOS or gen[-1] == PAD:
                break
            answer += gen[-1].replace('▁', ' ')
            count += 1
        return answer
    except Exception as e:
        print(e)
        return 500


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/chat', methods=['POST'])
def get_response():
    user_input = request.form['msg']
    if requests_queue.qsize() > BATCH_SIZE:
        return {'error': 'Too many requests'}, 429
    try:
        text = request.form['msg']
    except Exception:
        return Response('fail', status=400)

    req = {'input': text}
    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)
    return req['output']


@app.route("/healthz", methods=["GET"])
def healthCheck():
    return "", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)
