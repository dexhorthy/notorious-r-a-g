// hooks/useFirebaseListener.js
import { useState, useEffect } from 'react';
import { collection, query, onSnapshot } from 'firebase/firestore';
import { db } from '../firebase';

type Message = {
    user: string;
    message: string;
}
export type StateName = 'running' | 'completed' | 'failed' | 'cancelled';
type InitialState = Message[];
type FinalState = string | null;

interface Action {
    type: string;
    content: string;
}

interface AgentState {
    state: StateName;
    initial_state: InitialState;
    actions: Action[];
    final_state: FinalState;
}


export type DBRecord = {
    id: string;
    data: AgentState
}

export function useFirebaseListener(collectionName: string) {
  const [data, setData] = useState<DBRecord[]>([]);

  useEffect(() => {
    const q = query(collection(db, collectionName));
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const items: DBRecord[] = [];
      querySnapshot.forEach((doc) => {
        items.push({ id: doc.id, data: doc.data() as AgentState });
      });
      setData(items);
    });

    return () => unsubscribe();
  }, [collectionName]);

  return data;
}