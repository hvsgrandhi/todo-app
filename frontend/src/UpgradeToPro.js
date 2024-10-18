// src/UpgradeToPro.js
import React from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { useKeycloak } from '@react-keycloak/web';
import { Button, Alert } from '@mui/material';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

function UpgradeToPro() {
  const { keycloak } = useKeycloak();

  const isProUser = keycloak.hasRealmRole('pro_user');

  const handleUpgrade = async () => {
    const stripe = await stripePromise;

    const response = await fetch('http://localhost:5000/create-checkout-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${keycloak.token}`,
      },
    });

    const session = await response.json();

    if (response.ok) {
      const result = await stripe.redirectToCheckout({
        sessionId: session.id,
      });

      if (result.error) {
        console.error(result.error.message);
      }
    } else {
      console.error(session.error);
    }
  };

  if (isProUser) {
    return (
      <Alert severity="success" style={{ marginBottom: '20px' }}>
        You are a Pro User!
      </Alert>
    );
  }

  return (
    <Button variant="contained" color="secondary" onClick={handleUpgrade}>
      Upgrade to Pro
    </Button>
  );
}

export default UpgradeToPro;
