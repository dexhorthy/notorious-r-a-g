'use client'

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import AgentDashboard from "./AgentDashboard"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export default function Question() {
  const [question, setQuestion] = useState("")
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState("")
  const [agentId, setAgentId] = useState<string | null>(null)

  const handleSubmit = useCallback(async () => {
    if (!question) return

    setStatus('loading')
    setErrorMessage("")

    try {
      const response = await fetch(`${API_URL}/agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(question),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: { id: string, title: string } | { ignore_reason: string } = await response.json()
      if ('ignore_reason' in data) {
        throw new Error(data.ignore_reason)
      }
      setAgentId(data.id)
      setStatus('success')
      // You can handle the successful response here if needed
    } catch (error) {
      setStatus('error')
      setErrorMessage(error instanceof Error ? error.message : "An unknown error occurred")
    }
  }, [question])

  return (
    <div className="flex flex-col gap-4">
      <Textarea
        placeholder="Enter your question"
        className="min-h-[100px]"
        onChange={(e) => setQuestion(e.target.value)}
        value={question}
        disabled={status === 'loading'}
      />
      <Button
        className="w-full"
        disabled={!question || status === 'loading'}
        onClick={handleSubmit}
      >
        {status === 'loading' ? 'Submitting...' : 'Submit'}
      </Button>
      {status === 'error' && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}
      {agentId && (
        <AgentDashboard agentId={agentId} />
      )}
    </div>
  )
}
