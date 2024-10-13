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
  const [isConnected, setIsConnected] = useState(false)

  return (
    <section className="container min-h-screen flex flex-col justify-center items-center py-12 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} transition-colors duration-300`}>
            <span className={`w-2 h-2 mr-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></span>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
          <h1 className="mt-6 text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            Notorious R.A.G.
          </h1>
          <p className="mt-3 text-xl text-gray-500 sm:mt-5 sm:text-2xl">
            A Discord bot that uses RAG to answer questions.
          </p>
        </div>

        <div className="mt-10">
          <Tabs defaultValue="ask" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="ask">Ask a Question</TabsTrigger>
              <TabsTrigger value="view">View Questions</TabsTrigger>
            </TabsList>
            <TabsContent value="ask" className="mt-6">
              <Question />
            </TabsContent>
            <TabsContent value="view" className="mt-6">
              <QuestionViewer />
            </TabsContent>
          </Tabs>
        </div>

        <div className="mt-10 flex justify-center">
          <Image
            src={notoriousRagLogo}
            alt="Notorious R.A.G. Logo"
            width={300}
            height={300}
            className="rounded-lg shadow-2xl transition-transform duration-300 hover:scale-105"
          />
        </div>
      </div>
    </section>
  )
}
