"use client";
import Image from "next/image";
import notoriousRagLogo from "@/public/images/image.png";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

import { useState } from 'react'
import Question from "./Question";
import QuestionViewer from "./QuestionViewer";

export default function IndexPage() {
  const [isConnected, setIsConnected] = useState(true)

  return (
    <section className="container flex flex-col items-center py-8 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center flex items-center justify-center">
          <div>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} transition-colors duration-300`}>
              <span className={`w-2 h-2 mr-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></span>
              {isConnected ? 'Connected' : 'Disconnected'}
            </div>
            <h1 className="mt-6 text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
              Notorious R.A.G.
            </h1>
            <p className="mt-3 text-xl text-gray-500 sm:mt-5 sm:text-2xl">
              Leverage the knowledge in your Discord server to answer inbound questions.
            </p>
          </div>
          <div className="ml-6">
            <Image
              src={notoriousRagLogo}
              alt="Notorious R.A.G. Logo"
              width={300}
              height={300}
              className="rounded-lg shadow-2xl transition-transform duration-300 hover:scale-105"
            />
          </div>
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
      </div>
    </section>
  )
}
