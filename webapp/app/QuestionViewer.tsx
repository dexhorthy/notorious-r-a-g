// QuestionDetails.tsx
import React from 'react';
import ActionBubble from './ActionBubble';
import type { Action, DBRecord, InitialState } from '@/hooks/firebaseListener';

interface QuestionDetailsProps {
  record: DBRecord;
}

export default function QuestionDetails({ record }: QuestionDetailsProps) {
  return (
    <div className="space-y-4">
      <QuestionHeader record={record} />
      <InitialState initialState={record.data.initial_state} />
      <Actions actions={record.data.actions} createTime={record.data.create_time_ms} />
      {record.data.state === "cancelled" && (
        <FinalState finalState={record.data.final_state ?? "Unknown reason"} />
      )}
    </div>
  );
}

function QuestionHeader({ record }: QuestionDetailsProps) {
  let msg = Array.isArray(record.data.initial_state) ? record.data.initial_state[0] : record.data.initial_state.messages[0];
  let title = !Array.isArray(record.data.initial_state) ? record.data.initial_state.classification.title : msg.message;
  return (
    <div className="flex items-center gap-2">
      {msg.avatar_url && (
        <img
          src={msg.avatar_url}
          alt="User Avatar"
          className="w-10 h-10 rounded-full mb-2"
        />
      )}
      <h2 className="text-2xl font-bold">
        {title}
      </h2>
    </div>
  );
}

interface InitialStateProps {
  initialState: InitialState;
}

function InitialState({ initialState }: InitialStateProps) {
  return (
    <div>
      <h4 className="text-sm font-semibold mb-2">Initial State:</h4>
      <div className="space-y-2 border-l-2 border-gray-200 pl-3">
        {(Array.isArray(initialState) ? initialState : initialState.messages).map((message, index) => (
          <div key={index} className="bg-gray-100 rounded-lg p-2">
            <p className="text-sm">{message.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

interface ActionsProps {
  actions?: Action[];
  createTime: Date;
}

function Actions({ actions, createTime }: ActionsProps) {
  return (
    <div>
      <h4 className="text-sm font-semibold">Actions:</h4>
      <div className="space-y-2">
        {actions?.map((action, index) => (
          <ActionBubble
            key={index}
            action={action}
            startDate={createTime}
          />
        )) ?? <p className="text-sm">No actions</p>}
      </div>
    </div>
  );
}

interface FinalStateProps {
  finalState?: string;
}

function FinalState({ finalState }: FinalStateProps) {
  return (
    <div>
      <h4 className="text-sm font-semibold">Final State:</h4>
      <p className="text-sm">{finalState ?? "N/A"}</p>
    </div>
  );
}

