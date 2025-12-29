# import os
# import streamlit.components.v1 as components

# # --- CONFIGURATION ---
# # We use jsDelivr to ensure we get the exact 8.3.1 version
# TINYMCE_CDN = "https://cdn.jsdelivr.net/npm/tinymce@8.3.1/tinymce.min.js"

# # --- FRONTEND CODE (Embedded) ---
# _HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html>
# <head>
#     <script src="{cdn_url}"></script>
#     <style>
#         body {{ margin: 0; padding: 0; overflow: hidden; }}
#         /* Jira-like border focus */
#         .tox-tinymce {{ border: 1px solid #ccc !important; border-radius: 4px !important; }}
#         .tox-tinymce:focus-within {{ border: 2px solid #2684FF !important; }}
#     </style>
# </head>
# <body>

# <textarea id="mytextarea"></textarea>

# <script>
# // --- STREAMLIT COMM HELPER ---
# function sendToStreamlit(data) {{
#     window.parent.postMessage({{
#         isStreamlitMessage: true,
#         type: "streamlit:setComponentValue",
#         value: data
#     }}, "*");
# }}

# // --- EDITOR LOGIC ---
# let isInitialized = false;

# window.addEventListener("message", (event) => {{
#     if (event.data.type === "streamlit:render") {{
#         const args = event.data.args;
        
#         if (!isInitialized) {{
#             tinymce.init({{
#                 selector: '#mytextarea',
#                 height: args.height,
                
#                 // --- REQUIRED FOR TINYMCE 7+ ---
#                 license_key: 'gpl',
#                 // --------------------------------

#                 menubar: false,
#                 statusbar: false,
#                 plugins: args.plugins.join(' '),
#                 toolbar: args.toolbar,
#                 branding: false,
#                 promotion: false,
                
#                 // JIRA-LIKE IMAGE HANDLING
#                 paste_data_images: true,
#                 automatic_uploads: true,
                
#                 // Custom handler to convert images to Base64 immediately
#                 images_upload_handler: (blobInfo, progress) => new Promise((resolve, reject) => {{
#                     const reader = new FileReader();
#                     reader.readAsDataURL(blobInfo.blob());
#                     reader.onload = () => resolve(reader.result);
#                     reader.onerror = (error) => reject(error);
#                 }}),
                
#                 // Content Style to match Jira/Streamlit font
#                 content_style: `
#                     body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; }} 
#                     img {{ max-width: 100%; height: auto; }}
#                 `,

#                 setup: function(editor) {{
#                     editor.on('init', function() {{
#                         // Set initial value
#                         editor.setContent(args.initialValue || "");
#                         isInitialized = true;
#                     }});

#                     // Sync data back to Streamlit on any change
#                     editor.on('Change KeyUp ExecCommand', function() {{
#                         sendToStreamlit(editor.getContent());
#                     }});
#                 }}
#             }});
#         }}
#     }}
# }});

# // Signal Streamlit that we are ready
# window.parent.postMessage({{
#     isStreamlitMessage: true,
#     type: "streamlit:componentReady",
#     apiVersion: 1
# }}, "*");

# </script>
# </body>
# </html>
# """

# def custom_editor(initialValue="", height=300, 
#                   toolbar="undo redo | blocks | bold italic | align | bullist numlist | link image table", 
#                   plugins=["image", "link", "lists", "table"], 
#                   key=None):
#     """
#     A custom Jira-like editor component that handles rich text, image pasting/resizing, and tables.
#     Updated for TinyMCE 8.3.1.
    
#     Parameters:
#     - initialValue: The starting HTML content.
#     - height: The height of the editor in pixels.
#     - toolbar: Space-separated list of toolbar tools.
#     - plugins: List of plugins to load.
#     - key: Unique key for the component.
#     """
    
#     # 1. Prepare the frontend directory (Runtime Injection)
#     component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend_assets")
#     if not os.path.exists(component_dir):
#         os.makedirs(component_dir)
    
#     # 2. Write the HTML file if it doesn't exist or we want to update it
#     index_path = os.path.join(component_dir, "index.html")
    
#     # Always overwrite to ensure latest code is used
#     with open(index_path, "w", encoding="utf-8") as f:
#         html_content = _HTML_TEMPLATE.format(cdn_url=TINYMCE_CDN)
#         f.write(html_content)

