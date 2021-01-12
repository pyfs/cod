clean:
	rm -rf db.sqlite3
	rm -rf account/migrations
	rm -rf auth_token/migrations
	rm -rf data_source/migrations
	rm -rf converge/migrations
	rm -rf message/migrations
	rm -rf project/migrations
	rm -rf event/migrations
	rm -rf silence/migrations
	rm -rf delivery/migrations
	rm -rf send_template/migrations
	rm -rf receive_strategy/migrations

make:
	python manage.py makemigrations account auth_token data_source converge project silence event message delivery send_template receive_strategy
	python manage.py migrate
	python manage.py createsuperuser 
