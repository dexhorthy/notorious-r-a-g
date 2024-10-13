import React from 'react';
import {
  CheckCircle,
  ChevronDown,
  MessageSquare,
  UserCheck,
  Wrench,
  History,
} from "lucide-react";

interface ActionColor {
  class: string;
  icon: React.ComponentType<any>;
  overrideContent?: string;
}

export const actionColors: Record<string, ActionColor> = {
  default: { class: "bg-gray-100 text-gray-800", icon: ChevronDown },
  RAGQuery: { class: "bg-blue-100 text-blue-800", icon: Wrench },
  RAGResult: {
    class: "bg-blue-100 text-blue-800",
    icon: () => (
      <img
        src="https://yepcode.io/docs/img/integrations/icons/pinecone.svg"
        alt="Pinecone Logo"
        className="w-8 h-8"
      />
    ),
  },
  RespondToUser: { class: "bg-green-100 text-green-800", icon: MessageSquare },
  HumanApproval: { class: "bg-yellow-100 text-yellow-800", icon: UserCheck },
  "Finalizing Answer": {
    class: "bg-green-100 text-green-800",
    icon: CheckCircle,
    overrideContent: "Approved",
  },
  "Incorporating Feedback": {
    class: "bg-orange-100 text-orange-800",
    icon: History,
  },
};