#     # 3. Declare the component
#     component_func = components.declare_component(
#         "custom_editor",
#         path=component_dir
#     )

#     # 4. Pass arguments to the frontend
#     return component_func(
#         initialValue=initialValue,
#         height=height,
#         toolbar=toolbar,
#         plugins=plugins,
#         key=key,
#         default=initialValue
#     )


import os
import streamlit.components.v1 as components

# --- CONFIGURATION ---
# We use jsDelivr to ensure we get the exact 8.3.1 version
TINYMCE_CDN = "https://cdn.jsdelivr.net/npm/tinymce@8.3.1/tinymce.min.js"

# --- FRONTEND CODE (Embedded) ---
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <script src="{cdn_url}"></script>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; }}
        /* Jira-like border focus */
        .tox-tinymce {{ border: 1px solid #ccc !important; border-radius: 4px !important; }}
        .tox-tinymce:focus-within {{ border: 2px solid #2684FF !important; }}
    </style>
</head>
<body>

<textarea id="mytextarea"></textarea>

<script>
// --- STREAMLIT COMM HELPER ---
function sendToStreamlit(data) {{
    window.parent.postMessage({{
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: data
    }}, "*");
}}

// --- EDITOR LOGIC ---
let isInitialized = false;

window.addEventListener("message", (event) => {{
    if (event.data.type === "streamlit:render") {{
        const args = event.data.args;
        
        if (!isInitialized) {{
            tinymce.init({{
                selector: '#mytextarea',
                height: args.height,
                
                // --- REQUIRED FOR TINYMCE 7+ ---
                license_key: 'gpl',
                // --------------------------------

                menubar: false,
                statusbar: false,
                plugins: args.plugins.join(' '),
                toolbar: args.toolbar,
                branding: false,
                promotion: false,
                
                // JIRA-LIKE IMAGE HANDLING
                paste_data_images: true,
                automatic_uploads: true,
                
                // Custom handler to convert images to Base64 immediately
                images_upload_handler: (blobInfo, progress) => new Promise((resolve, reject) => {{
                    const reader = new FileReader();
                    reader.readAsDataURL(blobInfo.blob());
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = (error) => reject(error);
                }}),
                
                // Content Style to match Jira/Streamlit font
                content_style: `
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; }} 
                    img {{ max-width: 100%; height: auto; }}
                `,

                setup: function(editor) {{
                    editor.on('init', function() {{
                        // Set initial value
                        editor.setContent(args.initialValue || "");
                        isInitialized = true;
                    }});

                    // Sync data back to Streamlit ONLY on change or blur (removed KeyUp)
                    editor.on('change blur', function() {{
                        sendToStreamlit(editor.getContent());
                    }});
                }}
            }});
        }}
    }}
}});

// Signal Streamlit that we are ready
window.parent.postMessage({{
    isStreamlitMessage: true,
    type: "streamlit:componentReady",
    apiVersion: 1
}}, "*");

</script>
</body>
</html>
"""

def custom_editor(initialValue="", height=300, 
                  toolbar="undo redo | blocks | bold italic | align | bullist numlist | link image table", 
                  plugins=["image", "link", "lists", "table"], 
                  key=None):
    """
    A custom Jira-like editor component that handles rich text, image pasting/resizing, and tables.
    Updated for TinyMCE 8.3.1.
    
    Parameters:
    - initialValue: The starting HTML content.
    - height: The height of the editor in pixels.
    - toolbar: Space-separated list of toolbar tools.
    - plugins: List of plugins to load.
    - key: Unique key for the component.
    """
    
    # 1. Prepare the frontend directory (Runtime Injection)
    component_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend_assets")
    if not os.path.exists(component_dir):
        os.makedirs(component_dir)
    
    # 2. Write the HTML file if it doesn't exist or we want to update it
    index_path = os.path.join(component_dir, "index.html")
    
    # Always overwrite to ensure latest code is used
    with open(index_path, "w", encoding="utf-8") as f:
        html_content = _HTML_TEMPLATE.format(cdn_url=TINYMCE_CDN)
        f.write(html_content)

    # 3. Declare the component
    component_func = components.declare_component(
        "custom_editor",
        path=component_dir
    )

    # 4. Pass arguments to the frontend
    return component_func(
        initialValue=initialValue,
        height=height,
        toolbar=toolbar,
        plugins=plugins,
        key=key,
        default=initialValue
    )