// ActionBubble.tsx
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { ChevronDown, ChevronUp, FileText, MessageCircle } from 'lucide-react';
import { actionColors } from './constants';
import { Action, RagResult } from '@/hooks/firebaseListener';
import { Badge } from '@/components/ui/badge';

interface ActionBubbleProps {
  action: Action;
  startDate: Date;
}

export default function ActionBubble({ action, startDate }: ActionBubbleProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const maxLength = 200;

  const toggleExpand = () => setIsExpanded(!isExpanded);

  const truncatedContent = typeof action.content == "string" ? 
    action.content.length > maxLength
      ? action.content.slice(0, maxLength) + "..."
      : action.content
    : `(${action.content.result.length} context)`;

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
  content: string | RagResult;
  isExpanded: boolean;
  truncatedContent: string;
}

function ActionContent({ content, isExpanded, truncatedContent }: ActionContentProps) {
  if (!isExpanded) {
    return (
      <p className="text-sm">
        <ReactMarkdown>
          {truncatedContent}
        </ReactMarkdown>
      </p>
    );
  }

  return (
    <div className="text-sm">
      {
        typeof content === "string" ? (
          <ReactMarkdown>
            {content}
          </ReactMarkdown>
        ) : (
          content.result.map(({ content, metadata }, index) => {
            let meta = Object.fromEntries(Object.entries(metadata));
            
            const { thread_id, channel_id, ...restMeta } = meta;
            if (thread_id && channel_id) {
              const channelNames = {
                "1119375594984050779": "General",
                "1253172325205934181": "Troubleshooting",
                "1253172394345107466": "Questions"
              };

              if (channel_id in channelNames) {
                restMeta["channel_name"] = channelNames[channel_id as keyof typeof channelNames];
              }
              restMeta["url"] = `https://discord.com/channels/1119368998161752075/${channel_id}/${thread_id}`;
            }
            meta = restMeta;

            return<div key={index} className="mb-2">
              <div className="flex flex-wrap gap-1 mb-1">
                {Object.entries(meta)
                  .sort(([keyA], [keyB]) => {
                    const order = ["type", "channel_name", "title", "thread_name", "url", ];
                    const indexA = order.indexOf(keyA);
                    const indexB = order.indexOf(keyB);
                    if (indexA === -1 && indexB === -1) return 0;
                    if (indexA === -1) return 1;
                    if (indexB === -1) return -1;
                    return indexA - indexB;
                  })
                  .map(([key, value]) => {
                    if (key === "url") {
                      return (
                        <a key={key} href={String(value)} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline text-xs">
                          Link
                        </a>
                      );
                    } else if (key === "channel_name") {
                      return (
                        <Badge key={key} className="bg-primary text-primary-foreground text-xs">
                          #{value}
                        </Badge>
                      );
                    } else if (key === "title" || key === "thread_name") {
                      return (
                        <span key={key} className="font-bold text-xs">
                          {value}
                        </span>
                      );
                    } else if (key === "type") {
                      if (value === "docs") {
                        return (
                          <Badge key={key} className="bg-primary text-primary-foreground text-xs">
                            <FileText className="w-3 h-3 inline-block mr-1" />
                          </Badge>
                        );
                      } else if (value === "discord_thread") {
                        return (
                          <Badge key={key} className="bg-primary text-primary-foreground text-xs">
                            <MessageCircle className="w-3 h-3 inline-block mr-1" />
                          </Badge>
                        );
                      } else {
                        return (
                          <Badge key={key} className="bg-primary text-primary-foreground text-xs">
                            {value}
                          </Badge>
                        );
                      }
                    } else {
                      return (
                        <Badge key={key} className="bg-primary text-primary-foreground text-xs">
                          {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </Badge>
                      );
                    }
                  })}
              </div>
              <ReactMarkdown>
                {content.length > 100 ? content.slice(0, 100) + "..." : content}
              </ReactMarkdown>
            </div>
          }
          )
        )}
    </div>
  );
}

interface ExpandButtonProps {
  content: string | RagResult;
  isExpanded: boolean;
  maxLength: number;
  toggleExpand: () => void;
}

function ExpandButton({ content, isExpanded, maxLength, toggleExpand }: ExpandButtonProps) {
  if (typeof content == "string" && content.length <= maxLength) return null;

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

