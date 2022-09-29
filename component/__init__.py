import os
import json
import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True
_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATASET_PATH = os.path.join(
    os.path.dirname(_PARENT_DIR),
    "DocEE-en.json"
)
_COLOR_SCHEME_PATH = os.path.join(
    os.path.dirname(_PARENT_DIR),
    "color_scheme.json"
)

if not _RELEASE:
    _component_func = components.declare_component(
        "docee_viewer", url="http://localhost:5000",
    )
else:
    build_dir = os.path.join(_PARENT_DIR, "frontend/public")
    _component_func = components.declare_component(
        "docee_viewer", path=build_dir)


def docee_viewer(header, text, ents, key=None):
    _component_func(
        header=header, text=text, ents=ents, key=key)

def display_app_header(header):
    html_temp = f"""
        <div style = "padding:0px">
            <h2 style = "color:#00aa00; text-align:center;"> {header} </h2>
        </div>
    """
    st.markdown(html_temp, unsafe_allow_html=True)

def setup_meta():
    st.set_page_config( 
        page_icon=":smiley_face:",
        layout="wide"
    )

    hide_menu_style = """
        <style>
            #MainMenu {visibility: hidden; }
            footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def setup_sidebar(event_map):
    if "event_idx_map" not in st.session_state:
        st.session_state.event_idx_map = {}

    event = st.sidebar.selectbox(
        "Select Event Type",
        options=list(event_map.keys()),
    )
    
    index = st.session_state.event_idx_map.get(event, 0)
    layout = st.sidebar.columns(4)
    
    with layout[0]:
        if st.button("prev"):
            index = (index - 1) % len(event_map[event]["samples"])
    
    with layout[1]:
        if st.button("next"):
            index = (index + 1) % len(event_map[event]["samples"])
    
    st.session_state.event_idx_map[event] = index
    st.sidebar.markdown(
        f"""
            <h4 style="text-align: center;">
                Sample: {index + 1} / {len(event_map[event]["samples"])}
            </h4>
        """,
        unsafe_allow_html=True
    )

    with open(_COLOR_SCHEME_PATH) as f:
        color_scheme = json.load(f)

    div_template = (
        """<div style = "text-align: center; padding:0px"> """ 
        + "{}" * len(event_map[event]["types"]) + """</div>"""
    )
    
    span_template = """<span style = "background-color: {};"> {} </span><br>"""
    spans = [span_template.format(color_scheme[x], x.split("█")[-1]) for x in event_map[event]["types"]]

    st.sidebar.markdown(
        div_template.format(*spans),
        unsafe_allow_html=True
    )
    
    return event, index

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def get_event_map(path):
    with open(path) as f:
        json_data = json.load(f)

    event_map = {}
    for sample in json_data:
        event = sample[2]
        
        d = event_map.get(event, {"types": set(), "samples": []})
        d["types"] |= set([f'{event}█{k["type"]}' for k in json.loads(sample[3])])
        d["samples"] += [(sample[0], sample[1], json.loads(sample[3]))]

        event_map[event] = d

    return event_map
    
def main():
    setup_meta()
    event_map = get_event_map(_DATASET_PATH)
    display_app_header("DocEE Dataset Viewer")
    event, index = setup_sidebar(event_map)
    sample = event_map[event]["samples"][index]
    ents = []

    collected_points = set()
    for obj in sample[2]:
        for ment in obj["mention"]:
            
            if (ment["start"], ment["end"]) not in collected_points:    
                ents.append({
                    "start": ment["start"],
                    "end": ment["end"],
                    "label": f'{event}█{obj["type"]}'
                })

                collected_points.add(
                    (ment["start"], ment["end"])
                )
            else:
                st.markdown(
                    f"""
                        <h5 style="color: red; text-align: center;">
                            Multiple types found for the span positioned at: {ment["start"]} - {ment["end"]}!
                        </h5>
                    """,
                    unsafe_allow_html=True
                )

    docee_viewer(
        sample[0], sample[1], ents
    )

if __name__ == "__main__":
    main()

