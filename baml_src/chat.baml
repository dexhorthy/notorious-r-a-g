class Message {
    role string
    content string
}

function BasicChat(history: Message[]) -> string {
    client "openai/gpt-4o"
    prompt #"
        {% for m in history %}
        {{ _.role(m.role) }}
        {{ m.content }}
        {% endfor %}
    "#
}