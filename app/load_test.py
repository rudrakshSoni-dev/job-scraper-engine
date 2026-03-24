import threading
import requests

def hit():
    requests.post("http://localhost:8000/search", json={
        "query": "nodejs",
        "location": "india"
    })

threads = [threading.Thread(target=hit) for _ in range(10)]

for t in threads: t.start()
for t in threads: t.join()