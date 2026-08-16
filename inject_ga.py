import os
import streamlit as st

def inject_analytics():
    # Find the Streamlit index.html file
    streamlit_dir = os.path.dirname(st.__file__)
    index_path = os.path.join(streamlit_dir, "static", "index.html")

    ga_code = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-TRS54VERK8"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-TRS54VERK8');
    </script>
    """

    try:
        with open(index_path, "r") as f:
            html = f.read()

        if "G-TRS54VERK8" not in html:
            # Inject right before </head>
            html = html.replace("</head>", f"{ga_code}</head>")
            with open(index_path, "w") as f:
                f.write(html)
            print("Google Analytics injected successfully.")
        else:
            print("Google Analytics already present.")
    except Exception as e:
        print(f"Error injecting Google Analytics: {e}")

if __name__ == "__main__":
    inject_analytics()
