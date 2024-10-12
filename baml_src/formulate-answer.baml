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

// Create a function to extract the resume from a string.
function FormulateAnswer(query: string, context: string[]) -> RAGQuery | FinalAnswer {
  client "openai/gpt-4o" 
  prompt #"    
    You are an assistant to help users learn about BAML (a programming language for building AI agents).

    {{ _.role('user') }}
    Question from the user:
    {{ query }}

    Pick the best action to take, in general guidelines are:
    - Determine if the answer might be in some sort of documentation. If so, return a RAGQuery with the question to search the docs with.
    - Answer with something vague if its a general question.
    - Answer if there is sufficient information
    
    {{ ctx.output_format }}

    {% if context|length > 0 %}
    {{ _.role('user') }}
    {% for c in context %}
    {{ c }}
    {% endfor %}
    {% endif %}
  "#
}
