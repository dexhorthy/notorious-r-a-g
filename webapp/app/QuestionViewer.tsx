import { Badge } from "@/components/ui/badge";
import { DBRecord, StateName, useFirebaseListener, Action } from "@/hooks/firebaseListener";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@radix-ui/react-accordion";
import { ScrollArea } from "@radix-ui/react-scroll-area";
import { useState } from 'react';
import { ChevronDown, ChevronUp, Search, Database, MessageSquare, UserCheck, CheckCircle, Wrench } from 'lucide-react';
import { formatDistanceToNow, formatDuration, subHours } from 'date-fns';
import ReactMarkdown from "react-markdown";

const actionColors = {
  default: { class: 'bg-gray-100 text-gray-800', icon: ChevronDown },
  RAGQuery: {
    class: 'bg-blue-100 text-blue-800',
    icon: Wrench
  },
  RAGResult: { class: 'bg-blue-100 text-blue-800', icon: () => (
      <img
        src="https://yepcode.io/docs/img/integrations/icons/pinecone.svg"
        alt="Pinecone Logo"
        className="w-8 h-8"
      />
    ) },

  RespondToUser: { class: 'bg-green-100 text-green-800', icon: MessageSquare },
  HumanApproval: { class: 'bg-yellow-100 text-yellow-800', icon: UserCheck },
  "Finalizing Answer": { class: 'bg-purple-100 text-purple-800', icon: CheckCircle },
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
          <ReactMarkdown>{isExpanded ? action.content : truncatedContent}</ReactMarkdown>
        </p>
        {action.content.length > maxLength && (
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
  // Constants
  const stateColors: Record<StateName, string> = {
    running: 'bg-gray-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    cancelled: 'bg-orange-500',
    paused: 'bg-yellow-500',
  }

  function TruncatedContent({ content }: { content: string }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const maxLength = 200; // Adjust this value as needed

    const toggleExpand = () => setIsExpanded(!isExpanded);

    const truncatedContent = content.length > maxLength
      ? content.slice(0, maxLength) + '...'
      : content;

    return (
      <div>
        <p className="text-sm">
          {isExpanded ? content : truncatedContent}
        </p>
        {content.length > maxLength && (
          <button
            onClick={toggleExpand}
            className="flex items-center text-blue-500 hover:text-blue-700 mt-1"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="w-4 h-4 mr-1" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-1" />
                Show more
              </>
            )}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">DB Record Viewer</h1>
      <ScrollArea className="h-[600px] w-full rounded-md p-4">
        <Accordion type="single" collapsible className="w-full flex flex-col flex-col-reverse" defaultValue={records.length === 1 ? records[0].id : undefined}>
          {records.map((record) => (
            <AccordionItem value={record.id} key={record.id}>
              <AccordionTrigger className="w-full hover:no-underline border border-gray-200 rounded-lg mb-2">
                <div className="flex items-center justify-between w-full p-4 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
                  <div className="flex flex-col items-start flex-grow">
                    <div className="flex items-center">
                      <span className="text-lg font-semibold mb-2 text-left">{record.data?.initial_state?.[0]?.message || 'No question'}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600 text-left">
                      <span>{PSTDateRelative(record.data.create_time_ms.getTime())}</span>
                      <span>•</span>
                      <span>{record.data?.actions?.length || 0} steps</span>
                    </div>
                    {record.data?.final_state && (
                      <div className="mt-2 text-sm text-gray-700 max-w-md overflow-hidden">
                        <span className="truncate inline-block max-w-full">
                          {record.data.final_state}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 flex-shrink-0">
                    <div className="flex space-x-2">
                      {record.data?.actions?.slice(0, 3).map((action, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {action.type}
                        </Badge>
                      ))}
                      {record.data?.actions?.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{record.data.actions.length - 3} more
                        </Badge>
                      )}
                    </div>
                    <Badge className={`${stateColors[record.data?.state ?? 'running']} text-white`}>
                      {record.data?.state ?? 'Unknown'}
                    </Badge>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pl-4">
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Initial State:</h4>
                    <div className="space-y-2 border-l-2 border-gray-200 pl-3">
                      {record.data?.initial_state?.map((message, index) => (
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
                      {record.data?.actions?.map((action, index) => (
                        <ActionBubble key={index} action={action} startDate={record.data.create_time_ms} />
                      )) ?? <p className="text-sm">No actions</p>}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold">Final State:</h4>
                    <p className="text-sm">{record.data?.final_state ?? 'N/A'}</p>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </ScrollArea>
    </div>
  )
}
