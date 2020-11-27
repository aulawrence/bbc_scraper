#!/bin/sh
source /home/ec2-user/miniconda3/etc/profile.d/conda.sh && \
  conda activate bbc_scraper && \
  python main.py &
