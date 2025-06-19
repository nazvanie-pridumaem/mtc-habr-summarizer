up-gpu:
	docker-compose up --build frontend backend-gpu

up-cpu:
	docker-compose up --build frontend backend-cpu

down:
	docker-compose down

logs:
	docker-compose logs -f

rebuild-gpu:
	docker-compose down
	docker-compose up --build frontend backend-gpu

rebuild-cpu:
	docker-compose down
	docker-compose up --build frontend backend-cpu
