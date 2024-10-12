// firebaseConfig.js
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyDDIiReCPkjMrG9Ms6ihS-0x1ft2lrUi_I",
  authDomain: "notorious-rag.firebaseapp.com",
  projectId: "notorious-rag",
  storageBucket: "notorious-rag.appspot.com",
  messagingSenderId: "337725542688",
  appId: "1:337725542688:web:9e7dadda02031ef4db4745",
  measurementId: "G-7WH9VWZ9L8"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };
