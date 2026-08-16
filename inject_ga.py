import os
import streamlit as st

def inject_analytics():
    # Find the Streamlit index.html file
    streamlit_dir = os.path.dirname(st.__file__)
    index_path = os.path.join(streamlit_dir, "static", "index.html")

    tracking_code = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-TRS54VERK8"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-TRS54VERK8');
    </script>
    
    <!-- Microsoft Clarity -->
    <script type="text/javascript">
        (function(c,l,a,r,i,t,y){
            c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
            t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
            y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
        })(window, document, "clarity", "script", "y36xlls02y");
    </script>
    """
    try:
        with open(index_path, "r") as f:
            html = f.read()

        if "y36xlls02y" not in html:
            # Inject right before </head>
            html = html.replace("</head>", f"{tracking_code}</head>")
            with open(index_path, "w") as f:
                f.write(html)
            print("Analytics injected successfully.")
        else:
            print("Analytics already present.")
    except Exception as e:
        print(f"Error injecting Google Analytics: {e}")

if __name__ == "__main__":
    inject_analytics()
