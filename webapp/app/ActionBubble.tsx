// ActionBubble.tsx
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { actionColors } from './constants';
import { Action } from '@/hooks/firebaseListener';

interface ActionBubbleProps {
  action: Action;
  startDate: Date;
}

export default function ActionBubble({ action, startDate }: ActionBubbleProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxLength = 200;

  const toggleExpand = () => setIsExpanded(!isExpanded);

  const truncatedContent =
    action.content.length > maxLength
      ? action.content.slice(0, maxLength) + "..."
      : action.content;

  const actionConfig = actionColors[action.type] || actionColors.default;
  const Icon = actionConfig.icon;

  return (
    <div className={`rounded-lg flex flex-row gap-2 items-center p-3 mb-2 ${actionConfig.class}`}>
      <Icon className="w-8 h-8" />
      <div className="flex flex-col w-full justify-between">
        <ActionHeader action={action} startDate={startDate} />
        <ActionContent
          content={actionConfig.overrideContent ?? action.content}
          isExpanded={isExpanded}
          truncatedContent={truncatedContent}
        />
        <ExpandButton
          content={actionConfig.overrideContent ?? action.content}
          isExpanded={isExpanded}
          maxLength={maxLength}
          toggleExpand={toggleExpand}
        />
      </div>
    </div>
  );
}

interface ActionHeaderProps {
  action: Action;
  startDate: Date;
}

function ActionHeader({ action, startDate }: ActionHeaderProps) {
  return (
    <div className="flex justify-between items-center mb-1">
      <span className="font-medium flex items-center">{action.type}</span>
      <span className="text-xs text-gray-600 ml-2">
        +{((action.create_time_ms - startDate.getTime()) / 1000).toFixed(2)}s
      </span>
    </div>
  );
}

interface ActionContentProps {
  content: string;
  isExpanded: boolean;
  truncatedContent: string;
}

function ActionContent({ content, isExpanded, truncatedContent }: ActionContentProps) {
  return (
    <p className="text-sm">
      <ReactMarkdown>
        {isExpanded ? content : truncatedContent}
      </ReactMarkdown>
    </p>
  );
}

interface ExpandButtonProps {
  content: string;
  isExpanded: boolean;
  maxLength: number;
  toggleExpand: () => void;
}

function ExpandButton({ content, isExpanded, maxLength, toggleExpand }: ExpandButtonProps) {
  if (content.length <= maxLength) return null;

  return (
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
  );
}

