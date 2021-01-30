build:
	docker build -t yt_feed:latest .

run:
	docker run -id --restart always -v $(shell pwd)/lock:/opt/lock -v $(shell pwd)/var:/opt/var --name yt_feed yt_feed
