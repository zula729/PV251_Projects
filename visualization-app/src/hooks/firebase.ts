import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// Tvůj konfigurační objekt z Firebase konzole
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "visualization-88a6b.firebaseapp.com",
  databaseURL: "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "visualization-88a6b",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};

// Inicializace aplikace
const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);