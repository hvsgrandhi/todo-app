import React from 'react';
import { useKeycloak } from '@react-keycloak/web';
import { ApolloProvider } from '@apollo/client';
import client from './apollo';
import ToDoList from './ToDoList';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Success from './Success';
import Cancel from './Cancel';


function App() {
  const { keycloak, initialized } = useKeycloak();

  if (!initialized) {
    return <div>Loading Keycloak...</div>;
  }

  if (!keycloak.authenticated) {
    keycloak.login();
    return <div>Redirecting to login...</div>;
  }

  return (
    <ApolloProvider client={client}>
    <Router>
      <Routes>
        <Route path="/" element={<ToDoList />} />
        <Route path="/success" element={<Success />} />
        <Route path="/cancel" element={<Cancel />} />
      </Routes>
    </Router>
  </ApolloProvider>
  );
}

export default App;
