import markdown


def convert_md_to_html(
        answer_md: str,
        extension: str
):
    return markdown.markdown(answer_md, extensions=[extension])
