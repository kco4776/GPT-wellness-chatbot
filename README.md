# GPT-wellness-chatbot

[![Run on Ainize](https://ainize.ai/images/run_on_ainize_button.svg)](https://ainize.web.app/redirect?git_repo=https://github.com/kco4776/GPT-wellness-chatbot)


generative-based open domain chatbot

## How-to-use
### Input example
```bash
curl -X 'POST' \
  'https://master-gpt-wellness-chatbot-kco4776.endpoint.ainize.ai/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'msg=너무 힘들다'
```

### Output example
```
 세상은 넓고 사람은 많아요.
```

### Data
- [AIhub Wellness 대화 스크립트](https://aihub.or.kr/opendata/keti-data/recognition-laguage/KETI-02-006)
- [songys/Chatbot_data](https://github.com/songys/Chatbot_data)

### References
- [koGPT2](https://github.com/SKT-AI/KoGPT2)
- [koGPT2-chatbot](https://github.com/haven-jeon/KoGPT2-chatbot)
- [SoongsilBERT](https://github.com/jason9693/Soongsil-BERT)
