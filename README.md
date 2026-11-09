# Country Development Explorer

A data dashboard and CLI application for exploring development indicators of over 200 countries using the World Bank Open Data API.

## Purpose

Researchers, students, and analysts have to look up and compare development data (population, GDP, life expectancy, etc.) across countries. The app allows users to search for a country, choose an indicator, and view the data in the web browser or terminal. The app is to help users with data and not for entertainment.

## Live Demo

Website (via load balancer): https://3-87-66-241.sslip.io

## Credentials

- No API key is required. The World Bank API is public.

- There is no login, therefore, no credentials are required.

## Project Structure

```
country-explorer/
├── index.html #Web Dashboard (Frontend)
├── cli_app.py # Python Command Line Interface
├── README.md # Documentation
└── .gitignore # Git ignore file
```

## Local Execution

### Web App

1. Clone the repository

    ```bash

    git clone https://github.com/Ntwali-creator/country-explorer.git

    cd country-explorer

    ```

2. Open index.html in a web browser.

3. Enter a country name, choose an indicator and click Search.

### CLI App

Requires Python 3 and the 'requests' library

    ```bash
    pip install requests
    python3 cli_app.py
    ```

Choose a country to search for data or choose to compare two countries.

## Deployment

The app has been deployed to three servers:

| Server | Role | IP |
|--------|------|----|
| web-01 | Nginx web server | 3.82.191.8 |
| web-02 | Nginx web server | 35.176.246.92 |
| lb-01 | Haproxy load balancer (HTTPS) | 3.87.66.241 |

> Server IPs can change if the servers are re-provisioned. Check the Web Infrastructure dashboard before connecting.

Web servers (web-01 and web-02)

Run the following on each server:

sudo apt update && sudo apt install -y nginx git

cd ~ && git clone https://github.com/Ntwali-creator/country-explorer.git

Edit the default Nginx configuration:

sudo tee /etc/nginx/sites-available/default > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /home/ubuntu/country-explorer;
    index index.html;

    server_name _;

    location ~ /\.git {
        deny all;
    }

    location / {
        add_header X-Served-By $hostname;
        try_files $uri $uri/ =404;
    }
}
EOF

Make the target directories read/writable by nginx. Then test and reload nginx:

sudo chmod 755 /home/ubuntu && sudo chmod 755 /home/ubuntu/country-explorer
sudo nginx -t && sudo systemctl reload nginx

curl -I http://localhost

- add_header X-Served-By $hostname shows which server answered the request.

- location ~ /\.git { deny all; } tells Nginx to not serve the repository's .git folder.

HTTPS Certificate (lb-01)

Because Let's Encrypt only issues certificates to hostnames and not to bare IPs, the free hostname 3-87-66-241.sslip.io (which resolves to 3.87.66.241) is used.

sudo apt install -y certbot
sudo systemctl stop haproxy
sudo certbot certonly --standalone -d 3-87-66-241.sslip.io --agree-tos -m <your-email> --non-interactive
sudo mkdir -p /etc/haproxy/certs
```
sudo bash -c 'cat /etc/letsencrypt/live/3-87-66-241.sslip.io/fullchain.pem /etc/letsencrypt/live/3-87-66-241.sslip.io/privkey.pem > /etc/haproxy/certs/site.pem'

sudo chmod 600 /etc/haproxy/certs/site.pem

HAProxy requires the certificate and private key to be in a single PEM file. The files in /etc/letsencrypt must be removed from source control as they are automatically generated.

Certificate expiry and renewal: the certificate expires on 2027-02-07. To renew:

1. Stop HAproxy service: sudo systemctl stop haproxy
2. Renew certificate using the certbot service
3. Combine certificate and private key using the following command: sudo bash -c 'cat /etc/letsencrypt/live/3-87-66-241.sslip.io/fullchain.pem /etc/letsencrypt/live/3-87-66-241.sslip.io/privkey.pem > /etc/haproxy/certs/site.pem'
4. Restart the HAproxy service: sudo systemctl start haproxy

3. Load balancer (lb-01)

Configuration of HAproxy: /etc/haproxy/haproxy.cfg

```haproxy

global

    ssl-default-bind-options no-sslv3

    tune.ssl.default-dh-param 2048

    log /dev/log local0

    maxconn 4096

    user haproxy

    group haproxy

    daemon

defaults

    log global

    mode http

    option httplog

    timeout connect 5000

    timeout client 50000

    timeout server 50000

frontend http_front

    bind *:80

    http-request redirect scheme https code 301 unless { ssl_fc }

    default_backend http_back

frontend https_front

    bind *:443 ssl crt /etc/haproxy/certs/site.pem

    default_backend http_back

backend http_back

    balance roundrobin

    server web-01 3.82.191.8:80 check

    server web-02 35.176.246.92:80 check

```

Configure and start HAproxy:

```bash

haproxy -c -f /etc/haproxy/haproxy.cfg

systemctl start haproxy

```

The same configuration is in the alu-webstack repository in https_ssl/.

4. Verification

Check both web servers are serving app:

```bash

curl -s http://3.82.191.8 | grep -i "<title>"

curl -s http://35.176.246.92 | grep -i "<title>"

```

Check HTTP redirects to HTTPS:

```bash

curl -sI http://3-87-66-241.sslip.io | head -3

```

Check traffic alternates between servers:

```bash

for i in 1 2 3 4 5 6; do curl -sI https://3-87-66-241.sslip.io | grep -i x-served-by; done

```

x-served-by values alternate between web-01 and 7163-web-02.

The World Bank Open Data API provides programmatic access to its public data. Authentication is not required. The data is published by the World Bank and is attributed in the footer of the Web App as well as in the CLI code comments.

2. Issues Encountered and Solutions:

1. The World Bank API uses 2 letter country codes (e.g. RW for Rwanda) while users type full country names (e.g. Rwanda).

    Solution: The app fetches the full country list at start up, maps the typed country name to its code and then sends the request to the World Bank API.

2. Port conflict on the load balancer. HAProxy was not able to bind to port 80 because Nginx was using port 80 on lb-01.

    Solution: Nginx was stopped and disabled on lb-01 (sudo service nginx stop).

3. SSH “Permission denied (publickey)” on web-02. Web-02 was reprovisioned with a new IP and was only trusted to a different key then the one trusted by web-01.

    Solution: Each key was tried one at a time with “ssh -i <key>” and the one web-02 trusted was recorded. Per-server key trust was set in “~/.ssh/config”.

4. Nginx could not read the application files. /home/ubuntu was not traversable by www-data.

    Solution: chmod 755 /home/ubuntu and chmod 755 the app directory.

5. Browsers and curl could not accept the self-signed certificates.

    Solution: A trusted Let’s Encrypt certificate was retrieved for a hostname of sslip.io with certbot. This required a temporary stop of HAProxy to free up port 80.

The .git folder was publicly readable. Requests to /.git/config returned 200.
I added location ~ /\.git { deny all; } to the Nginx config on both servers.

## Credits

- Data: [World Bank Open Data](https://data.worldbank.org/)
- Free hostname for HTTPS: [sslip.io](https://sslip.io)
- Certificates: [Let's Encrypt](https://letsencrypt.org/) via [Certbot](https://certbot.eff.org/)
- Web server and load balancer: [Nginx](https://nginx.org/) and [HAProxy](https://www.haproxy.org/)
