# Home Assignment – Streaming & Mobile Automation

## Overview
This project implements a minimal automation framework with two layers:

1. **Streaming validation** using a mock HLS server  
2. **Mock mobile testing** simulating the Nanit app flow (Welcome → Login → Live Stream)

Both layers run under pytest.

---

## Running the Mock Streaming Server
Start the server in a separate terminal:

```
python mock_services/mock_streaming_server.py
```

Server runs on:
```
http://localhost:8082
```

Endpoints:
- `/health`
- `/stream.m3u8`
- `/segment1.ts` → `/segment5.ts`
- `/control/network/<condition>`

---

## Project Structure
```
infra/
  streaming/
  mobile/
  http/
tests/
mock_services/
config/
```

---

## Installation
```
pip install -r requirements.txt
```

---

## Running Tests
```
pytest -v
```

HTML report:
```
reports/report.html
```

---

## What’s Implemented
**Streaming Layer**
- Health metrics retrieval  
- Manifest and segment fetch  
- Network condition switching  
- Latency comparison tests  

**Mobile Layer**
- Mock MobileSession  
- Cross-platform element resolver  
- Page objects (Welcome, Login, LiveStream)  
- Login flow test  

**E2E**
- Mobile login → live stream  
- Backend streaming health check  
- Network degradation validation  
