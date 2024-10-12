"use client";

import Link from "next/link"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

import { siteConfig } from "@/config/site"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useState, useEffect } from 'react'
import { io, Socket } from 'socket.io-client'

export default function IndexPage() {
  const [question, setQuestion] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<string[]>([])
  const [finalMessage, setFinalMessage] = useState<string | null>(null)

  useEffect(() => {
    const newSocket = io('http://localhost:8080', {
      transports: ['websocket']
    });

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
    });

    newSocket.on('message', (data) => {
      console.log('Received message:', data);
      setMessages(prevMessages => [...prevMessages, `${data.id}: ${data.state}`]);
    });

    newSocket.on('final_answer', (data) => {
      setFinalMessage(data.answer);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const handleSubmit = () => {
    if (socket && question) {
      socket.emit('message', { text: question });
      setQuestion('');
    }
  };

  return (
    <section className="container grid items-center gap-6 pb-8 pt-6 md:py-10">
      <div className="flex max-w-[980px] flex-col items-start gap-2">
        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          <span className={`w-2 h-2 mr-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></span>
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
        <h1 className="text-3xl font-extrabold leading-tight tracking-tighter md:text-4xl">
          Notorious R.A.G.
        </h1>
        <p className="max-w-[700px] text-lg text-muted-foreground">
          A Discord bot that uses RAG to answer questions.
        </p>
      </div>
      <div className="flex gap-4">
        <Tabs defaultValue="submit-question" className="w-[400px]">
          <TabsList>
            <TabsTrigger value="submit-question">Submit Question</TabsTrigger>
            <TabsTrigger value="view-questions">View Questions</TabsTrigger>
          </TabsList>
          <TabsContent value="submit-question">
            <div className="flex flex-col space-y-4">
              <Textarea
                placeholder="Enter your question"
                className="min-h-[100px]"
                onChange={(e) => setQuestion(e.target.value)}
                value={question}
              />
              <Button onClick={handleSubmit}>
                Submit
              </Button>
              <div className="mt-4 space-y-2">
                <h3 className="font-semibold">Messages from server:</h3>
                {messages.map((msg, index) => (
                  <div key={index} className="p-2 bg-gray-100 rounded flex items-center">
                    {index === messages.length - 1 && !finalMessage ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 mr-2"></div>
                        {msg}
                      </>
                    ) : (
                      msg
                    )}
                  </div>
                ))}
              </div>
            </div>
              {finalMessage && (
                <div className="mt-4 p-4 bg-blue-100 rounded-lg border border-blue-300">
                  <h3 className="font-semibold text-blue-800 mb-2">Final Answer:</h3>
                  <p className="text-blue-900">{finalMessage}</p>
                </div>
              )}
          </TabsContent>
          <TabsContent value="view-questions">View the questions asked to the bot.</TabsContent>
        </Tabs>
      </div>
    </section>
  )
}
