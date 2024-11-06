def __generate_completion__(client, messages, model, temperature, top_p):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
    )
    return completion.choices[0].message.content


def generate_completion_baseline(client, problem, language, model, temperature, top_p):
    messages = [
        {
            "role": "system",
            "content": f"You're a very experienced {language} programmer.",
        },
        {
            "role": "user",
            "content": f"""Below is an instruction that describes a task. Write a response that appropriately 
            completes the request. \n\n### Instruction: Complete the following {language} code without any tests or 
            explanation\n{problem["prompt"]}\n\n### Response:""",
        },
    ]
    return __generate_completion__(client, messages, model, temperature, top_p)


def generate_completion_mermaid(
    client, problem, language, mermaid, model, temperature, top_p
):
    messages = [
        {
            "role": "system",
            "content": f"You're a very experienced {language} programmer.",
        },
        {
            "role": "user",
            "content": f"""Below is a mermaid syntax and an instruction that describes a task. Write a response that 
            appropriately completes the request.\n\n### Mermaid:\n{mermaid["mermaid"]}\n### Instruction:\nComplete 
            the following {language} code without any tests or explanation\n{problem["prompt"]}\n\n### Response:""",
        },
    ]
    return __generate_completion__(client, messages, model, temperature, top_p)
