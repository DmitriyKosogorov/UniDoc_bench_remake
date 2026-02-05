import re

def find_fig_tables(text):
    tabs = re.findall(r"<<tab-([^>]+)>>", text)
    figs = re.findall(r"<<fig-([^>]+)>>", text)
    return {"Table":set(tabs), "Figure": set(figs)}

def flatten_unique_ignore_case(input_list):
    result = []
    seen = set()

    def normalize(x):
        return x.lower() if isinstance(x, str) else x

    for item in input_list:
        if isinstance(item, list):
            for subitem in item:
                key = normalize(subitem)
                if key not in seen:
                    result.append(subitem)
                    seen.add(key)
        else:
            key = normalize(item)
            if key not in seen:
                result.append(item)
                seen.add(key)

    return result