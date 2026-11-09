# Country Development Explorer

A professional data dashboard and CLI tool that visualizes and explores the development indicators of over 200 countries using the World Bank Open Data API.

## 🎯 Purpose
The main purpose of this application is to provide a platform for researchers, students and analysts to search, filter and compare various development data around the world. This goes beyond the purpose of mere entertainment to provide a tool for those interested in exploring data.

## 🔗 Live Demo
- **Load Balancer URL:** `http://3.87.66.241`

## 🛠️ Project Structure
```text
country-explorer/
├── index.html          # Web Dashboard (Frontend)
├── cli_app.py          # Python Command Line Interface
├── README.md           # Documentation
└── .gitignore          # Git ignore file
💻 Local Execution
Running the Web App
Open the index.html file in any modern web browser.

Enter a country name, select an indicator and click Search.

Running the CLI App
Ensure you have Python 3 and the requests library installed:

bash
pip install requests
Run the CLI application:

bash
python3 cli_app.py
Follow the on-screen menu to search for a country or to compare two countries.

🌐 Deployment Architecture
The application is deployed on a very available web infrastructure that consists of three servers:

web-01 (3.82.191.8): Nginx Web Server

web-02 (3.82.162.246): Nginx Web Server

lb-01 (3.87.66.241): HAProxy Load Balancer

Step-by-Step Deployment Process
1. Server Provisioning & Nginx Setup (web-01 & web-02)
Installed Nginx on both servers and configured them to serve the static index.html file. The configuration file /etc/nginx/sites-available/default was updated with:

nginx
server {
    listen 80 default_server;
    root /home/ubuntu/country-explorer;
    index index.html;
    server_name _;
    location / {
        try_files $uri $uri/ =404;
    }
}

2. Load Balancer Configuration (lb-01)

Haproxy was installed on lb-01 to balance the load. The configuration file, /etc/haproxy/haproxy.cfg, was modified to include a round-robin configuration as follows:

haproxy

frontend http_front

bind *:80

default_backend http_back

backend http_back

balance roundrobin

server web-01 3.82.191.8:80 check

server web-02 3.82.162.246:80 check

3. Verification

Distribution of the traffic between web-01 and web-02 is verified by X-Served-By header returned by the web app with each request.

🔌 API Usage and Attribution

API Used: World Bank Open Data API

Authentication: No API key is required for this public API.

Attribution: All data is provided by the World Bank. The API is credited in the footer of the web app and in the CLI code comments.

🚧 Challenges Faced & Solutions

API Country Codes vs. Names: The World Bank API uses 2-letter country codes (e.g. RW), but users prefer to type in full country names (e.g. Rwanda).

Solution: Pre-fetch of all 200+ countries is done at app startup, and the app matches the user’s input to the corresponding 2 letter code before fetching the data.

Load Balancer Port Conflict: HAProxy initially failed to bind to port 80 due to Nginx was using the same port on lb-01.

Solution: Nginx was stopped and disabled on lb-01 (sudo service nginx stop) to free port 80 for HAProxy.

🎥 Demo Video

Link: [Insert YouTube or Vimeo link here]


