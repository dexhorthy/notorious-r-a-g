// hooks/useFirebaseListener.js
import { useEffect, useState } from "react"
import { collection, onSnapshot, query } from "firebase/firestore"

import { db } from "../firebase"

export type Message = {
  user_id: string
  avatar_url?: string
  message: string
}
export type StateName = "running" | "completed" | "failed" | "cancelled" | "paused"
export type InitialState = Message[] | {
    messages: Message[]
    classification: {
        intent: string
        title: string
    }
}
export type FinalState = string | null

export type RagResult = {
  result: {
    content: string
    metadata: Record<string, any>
  }[]
}

export interface Action {
  type: string
  content: string | RagResult
  create_time_ms: number
}

export interface AgentState {
  create_time_ms: Date
  update_time_ms: Date
  state: StateName
  initial_state: InitialState
  actions: Action[]
  final_state: FinalState
}

export type DBRecord = {
  id: string
  data: AgentState
}

export function useFirebaseListener(collectionName: string) {
  const [data, setData] = useState<DBRecord[]>([])

  useEffect(() => {
    const q = query(collection(db, collectionName))
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const items: DBRecord[] = []
      querySnapshot.forEach((doc) => {
        const docData = doc.data() as AgentState
        const agentState: AgentState = {
          ...docData,
          create_time_ms: new Date(docData.create_time_ms),
          update_time_ms: new Date(docData.update_time_ms),
        }
        items.push({ id: doc.id, data: agentState })
      })

      // Sort by create_time_ms
      items.sort((a, b) => {
        return a.data.create_time_ms.getTime() - b.data.create_time_ms.getTime()
      })

      setData(items)
    })

    return () => unsubscribe()
  }, [collectionName])

  return data
}
