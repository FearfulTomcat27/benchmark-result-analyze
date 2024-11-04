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
            "content": f"Write code in {language} that meets the problem following. Ensure that the code you generate is "
            "accurate and valid and does not come with test cases. Answer me only the body of the function."
            "Remember, do not need to explain the code you wrote.",
        },
        {"role": "user", "content": problem["prompt"]},
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
            "content": f"Help me complete the {language} code for the following question and I will give the flowchart syntax "
            "for the following problem. Ensure that the complementary code is accurate, valid, and formatted "
            "correctly, and do not need to generate test cases. Remember, do not need to explain the code you wrote.",
        },
        {"role": "user", "content": problem["prompt"]},
        {"role": "user", "content": mermaid["mermaid"]},
    ]
    return __generate_completion__(client, messages, model, temperature, top_p)
