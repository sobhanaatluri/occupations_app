import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os



def create_scaled_text_image(data1, data2, dict_name1="Dataset 1", dict_name2="Dataset 2", output_path=None):
    """
    Create an image displaying two sets of scaled text side by side with their dictionary names below, using Lato font.

    Parameters:
    - data1: dict -> First dataset where keys are displayed with font sizes based on their values.
    - data2: dict -> Second dataset where keys are displayed with font sizes based on their values.
    - dict_name1: str -> Name of the first dataset (displayed below the column).
    - dict_name2: str -> Name of the second dataset (displayed below the column).
    - output_path: str -> Optional, if provided, the image is saved to this path.

    Returns:
    - Saves the image if output_path is provided; otherwise, displays the image.
    """
    # Path to Lato font (Ensure this is the correct path on your system)
    lato_font_path = "/Users/sobhanaatluri/Dropbox/00-Stanford-MacroOB/02-Research Projects/Schemas/Code/fonts/Lato/Lato-Regular.ttf"
    lato_font = fm.FontProperties(fname=lato_font_path)
    # Create figure and remove axes
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.axis("off")

    # Normalize font sizes
    max_value1 = max(data1.values())
    max_value2 = max(data2.values())
    min_font_size, max_font_size = 10, 50  # Set font size range
    spacing = 0.25  # Adjust vertical spacing between words

    # Iterate through both dictionaries and determine font sizes
    for i, ((key1, value1), (key2, value2)) in enumerate(zip(data1.items(), data2.items())):
        font_size1 = min_font_size + (value1 / max_value1) * (max_font_size - min_font_size)
        font_size2 = min_font_size + (value2 / max_value2) * (max_font_size - min_font_size)
        y_position = 1 - (i * spacing)

        # Left column (data1)
        ax.text(0.3, y_position, key1, fontsize=font_size1, ha='center', va='center', fontproperties=lato_font, fontweight='bold')

        # Right column (data2)
        ax.text(0.63, y_position, key2, fontsize=font_size2, ha='center', va='center', fontproperties=lato_font, fontweight='bold')

    # Add dataset names below each column
    ax.text(0.3, y_position - spacing, dict_name1, fontsize=15, ha='center', va='center', fontproperties=lato_font, fontweight='light', color='orange')
    ax.text(0.63, y_position - spacing, dict_name2, fontsize=15, ha='center', va='center', fontproperties=lato_font, fontweight='bold', color='blue')

    # Save or show the image
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        print(f"Image saved to: {output_path}")
    else:
        plt.show()

    # Close the figure to free memory
    plt.close(fig)