// Defining a data model.
class Answer {
  answer string
}

class RAGQuery {
  question string
}

// Create a function to extract the resume from a string.
function FormulateAnswer(query: string, context: string[]) -> RAGQuery | Answer {
  client "openai/gpt-4o" 
  prompt #"
    Anwser the following query, potentially executing a RAGQuery to get the context

    {{ query }}

    {{ ctx.output_format }}

    {% if context|length > 0 %}
    {{ _.role('user') }}
    {% for c in context %}
    {{ c }}
    {% endfor %}
    {% endif %}
  "#
}
