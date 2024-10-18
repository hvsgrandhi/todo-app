# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_graphql import GraphQLView
from schema import schema
from database import db_session
from flask_cors import CORS
from keycloak import KeycloakOpenID, KeycloakAdmin
import stripe
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os, jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOADED_IMAGES_DEST'] = 'static/uploads'

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

keycloak_openid = KeycloakOpenID(
    server_url=os.getenv('KEYCLOAK_SERVER_URL'),
    client_id=os.getenv('KEYCLOAK_CLIENT_ID'),
    client_secret_key=os.getenv('KEYCLOAK_CLIENT_SECRET'),
    realm_name=os.getenv('KEYCLOAK_REALM_NAME')
    # verify=True
)

# keycloak_admin = KeycloakAdmin(
#     server_url=os.getenv('KEYCLOAK_SERVER_URL'),
#     realm_name=os.getenv('KEYCLOAK_REALM_NAME'),
#     client_id=os.getenv('KEYCLOAK_CLIENT_ID'),
#     client_secret_key=os.getenv('KEYCLOAK_CLIENT_SECRET'),
#     username=os.getenv('KEYCLOAK_ADMIN_USERNAME'),
#     password=os.getenv('KEYCLOAK_ADMIN_PASSWORD')
#     # verify=True
# )

# keycloak_admin = KeycloakAdmin(
#     server_url=os.getenv('KEYCLOAK_SERVER_URL'),
#     # realm_name=os.getenv('KEYCLOAK_REALM_NAME'),
#     realm_name='master',
#     username=os.getenv('KEYCLOAK_ADMIN_USERNAME'),
#     password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
#     verify=False
# )


# keycloak_admin = KeycloakAdmin(
#     server_url=os.getenv('KEYCLOAK_SERVER_URL'),
#     username=os.getenv('KEYCLOAK_ADMIN_USERNAME'),
#     password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
#     realm_name=os.getenv('KEYCLOAK_REALM_NAME'),  # This is 'todo-app'
#     user_realm_name='master',  # Admin user is in the 'master' realm
#     verify=False
# )

def get_keycloak_admin():
    """Create a fresh Keycloak admin client with each request."""
    keycloak_admin = KeycloakAdmin(
        server_url=os.getenv('KEYCLOAK_SERVER_URL'),
        username=os.getenv('KEYCLOAK_ADMIN_USERNAME'),
        password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
        realm_name=os.getenv('KEYCLOAK_REALM_NAME'),
        user_realm_name='master',
        verify=False
    )
    keycloak_admin.refresh_token()  # Refresh token on every call
    return keycloak_admin


public_key = keycloak_openid.public_key()
print(f"Public Key: {public_key}")


# Ensure 'static/uploads' directory exists
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        return None
    parts = auth.split()
    if parts[0].lower() != "bearer":
        return None
    elif len(parts) == 1:
        return None
    elif len(parts) > 2:
        return None
    token = parts[1]
    return token

# def keycloak_protect(function):
#     def wrapper(*args, **kwargs):
#         token = get_token_auth_header()
#         if token is None:
#             return jsonify({"message": "Unauthorized"}), 401
#         try:
#             # Decode token without verification to inspect contents
#             unverified_token = jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
#             print("Unverified Token Info:", unverified_token)  # Debugging

#             # Proceed with proper verification
#             public_key = keycloak_openid.public_key()
#             public_key_pem = "-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----".format(public_key)
#             token_info = keycloak_openid.decode_token(
#                 token,
#                 key=public_key_pem,
#                 options={"verify_signature": True, "verify_aud": False, "verify_exp": True}
#             )
#             request.user = token_info
#             print("Decoded Token Info:", token_info)  # Debugging
#         except Exception as e:
#             print("Token decoding error:", e)  # Debugging
#             return jsonify({"message": "Invalid token"}), 401
#         return function(*args, **kwargs)
#     wrapper.__name__ = function.__name__
#     return wrapper


def keycloak_protect(function):
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        if token is None:
            return jsonify({"message": "Unauthorized"}), 401
        try:
            # Proceed with proper verification
            public_key = keycloak_openid.public_key()
            public_key_pem = "-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----".format(public_key)
            token_info = keycloak_openid.decode_token(
                token,
                key=public_key_pem,
                options={"verify_signature": True, "verify_aud": False, "verify_exp": True}
            )
            request.user = token_info
            # Optionally, remove debugging prints in production
            # print("Decoded Token Info:", token_info)
        except Exception as e:
            print("Token decoding error:", e)  # For debugging purposes
            return jsonify({"message": "Invalid token"}), 401
        return function(*args, **kwargs)
    wrapper.__name__ = function.__name__
    return wrapper


app.add_url_rule(
    '/graphql',
    view_func=keycloak_protect(
        GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True,
            get_context=lambda: {'session': db_session, 'user': request.user}
        )
    ),
    methods=['GET', 'POST']  # Move methods parameter here
)



@app.route('/upload-image', methods=['POST'])
@keycloak_protect
def upload_image():
    user_info = request.user
    if 'pro_user' not in user_info.get('realm_access', {}).get('roles', []):
        return jsonify({"message": "Pro license required"}), 403

    if 'image' not in request.files:
        return jsonify({"message": "No image provided"}), 400

    filename = images.save(request.files['image'])
    file_url = '/static/uploads/' + filename
    return jsonify({'image_url': file_url})

@app.route('/create-checkout-session', methods=['POST'])
@keycloak_protect
def create_checkout_session():
    try:
        # Fetch username from Keycloak token (from request.user)
        customer_username = request.user.get('preferred_username')  # Fetch directly from the token
        
        if not customer_username:
            return jsonify({"error": "Username not found in token"}), 400

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': os.getenv('STRIPE_PRICE_ID'),  # Use environment variable
                'quantity': 1,
            }],
            mode='payment',
            customer_email=request.user.get('email'),  # Fetch the email from the token
            metadata={'username': customer_username},  # Automatically add username to metadata
            billing_address_collection='required',  # Add this line
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/webhook', methods=['POST'])
def webhook():
    keycloak_admin = get_keycloak_admin()  # Use fresh Keycloak client instance
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return {}, 400
    except stripe.error.SignatureVerificationError:
        return {}, 400

    # Handling specific events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Checkout Session completed:", session)

        # Get the customer username from metadata
        customer_username = session.get('metadata', {}).get('username')
        print(f"Customer username from session metadata: {customer_username}")

        if customer_username:
            try:
                # Fetch user ID directly by username
                user_id = keycloak_admin.get_user_id(customer_username)
                print(f"Fetched User ID for username {customer_username}: {user_id}")

                # Get 'pro_user' realm role
                pro_role = keycloak_admin.get_realm_role('pro_user')
                print(f"Fetched 'pro_user' role: {pro_role}")

                # Assign the 'pro_user' role to the user
                keycloak_admin.assign_realm_roles(user_id = user_id, client_id =os.getenv('KEYCLOAK_CLIENT_ID'), roles=[pro_role])
                print(f"Assigned 'pro_user' role to user with username {customer_username}")
            except Exception as e:
                print(f"Error assigning role to user with username {customer_username}: {e}")
        else:
            print("Customer username not found in session data")
    else:
        print(f'Unhandled event type {event["type"]}')

    return {"status": "success"}, 200

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
