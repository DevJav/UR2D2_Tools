import pandas as pd

def highlight_best_and_apply_gradient(df):
    def highlight_best(series):
        """Highlight the best value in purple with transparency."""
        is_best = series == series.min()
        return ['background-color: rgba(147, 112, 219, 0.5)' if v else '' for v in is_best]

    def gradient_background(series):
        """Apply a green-to-red gradient with transparency."""
        norm = (series - series.min()) / (series.max() - series.min())
        colors = (1 - norm) * 120
        return [f'background-color: hsla({int(c)}, 100%, 75%, 0.5)' for c in colors]

    # Apply formatting for gradient and best values
    styled_df = df.style.apply(gradient_background, subset=['S1', 'S2', 'S3', 'LapTime'], axis=0)
    styled_df = styled_df.apply(highlight_best, subset=['S1', 'S2', 'S3', 'LapTime'], axis=0)
    styled_df = styled_df.format(precision=2, subset=['S1', 'S2', 'S3', 'LapTime'])
    return styled_df

# Load CSV and normalize column names
input_csv = "lap_data_2024-12-10_18-46-54.csv"
df = pd.read_csv(input_csv)
df.columns = df.columns.str.strip()  # Strip spaces

# Remove default index and set "Lap" as the index
df.set_index("Lap", inplace=True)

# Apply formatting
styled_df = highlight_best_and_apply_gradient(df)

# Create HTML output with custom styling
html_content = styled_df.to_html(index=True)

# Add custom CSS for black background and white text
html_content = f"""
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {{
        background-color: black;
        color: white;
        font-family: 'Roboto', sans-serif;
    }}
    table {{
        width: 80%;
        margin: auto;
        border-collapse: collapse;
        font-family: 'Roboto', sans-serif;
    }}
    th, td {{
        border: 1px solid white;
        text-align: center; 
        padding: 8px;
    }}
    th {{
        background-color: #333333;
        color: white;
    }}
    td {{
        color: white;
    }}
</style>
</head>
<body>
{html_content}
</body>
</html>
"""

# Save to HTML file
with open("formatted_table.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Formatted table saved as: formatted_table.html")
# Add custom CSS for highlighting row on hover
html_content = html_content.replace(
    "</style>",
    """
    tr:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    </style>
    """
)

# Save to HTML file with hover effect
with open("formatted_table_with_hover.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Formatted table with hover effect saved as: formatted_table_with_hover.html")