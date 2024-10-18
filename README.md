# ToDo App with Authentication, Authorization, and Payment Integration

This project is a ToDo application with authentication and authorization using **Keycloak**, a backend built with **Flask**, a frontend built with **React**, and payment processing using **Stripe**. It allows users to create, update, and delete ToDo items, and offers a Pro tier with additional features like image uploads.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Clone the Repository](#clone-the-repository)
  - [Backend Setup](#backend-setup)
    - [Create a Virtual Environment](#create-a-virtual-environment)
    - [Install Dependencies](#install-dependencies)
    - [Environment Variables](#environment-variables)
    - [Initialize the Database](#initialize-the-database)
  - [Keycloak Configuration](#keycloak-configuration)
    - [Run Keycloak with Docker](#run-keycloak-with-docker)
    - [Keycloak Setup](#keycloak-setup)
    <!-- - [Run the Backend Server](#run-the-backend-server) -->
  - [Frontend Setup](#frontend-setup)
    - [Install Dependencies](#install-dependencies-1)
    - [Environment Variables](#environment-variables-1)
    - [Run the Frontend Server](#run-the-frontend-server)

- [Stripe Configuration](#stripe-configuration)
  - [Create a Stripe Account](#create-a-stripe-account)
  - [Obtain API Keys](#obtain-api-keys)
  - [Create a Product and Price](#create-a-product-and-price)
  - [Set Up Webhook Endpoint](#set-up-webhook-endpoint)
- [Running the Application](#running-the-application)
---

## Features

- User authentication and registration via Keycloak.
- Role-based access control (Standard User and Pro User).
- Create, update, and delete ToDo items.
- Pro users can upload images with their ToDo items.
- Payment integration with Stripe to upgrade users to Pro.
- Responsive frontend using React and Material-UI.

## Prerequisites

- **Python 3.9**
- **Node.js 14+ and npm**
- **Docker (for running Keycloak)**
- **Git (for version control)**

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/hvsgrandhi/todo-app.git
cd todo-app
```

## Backend Setup
### Create a Virtual Environment

```bash
cd backend
py -3.9 -m venv venv39
```

### Activate the virtual environment:

#### On Windows:
```bash
venv39\Scripts\activate
```

#### On Unix or MacOS:
```bash
venv39\Scripts\activate
```

### Install Dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables:
```bash
# .env (backend)
DATABASE_URL=sqlite:///todo.db

# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080/
KEYCLOAK_REALM_NAME=todo-app
KEYCLOAK_CLIENT_ID=todo-backend
KEYCLOAK_CLIENT_SECRET=your_keycloak_client_secret

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_ENDPOINT_SECRET=your_stripe_webhook_secret
STRIPE_PRICE_ID=your_stripe_price_id

# Keycloak Admin Credentials (for assigning roles)
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```
Note: Replace ``` your_keycloak_client_secret, your_stripe_secret_key, etc.```, with your actual credentials.

### Initialize The Database:
```bash
python init_db.py
```

## Keycloak Configuration

### Run Keycloak with Docker

Ensure Docker is installed and running.

```bash
docker-compose up -d
```
Note: Even after Docker container is created, it may take time for 8080 port to get activated

### Keycloak Setup

#### Access the Keycloak Admin Console:

- Open a browser and navigate to http://localhost:8080/
- Log in with:
  - Username: **admin**
  - Password: **admin**
- Create a New Realm
  - Click on **"Add Realm"** and name it **todo-app**
- Enable User Registration
  - Go to Realm Settings > Login tab
  - Enable User Registration by toggling it ON
- Create Clients
  - Frontend Client (todo-frontend):
    ```bash
    Client ID: todo-frontend
    Access Type: public
    Root URL: http://localhost:3000
    Valid Redirect URIs: http://localhost:3000/*
    Web Origins: http://localhost:3000
    ```
  - Backend Client (todo-backend):
    ```bash
    Client ID: todo-backend
    Access Type: confidential
    Root URL: http://localhost:5000
    Valid Redirect URIs: http://localhost:5000/*
    Turn On Client Authentication
    Select "Service Accounts Roles"
    Credentials: Copy the Client Secret and paste it into your backend .env file.
    ```
- Create Realm Roles
  - Go to Realm Roles and create a role named **"pro_user"**

- Create a Test User
  - Go to Users > Add User
    - Fill out Username, Email *(Mandatory)*
    - Fill out First Name, Last Name *(Not Mandatory over here)*
    - Turn ON Email Verified *(Optional)*
  - Click on the created User
    - Go to Credentials Tab
    - Click on "Set Password"
    - Make sure to **Turn Off** "Temporary Password" *(Mandatory)*

## Stripe Configuration

### Create a Stripe Account
[Stripe Dashboard](https://dashboard.stripe.com/test/dashboard)

Sign up at Stripe and log in to the Dashboard and make sure to enable **Test Mode**

### Obtain API Keys

- Go to Developers > API Keys
- Use the Test Mode keys.
- Copy the Publishable Key and Secret Key.
- Paste them into your **.env**(Backend) files ```(STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY)```

### Create a Product and Price

#### Create a Product
- Click on Product Catalog on Left sidebar and create product 
- Name it Pro_Todo *(any name)*
- Select one-off
- Enter random Amount in INR
- Click Add Product
- Copy the Price ID and paste it into your **backend .env** file ```(STRIPE_PRICE_ID)```


### Set Up Webhook Endpoint

[Download Stripe CLI](https://github.com/stripe/stripe-cli/releases/download/v1.21.9/stripe_1.21.9_windows_x86_64.zip)


- Start Stripe CLI to Forward Events:
 ```bash
stripe login
stripe listen --forward-to localhost:5000/webhook
```
- Copy the Webhook Signing Secret:

```bash
After running the above command, you'll see a webhook signing secret. Copy it and paste it into your backend .env file (STRIPE_ENDPOINT_SECRET).
```

## Backend Setup(Continue)

### Run the Backend Server
 ```bash
 python app.py
```

## Frontend Setup
 ```bash
 cd ../frontend
```

### Install Dependencies

```bash
npm install
```
### Environment Variables

Create a .env file in the frontend directory with the following content:

```bash
# .env (frontend)
REACT_APP_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
REACT_APP_KEYCLOAK_URL=http://localhost:8080/
REACT_APP_KEYCLOAK_REALM=todo-app
REACT_APP_KEYCLOAK_CLIENT_ID=todo-frontend
GENERATE_SOURCEMAP=false
```

### Run the Frontend Server

```bash
npm start
```

## Running the Application

Ensure all servers are running:

- **Keycloak: Via Docker (docker-compose up -d) at port 8080**
- **Backend: python app.py at port 5000**
- **Frontend: npm start in the frontend directory at port 3000**
- **Stripe CLI: stripe listen --forward-to localhost:5000/webhook**

### Access the Application

Open ```http://localhost:3000``` in your browser.

#### Register a New User:
Click on Register and create a new account.

#### Test Standard User Features:
Add, update, and delete ToDo items without images.

#### Upgrade to Pro User:
- Click on Upgrade to Pro
- Complete the payment using test card details:
  - Card Number: 4242 4242 4242 4242
  - Expiry Date: Any future date
  - CVC: Any 3-digit number
  - Address: Any Indian address Required *(due to Indian regulations)*

#### Test Pro User Features
- After successfull payment, you will be redirected to main page.
- You should now see options to upload images with your ToDo items.

