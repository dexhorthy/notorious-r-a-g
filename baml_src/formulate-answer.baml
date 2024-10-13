enum Action {
  RespondToUser
}

// Defining a data model.
class FinalAnswer {
  intent Action
  reason string @description(#"
    Why there is sufficient information to answer the question
  "#)
}

enum RagAction {
  RAGQuery
}


enum Source {
  Documentation
  Discord
}

class RAGQuery {
  intent RagAction
  question string @description(#"
    A question to use for searching a knowledge base for relevant context
  "#)
  filter_to Source[] @description(#"
    if specified, the search should be limited to these sources
  "#)
}

class Context {
  intent string
  context string
}

template_string PrintContext(context: Context) #"
  {% if context.intent == "RAGQuery" %}
  Action: {{ context.intent }}
  Response: {{ context.context }}
  {% else %}
  {{ context.intent }}:
  {{ context.context }}
  {% endif %}
"#

enum QuestionType {
  Trivia
  Bug
  Troubleshooting
  FeatureRequest
  Documentation
}

class Classification {
  intent QuestionType
  title string @description(#"
    Short title for a thread pertaining to the question
  "#)
}

enum NonAction {
  Spam
  Thanking
  Other
}

class ChatMessage {
  user_id string
  message string
  avatar_url string?
  name string?
}


function ClassifyMessage(chat: ChatMessage[]) -> Classification | NonAction {
  client CustomFast
  prompt #"
    Given the user is messaging a forum about BAML (a programming language for building AI agents), classify the message.

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {% for m in chat %}
    {{ m.message }}
    {% endfor %}
  "#
}

function AnswerQuestion(query: string, context: Context[]) -> string {
  client "openai/gpt-4o"
  prompt #"
    Question from the user about BAML (a programming language for building AI agents).
    {{ query }}

    {{ _.role('user') }}
    {% if context|length > 0 %}
    {% for c in context %}
    {{ PrintContext(c) }}
    {% endfor %}
    {% endif %}
  "#
}


// Create a function to extract the resume from a string.
function FormulateAnswer(query: string, context: Context[]) -> RAGQuery | FinalAnswer {
  client "openai/gpt-4o" 
  prompt #"    
    You are an assistant to help users learn about BAML (a programming language for building AI agents).

    {{ _.role('user') }}
    Question from the user:
    {{ query }}

    {% if context|length > 0 %}
    Information:
    {% for c in context %}
    {{ PrintContext(c) }}
    {% endfor %}
    {% endif %}

    {{ _.role('assistant') }}
    Picking the best action to take next:
    - Query the RAG system for more information (i.e. syntax)
    - Determine if there is enough information to answer the question
    
    {{ ctx.output_format }}
  "#
}
