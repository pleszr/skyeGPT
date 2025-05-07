from types import SimpleNamespace


def mock_assistant_chunk_generator(
        number_of_chunks: int,
        type_of_event: str
):
    for x in range(number_of_chunks):
        chunk = SimpleNamespace(
            event=type_of_event,
            data=SimpleNamespace(
                delta=SimpleNamespace(
                    content=[
                        SimpleNamespace(
                            text=SimpleNamespace(value=f"chunk_{x}")
                        )
                    ]
                )
            )
        )
        yield chunk


def mock_token_generator(
        number_of_chunks: int
):
    for x in range(number_of_chunks):
        yield f"token_{x}"


def mock_completions_chunk_generator(
        number_of_chunks: int
):
    for x in range(number_of_chunks):
        chunk = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    delta=SimpleNamespace(
                        content=f"chunk_{x}"
                    )
                )
            ]
        )
        yield chunk


