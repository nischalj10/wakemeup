# wake-me-up

The agnet takes you on a little voice adventure every morning and wakes you up feeling refreshed! a better way to wake up isn't it :D

## Steps to run in localhost

1. First install dependencies

```bash
pip3 install -r requirements.txt
```

2. Fill out the API keys in `.env`

3. In another bash, use ngrok to expose this port to public network

```bash
ngrok http 8080
```

4. Start the websocket server

```bash
python3 -m uvicorn app.server:app --reload --port=8080
```

You should see a fowarding address like
`https://dc14-2601-645-c57f-8670-9986-5662-2c9a-adbd.ngrok-free.app`, and you
are going to take the IP address, prepend it with wss, postpend with
`llm-websocket` path and use that in the [retell ai dashboard](https://beta.retellai.com/dashboard) to create a new `agent`. Now
the `agent` you created should connect with your localhost.

The custom LLM URL would look like
`wss://dc14-2601-645-c57f-8670-9986-5662-2c9a-adbd.ngrok-free.app/llm-websocket`

## credits

powered by [retell ai](https://www.retellai.com/) & [litellm](https://docs.litellm.ai/docs/)