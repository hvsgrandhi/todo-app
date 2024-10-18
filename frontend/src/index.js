import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import keycloak from './keycloak';
import { ReactKeycloakProvider } from '@react-keycloak/web';

const root = ReactDOM.createRoot(document.getElementById('root'));
const keycloakInitOptions = {
  onLoad: 'login-required',
  checkLoginIframe: false, // Add this line
};
root.render(
  <ReactKeycloakProvider authClient={keycloak} initOptions={keycloakInitOptions}>
    <App />
  </ReactKeycloakProvider>
);
