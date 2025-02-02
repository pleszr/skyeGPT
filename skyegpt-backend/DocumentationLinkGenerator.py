def documentation_link_generator(
        file_name: str,
        type_of_documentation: str
):
    # I expect skye documentation to be moved to a new place and didn't want to invest more time to this until
    skye_documentation_search_link_base = "https://confluence.innoveo.com/dosearchsite.action?queryString="
    if type_of_documentation == "skye":
        return str(skye_documentation_search_link_base+file_name)
