runs:
	docker run --network host -p 5000:5000 myserv_img

runc:
	python3 prot1_client.py

runk:
	sudo systemctl start redis
	uvicorn key_server:app --reload --port 5050
