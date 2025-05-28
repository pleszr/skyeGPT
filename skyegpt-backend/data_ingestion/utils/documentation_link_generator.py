from pathlib import Path


def select_doc_source_by_folder_path(relative_path: Path) -> str:
    relative_path_str = str(relative_path)
    if "innoveo-partner-hub" in relative_path_str:
        return "iph"
    elif "skyedoc" in relative_path_str:
        return "skye"


def link_generator(file_name: str, type_of_documentation: str):
    # I expect skye documentation to be moved to a new place and didn't want to invest more time to this until
    if type_of_documentation == "skye":
        skye_documentation_search_link_base = "https://confluence.innoveo.com/dosearchsite.action?queryString="
        return str(skye_documentation_search_link_base + file_name)
    elif type_of_documentation == "iph":
        partner_hub_base_link = "https://innoveo.atlassian.net/wiki/spaces/IPH/pages/"
        return str(partner_hub_base_link + file_name)
    else:
        print("Link generator error. Type of documentation is nor skye nor iph")
