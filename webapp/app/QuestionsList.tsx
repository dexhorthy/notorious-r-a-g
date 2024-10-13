// QuestionList.tsx
import React from 'react';
import { Badge } from "@/components/ui/badge";
import { PSTDateRelative } from './utils';
import { DBRecord } from '@/hooks/firebaseListener';

const stateColors: Record<string, string> = {
  running: "bg-gray-500",
  completed: "bg-green-500",
  failed: "bg-red-500",
  cancelled: "bg-orange-500",
  paused: "bg-yellow-500",
};

interface QuestionListProps {
  records: DBRecord[];
  selectedRecordId?: string;
  onSelectRecord: (record: DBRecord) => void;
}

export default function QuestionList({ records, selectedRecordId, onSelectRecord }: QuestionListProps) {
  return (
    <div className="flex flex-col-reverse">
      {records.map((record) => (
        <QuestionListItem
          key={record.id}
          record={record}
          isSelected={selectedRecordId === record.id}
          onClick={() => onSelectRecord(record)}
        />
      ))}
    </div>
  );
}

interface QuestionListItemProps {
  record: DBRecord;
  isSelected: boolean;
  onClick: () => void;
}

function QuestionListItem({ record, isSelected, onClick }: QuestionListItemProps) {
  let msg = Array.isArray(record.data.initial_state) ? record.data.initial_state[0] : record.data.initial_state.messages[0];
  let title = !Array.isArray(record.data.initial_state) ? record.data.initial_state.classification.title : msg.message;
  
  return (
    <div
      className={`cursor-pointer p-4 mb-2 rounded-lg ${
        isSelected ? "bg-blue-100" : "bg-white"
      } hover:bg-blue-50`}
      onClick={onClick}
    >
      <div className="flex flex-col">
        <div className="flex items-center gap-2">
          {msg.avatar_url && (
            <img
              src={msg.avatar_url}
              alt="User Avatar"
              className="w-6 h-6 rounded-full mb-1"
            />
          )}
          <span className="text-sm font-semibold mb-1 truncate">
            {title}
          </span>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            {PSTDateRelative(record.data.create_time_ms.getTime())}
          </span>
          <div className="flex items-center space-x-2">
            <Badge
              className={`${
                stateColors[record.data?.state ?? "running"]
              } text-white`}
            >
              {record.data?.state ?? "Unknown"}
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}