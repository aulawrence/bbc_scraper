# BBC Scraper
From the sitemap, extract recent BBC News articles and store them into a hosted MongoDB database. The server provides API access for simple keyword/ text queries.

## Setup environment
1. Install Anaconda/ Miniconda
2. Run `conda env create -f environment.yml`

## Run unit tests
1. Run `python -m unittest discover -p "test_*.py"`

## Run scraper
1. Configure [config.py](config.py)
2. Activate the environment with `conda activate bbc_scraper`
3. Run `python main.py`

## Run server
1. Configure firewall rules if needed
2. Run `gunicorn -w 4 -b 0.0.0.0:5050 server:app` to start a server with 4 workers and bound to a socket listening on port 5050

## API
The API is documented in [api.md](api.md)
