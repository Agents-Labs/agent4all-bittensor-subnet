# Praison AI Call Docker

1. Build the Docker image:
```
docker build -t agent4all-call .
```

2. Run the container:
```
docker run -d -p 8090:8090 agent4all-call -e OPENAI_API_KEY=your_api_key_here
```

Make sure to replace your_api_key_here with your actual OpenAI API key.