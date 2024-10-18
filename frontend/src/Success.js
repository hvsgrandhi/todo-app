// src/Success.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Typography, CircularProgress, Box } from '@mui/material';

function Success() {
  const navigate = useNavigate();
  const [counter, setCounter] = useState(5);

  useEffect(() => {
    // Update the counter every second
    const timer =
      counter > 0 && setInterval(() => setCounter(counter - 1), 1000);

    // Redirect when counter reaches 0
    if (counter === 0) {
      navigate('/');
    }

    return () => clearInterval(timer);
  }, [counter, navigate]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="80vh"
    >
      <Typography variant="h4" gutterBottom>
        Payment Successful!
      </Typography>
      <Typography variant="body1">
        Redirecting to the main page in {counter} seconds...
      </Typography>
      <CircularProgress sx={{ mt: 2 }} />
    </Box>
  );
}

export default Success;
