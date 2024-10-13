enum Action {
  RespondToUser
}

// Defining a data model.
class FinalAnswer {
  intent Action
  answer string
}

enum RagAction {
  RAGQuery
}

class RAGQuery {
  intent RagAction
  question string @description(#"
    A question to use for searching a knowledge base for relevant context
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

// Create a function to extract the resume from a string.
function FormulateAnswer(query: string, context: Context[]) -> RAGQuery | FinalAnswer {
  client "openai/gpt-4o" 
  prompt #"    
    You are an assistant to help users learn about BAML (a programming language for building AI agents).

    {{ _.role('user') }}
    Question from the user:
    {{ query }}

    {% if context|length > 0 %}
    {% for c in context %}
    {{ PrintContext(c) }}
    {% endfor %}
    {% endif %}

    {{ _.role('assistant') }}
    Picking the best action to take, in general guidelines are:
    - Determining if the answer might be in some sort of documentation. If so, return a RAGQuery with the question to search the docs with.
    - Answering with something vague if its a general question.
    - Answering if there is sufficient information
    
    {{ ctx.output_format }}
  "#
}
