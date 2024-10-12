"use client";
import Image from "next/image";
import notoriousRagLogo from "@/public/images/image.png";

import Link from "next/link"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

import { siteConfig } from "@/config/site"
import { Button, buttonVariants } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useState, useEffect } from 'react'
import { io, Socket } from 'socket.io-client'
import ReactMarkdown from "react-markdown";
import Question from "./Question";
import QuestionViewer from "./QuestionViewer";

function getIcon(icon: string) {
  switch (icon) {
    case 'pencil':
      return '✏️';
    case 'github':
      return '🐙';
    default:
      return '❓';
  }
}

export default function IndexPage() {
  const [question, setQuestion] = useState('')
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<string[]>([])
  const [messageData, setMessageData] = useState<{ state: string, type: string, icon?: string }[]>([])
  const [finalMessage, setFinalMessage] = useState<string | null>(null)


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
      <div className="flex flex-col gap-4">
        <Question />
        <QuestionViewer />
        <div className="w-1/3">
          <Image
            src={notoriousRagLogo}
            alt="Notorious R.A.G. Logo"
            width={300}
            height={300}
            className="rounded-lg shadow-lg"
          />
        </div>
      </div>
    </section>
  )
}
