# this_is_an_app_attack___this_IS_app_attack
Framework for attacking _any_ web app! Probably only UK folks will get the joke ;-)

P.S. Neil Buchanan _is_ Banksy!

# Overview

This Flask application was designed to automatically launch attacks against web applications.

This is not majorly sophisticated (yet!) but was conceived to have a one-stop-shop launchpad to perform web app security demos.

# Installation

This is based on Flask/Python. Firstly install the required packages as per requirements.txt e.g.

`pip3 install -r requirements.txt`

Set an environment variable "WEB_STEALER_BASE_API" to be your API gateway base URL (more on that in the pre-reqs section later).

Then to run locally:

`python3 -m flask run`

Then navigate to your browser to localhost on the Flask server port (usually 5000). Ensure you have outbound connectivity of course!

To deploy fully / publicly there are many methods, ranging from Heroko to Cloud Service Providers. One example is using GCP's App Engine: https://cloud.google.com/appengine/docs/standard/python3/building-app

# Features

## Prerequisites

Reverse shell and cookie stealing will require some additional services you will need to set up.

### Reverse shell

Check the instructions under the shellcode folder. You'll need a Linux machine running Metasploit.

This machine needs to be connectable from your target server. E.g. give it an elastic IP (AWS). Ensure you have opened the relevant port (30000 in this example - you can change it).

### Cookie Stealer

There is probably a simpler way to get this working, but I love all things cloud-native and try not to use servers where possible. For that reason I created an AWS API Gateway and DynamoDB table.

I have exported a Swagger (with AWS extension) file available in the **docs** folder. **Please note** I have anonymised the role ARN - you'll need to update that. The role basically needs access to your DynamoDB table.

For DynamoDB itself - there is a screenshot under the **docs** folder. I have column "timestamp" but this is actually to hold a UUID. This is a legacy feature from early dev. I would have had to create a new DynamoDB table which I didn't have time to do.

## Portal (Main) Page

The landing page (server root) is the main part of the app. This will launch various attacks against the web app specified.

**Currently only DVWA is implemented**. The long term goal is to make the app modular by having server 'profiles' and even potentially having the ability to enter custom payloads.

**Currently the User-Agent has no effect**. I had an issue maintaining the web app security session cookie in Python Requests when using anything _other_ than the default User-Agent. Still need to debug.

Simply enter the URL and click attack. The app will stay in a loading state until completed, and the attack output will be displayed on the right panel.

If the attack cannot complete, then a famous movie reference will pop up ;-)

If the attack was successful, output will appear on the right-panel. **Note the cookie UUID if you intend on replaying later**

## Cookie Replay

On this section you enter a UUID of a stolen cookie (either from the main attack section, or by querying your API gateway).

When entered, click the Get Cookies button. That will query your API gateway and grab all the details! If successful you'll see the cookies on the right panel, and the button changes to Blast Off.

When clicking Blast Off it will attempt to access the target server using the supplied cookies.

**Raw HTML will be returned**, this is a work in progress to return rendered HTML but for now simply look for the title or body. If unsuccessful you'll get the log in page. If successful you'll get the 'authenticated' page.

## Scripts

This page is purely there for some notes when performing the demo. I'll leave these instructions as is but if they're useful this is a description of what I was doing:

- API attack: in sock-shop (https://microservices-demo.github.io/) when you have shell access you can perform an East-West attack by contacting the API to grab a user's card details.

- Kubernetes attack: from shell access - download and execute kubectl to trigger Prisma Cloud K8S attack detection.

- Scaling an app: this is to demonstrate Prisma Cloud WAAS scaling with an app.

# Bugs / Limitations

- Changing the user-agent currently has issues, so the selector is not implemented yet.
- Only DVWA is implemented currently.
- Cookie reply output is bare HTML.