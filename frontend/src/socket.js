import { io } from 'socket.io-client';

// Define the server URL
const SERVER_URL = 'http://localhost:5000';

// Create a single, shared socket connection
const socket = io(SERVER_URL, {
  autoConnect: false // We will connect manually in our main App component
});

export default socket;