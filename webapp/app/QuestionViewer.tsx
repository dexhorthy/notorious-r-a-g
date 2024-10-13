import { Badge } from "@/components/ui/badge";
import { DBRecord, StateName, useFirebaseListener } from "@/hooks/firebaseListener";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@radix-ui/react-accordion";
import { ScrollArea } from "@radix-ui/react-scroll-area";

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
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">DB Record Viewer</h1>
      <ScrollArea className="h-[600px] w-full rounded-md border p-4">
        <Accordion type="single" collapsible className="w-full">
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
                        </li>
                      )) ?? <li className="text-sm">No initial state</li>}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold">Actions:</h4>
                    <ul className="list-inside list-disc space-y-1">
                      {record.data?.actions?.map((action, index) => (
                        <li key={index} className="text-sm">
                          <span className="font-medium">{action.type}:</span> {action.content}
                        </li>
                      )) ?? <li className="text-sm">No actions</li>}
                    </ul>
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