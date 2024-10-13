import { Badge } from "@/components/ui/badge";
import { DBRecord, StateName, useFirebaseListener, Action } from "@/hooks/firebaseListener";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@radix-ui/react-accordion";
import { ScrollArea } from "@radix-ui/react-scroll-area";
import { useState } from 'react';
import { ChevronDown, ChevronUp, Search, Database, MessageSquare, UserCheck, CheckCircle, Wrench, History } from 'lucide-react';
import { formatDistanceToNow, formatDuration, subHours } from 'date-fns';
import ReactMarkdown from "react-markdown";

const actionColors: {
  [key: string]: {
    class: string
    icon: React.ElementType
    overrideContent?: string
  }
} = {
  default: { class: 'bg-gray-100 text-gray-800', icon: ChevronDown },
  RAGQuery: {
    class: 'bg-blue-100 text-blue-800',
    icon: Wrench
  },
  RAGResult: {
    class: 'bg-blue-100 text-blue-800', icon: () => (
      <img
        src="https://yepcode.io/docs/img/integrations/icons/pinecone.svg"
        alt="Pinecone Logo"
        className="w-8 h-8"
      />
    )
  },

  RespondToUser: { class: 'bg-green-100 text-green-800', icon: MessageSquare },
  HumanApproval: { class: 'bg-yellow-100 text-yellow-800', icon: UserCheck },
  "Finalizing Answer": { class: 'bg-green-100 text-green-800', icon: CheckCircle, overrideContent: "Approved" },
  "Incorporating Feedback": { class: 'bg-orange-100 text-orange-800', icon: History },
  // Add more action types, classes, and icons as needed
};

function PSTDate(ms: number) {
  return subHours(new Date(ms), 7).toLocaleString('en-US', { timeZone: 'America/Los_Angeles' })
}

function PSTDateRelative(ms: number) {
  return formatDistanceToNow(subHours(new Date(ms), 7), { addSuffix: true })
}

function relativeDate(date: Date) {
  return formatDistanceToNow(date, { addSuffix: true })
}

function ActionBubble({ action, startDate }: { action: Action, startDate: Date }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxLength = 200; // Adjust this value as needed

  const toggleExpand = () => setIsExpanded(!isExpanded);

  const truncatedContent = action.content.length > maxLength
    ? action.content.slice(0, maxLength) + '...'
    : action.content;

  const actionConfig = actionColors[action.type as keyof typeof actionColors] || actionColors.default;
  const Icon = actionConfig.icon;

  return (
    <div className={`rounded-lg flex flex-row gap-2 items-center p-3 mb-2 ${actionConfig.class}`}>
      <Icon className="w-8 h-8" />
      <div className="flex flex-col  w-full justify-between">
        <div className="flex justify-between items-center mb-1">
          <span className="font-medium flex items-center">
            {action.type}
          </span>
          <span className="text-xs text-gray-600 ml-2">
            +{((action.create_time_ms - startDate.getTime()) / 1000).toFixed(2)}s
          </span>
        </div>


        <p className="text-sm">
          {actionConfig.overrideContent ?? <ReactMarkdown>{isExpanded ? action.content : truncatedContent}</ReactMarkdown>}
        </p>
        {(actionConfig.overrideContent ?? action.content).length > maxLength && (
          <button
            onClick={toggleExpand}
            className="flex items-center text-blue-500 hover:text-blue-700 mt-1 text-xs"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-3 h-3 mr-1" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="w-3 h-3 mr-1" />
                Show more
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export default function Page({ agentId }: { agentId?: string }) {
  const pages = useFirebaseListener("agentstate")
  if (!agentId) {
    return <Component records={pages} />
  } else {
    const record = pages.find(page => page.id === agentId)
    if (!record) {
      return null
    }
    return <Component records={[record]} />
  }
}

function Component({ records }: { records: DBRecord[] }) {
  const [_selectedRecord, setSelectedRecord] = useState<DBRecord | null>(null);

  const selectedRecord = _selectedRecord ?? records.at(-1);

  // Constants
  const stateColors: Record<StateName, string> = {
    running: 'bg-gray-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    cancelled: 'bg-orange-500',
    paused: 'bg-yellow-500',
  }

  return (
    <div className="flex h-[600px] space-x-4">
      <div className="w-1/3 overflow-y-auto border-r pr-4">
        <h2 className="text-xl font-bold mb-4">Questions</h2>
        <div className="flex flex-col-reverse">
          {records.map((record) => {
            const lastAction = record.data?.actions?.[record.data.actions.length - 1];
            const lastActionType = lastAction?.type || 'No actions';

            return (
              <div
                key={record.id}
                className={`cursor-pointer p-4 mb-2 rounded-lg ${selectedRecord?.id === record.id ? 'bg-blue-100' : 'bg-white'} hover:bg-blue-50`}
                onClick={() => setSelectedRecord(record)}
              >
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    {record.data?.initial_state?.[0]?.avatar_url && (
                      <img
                        src={record.data.initial_state[0].avatar_url}
                        alt="User Avatar"
                        className="w-6 h-6 rounded-full mb-1"
                      />
                    )}
                    <span className="text-sm font-semibold mb-1 truncate">{record.data?.initial_state?.[0]?.message || 'No question'}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-500">

                    <span>{PSTDateRelative(record.data.create_time_ms.getTime())}</span>
                    <div className="flex items-center space-x-2">
                      <Badge className={`${stateColors[record.data?.state ?? 'running']} text-white`}>
                        {record.data?.state ?? 'Unknown'}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="w-2/3 overflow-y-auto">
        {selectedRecord ? (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              {selectedRecord.data?.initial_state?.[0]?.avatar_url && (
                <img
                  src={selectedRecord.data.initial_state[0].avatar_url}
                  alt="User Avatar"
                  className="w-10 h-10 rounded-full mb-2"
                />
              )}
              <h2 className="text-2xl font-bold">{selectedRecord.data?.initial_state?.[0]?.message || 'No question'}</h2>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-2">Initial State:</h4>
              <div className="space-y-2 border-l-2 border-gray-200 pl-3">
                {selectedRecord.data?.initial_state?.map((message, index) => (
                  <div key={index} className="bg-gray-100 rounded-lg p-2">
                    <p className="text-sm">{message.message}</p>
                  </div>
                )) ?? (
                    <div className="bg-gray-100 rounded-lg p-2">
                      <p className="text-sm">No initial state</p>
                    </div>
                  )}
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold">Actions:</h4>
              <div className="space-y-2">
                {selectedRecord.data?.actions?.map((action, index) => (
                  <ActionBubble key={index} action={action} startDate={selectedRecord.data.create_time_ms} />
                )) ?? <p className="text-sm">No actions</p>}
              </div>
            </div>
            {selectedRecord.data?.state === 'cancelled' && (
              <div>
                <h4 className="text-sm font-semibold">Final State:</h4>
                <p className="text-sm">{selectedRecord.data?.final_state ?? 'N/A'}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Select a question from the list to view details
          </div>
        )}
      </div>
    </div>
  )
}
