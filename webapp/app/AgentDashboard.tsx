import React, { useState } from 'react';
import { DBRecord, useFirebaseListener } from "@/hooks/firebaseListener";
import QuestionList from './QuestionsList';
import QuestionDetails from './QuestionViewer';


interface AgentDashboardProps {
  agentId?: string;
}

export default function AgentDashboard({ agentId }: AgentDashboardProps) {
  const pages = useFirebaseListener("agentstate");
  const [selectedRecord, setSelectedRecord] = useState<DBRecord | null>(null);

  const records = agentId
    ? pages.filter((page) => page.id === agentId)
    : pages;

  const currentRecord = selectedRecord ?? records.at(-1);

  return (
    <div className="flex h-[600px] space-x-4">
      <div className="w-1/3 overflow-y-auto border-r pr-4">
        <h2 className="text-xl font-bold mb-4">Questions</h2>
        <QuestionList
          records={records}
          selectedRecordId={currentRecord?.id}
          onSelectRecord={setSelectedRecord}
        />
      </div>
      <div className="w-2/3 overflow-y-auto">
        {currentRecord ? (
          <QuestionDetails record={currentRecord} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a question from the list to view details
          </div>
        )}
      </div>
    </div>
  );
}
