import { Badge } from "@/components/ui/badge";
import { DBRecord, StateName, useFirebaseListener, Action } from "@/hooks/firebaseListener";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@radix-ui/react-accordion";
import { ScrollArea } from "@radix-ui/react-scroll-area";
import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { formatDistanceToNow, formatDuration, subHours } from 'date-fns';

const actionColors = {
  default: 'bg-gray-100 text-gray-800',
  RAGQuery: 'bg-blue-100 text-blue-800',
  RAGResult: 'bg-blue-100 text-blue-800',
  RespondToUser: 'bg-green-100 text-green-800',
  HumanApproval: 'bg-yellow-100 text-yellow-800',
  // Add more action types and colors as needed
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

  const bubbleColor = actionColors[action.type as keyof typeof actionColors] || actionColors.default;

  return (
    <div className={`rounded-lg p-3 mb-2 ${bubbleColor}`}>
      <div className="flex justify-between items-center mb-1">
        <span className="font-medium">{action.type}</span>
        <span className="text-xs text-gray-600 ml-2">
          +{((action.create_time_ms - startDate.getTime()) / 1000).toFixed(2)}s
        </span>

      </div>

      <p className="text-sm">
        {isExpanded ? action.content : truncatedContent}
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
    running: 'bg-blue-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    cancelled: 'bg-yellow-500',
    paused: 'bg-gray-500',
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
      <ScrollArea className="h-[600px] w-full rounded-md border p-4">
        <Accordion type="single" collapsible className="w-full" defaultValue={records.length === 1 ? records[0].id : undefined}>
          {records.map((record) => (
            <AccordionItem value={record.id} key={record.id}>
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">Record ID: {record.id}</span>
                  <Badge className={`${stateColors[record.data?.state ?? 'running']} text-white`}>
                    {record.data?.state ?? 'Unknown'}
                  </Badge>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4 pl-4">
                  <div>
                    <h4 className="text-sm font-semibold">Initial State:</h4>
                    <ul className="list-inside list-disc space-y-1">
                      {record.data?.initial_state?.map((message, index) => (
                        <li key={index} className="text-sm">
                          <span className="font-medium">{message.user}:</span> {message.message}
                          <span className="text-xs text-gray-500 ml-2">
                            {PSTDateRelative(record.data.create_time_ms.getTime())}
                          </span>
                          <span className="text-xs text-gray-500 ml-2">
                            ({formatDuration({ seconds: record.data.create_time_ms.getTime() / 1000 - (record.data.state !== 'running' ? record.data.update_time_ms.getTime() : Date.now() / 1000) })})
                          </span>
                        </li>
                      )) ?? <li className="text-sm">No initial state</li>}
                    </ul>
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
