import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')  # Use the non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
from reportlab.lib.utils import ImageReader
import matplotlib.font_manager as fm
import ast
    
def plot_attr_comparison(focal_vec, target_vec, attribute_list, focal_job, target_job, attribute, output_path):
    """
    Creates and saves a horizontal bar chart showing differences in importance
    between focal and target jobs for a specific attribute, with consistent sizing and alignment.
    """
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Ensure inputs are numpy arrays
    focal_vec = np.array(focal_vec)
    target_vec = np.array(target_vec)
    attribute_list = np.array(attribute_list)
    
    # Compute the difference
    differences = focal_vec - target_vec
    
    # Combine attribute names with ratings (make more readable with spaces)
    list_with_ratings = [f"{name} ({rating})" for name, rating in zip(attribute_list, target_vec)]
    
    # Create DataFrame for sorting and plotting
    df = pd.DataFrame({
        attribute: list_with_ratings,
        'Focal': focal_vec,
        'Target': target_vec,
        'Difference': differences
    })
    
    # Sort by target values for consistency
    df_sorted = df.sort_values(by='Target', ascending=True).reset_index(drop=True)
    
    # Determine colors based on positive or negative differences
    colors = ['dodgerblue' if x > 0 else 'sandybrown' for x in df_sorted['Difference']]
    
    # Set truly fixed and consistent dimensions
    total_width = 2000  # Total fixed width for all plots
    label_width = 400   # Fixed width for label area
    
    # Calculate actual plot area width (total - label area - right margin)
    plot_area_width = total_width - label_width - 100
    
    # Dynamic height based on number of attributes
    row_height = 25    # Height per attribute row
    min_height = 600   # Minimum height
    plot_height = max(min_height, row_height * len(attribute_list) + 150)
    
    # FIXED x-axis range - consistent across ALL plots
    x_min = -100
    x_max = 100
    
    # Create figure
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=df_sorted['Difference'],
        y=df_sorted[attribute],
        orientation='h',
        marker=dict(color=colors),
        text=df_sorted['Difference'].round(1),
        textposition='outside',
        cliponaxis=False
    ))
    
    # Add a vertical reference line at x=0
    fig.add_shape(
        type='line',
        x0=0, y0=-0.5,
        x1=0, y1=len(attribute_list) - 0.5,
        line=dict(color='black', width=1)
    )
    
    # Create a more rigid layout with fixed dimensions
    fig.update_layout(
        title={
            'text': f'{attribute} Alignment: {focal_job} → {target_job}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'family': 'Arial, sans-serif'}
        },
        xaxis=dict(
            title='Difference in Importance',
            range=[x_min, x_max],  # FIXED range for all plots
            #constrain='domain',
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            dtick=20,  # Fixed tick spacing
            tickfont={'size': 12}
        ),
        yaxis=dict(
            title=attribute,
            autorange=True,
            fixedrange=False,  # Allow adjusting for different numbers of items
            tickfont={'size': 13},
            ticksuffix='  ',  # Add space after tick labels
        ),
        width=total_width,  # Fixed total width
        height=plot_height,
        margin=dict(
            l=label_width,
            r=20,  # Increase right margin to accommodate bar labels
            t=20,  # Increase top margin for title
            b=30,  # Increase bottom margin for x-axis title
            autoexpand=False  # Critical: prevent auto-expansion
        ),
        paper_bgcolor='white',
        plot_bgcolor='#f8f9fa',  # Light background for better readability
        uniformtext=dict(mode='hide', minsize=10),
        showlegend=False
    )
    
    # Explicitly set the domain to control plot width
    fig.update_xaxes(domain=[label_width/total_width, (total_width-80)/total_width])
    
    # Increase font sizes for better readability
    fig.update_yaxes(
        tickfont={'size': 13, 'family': 'Arial, sans-serif'},
        title_font={'size': 14, 'family': 'Arial, sans-serif'}
    )
    
    # Save with a higher DPI for clearer text
    fig.write_image(
        output_path, 
        format="png", 
        scale=2.5,  # Higher scale for clearer text
        width=total_width,
        height=plot_height
    )
    
    print(f"✅ Plot saved: {output_path}")


def create_scaled_text_image(data1, data2, dict_name1="Dataset 1", dict_name2="Dataset 2", output_path=None):
    """
    Create an image displaying two sets of scaled text side by side with their dictionary names below, using Lato font.
    """
    
    #print("THIS ONE")

    # Path to Lato font
    lato_font_path = "/Users/sobhanaatluri/Dropbox/00-Stanford-MacroOB/02-Research Projects/Schemas/Code/fonts/Lato/Lato-Regular.ttf"
    
    # Check if the font file exists
    if not os.path.exists(lato_font_path):
        print(f"❌ Warning: Lato font not found at {lato_font_path}. Using default font.")
        lato_font = None  # Use default font
    else:
        lato_font = fm.FontProperties(fname=lato_font_path)

    # Create a figure
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.axis("off")

    # Normalize font sizes based on their max values
    max_value1 = max(data1.values())
    max_value2 = max(data2.values())

    min_font_size, max_font_size = 10, 50  # Font size range
    spacing = 0.2  # Vertical spacing between words

    for i, ((key1, value1), (key2, value2)) in enumerate(zip(data1.items(), data2.items())):
        font_size1 = min_font_size + (value1 / max_value1) * (max_font_size - min_font_size)
        font_size2 = min_font_size + (value2 / max_value2) * (max_font_size - min_font_size)

        y_position = 1 - (i * spacing)

        # Left column (data1)
        ax.text(0.3, y_position, key1, fontsize=font_size1, ha='center', va='center', fontproperties=lato_font, fontweight='bold' if lato_font else 'normal')

        # Right column (data2)
        ax.text(0.8, y_position, key2, fontsize=font_size2, ha='center', va='center', fontproperties=lato_font, fontweight='bold' if lato_font else 'normal')

    # Add dataset names below each column
    ax.text(0.3, y_position - spacing, dict_name1, fontsize=15, ha='center', va='center', fontproperties=lato_font, fontweight='light' if lato_font else 'normal', color='orange')
    ax.text(0.8, y_position - spacing, dict_name2, fontsize=15, ha='center', va='center', fontproperties=lato_font, fontweight='bold' if lato_font else 'normal', color='blue')

    # Save the image
    if output_path:
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        print(f"✅ Scaled Text Image saved: {output_path}")
    else:
        plt.show()

    plt.close(fig)  # ✅ Close the figure to free memory

def generate_value_graph(values_order_str, onet_job, attainable_job, dream_job, 
                         val_df, output_path, font_path=None):
    """
    Generate a value alignment graph comparing three jobs against a personalized value order.
    
    Parameters:
    -----------
    values_order_str : str
        Comma-separated string of values in order of importance to the user
    onet_job : str
        Current/Most Recent job title
    attainable_job : str
        Attainable job title
    dream_job : str
        Dream job title
    val_df : pandas.DataFrame
        DataFrame containing occupation data with columns 'Occupation' and 'Extent'
    output_path : str
        Path to save the output figure
    font_path : str, optional
        Path to the custom font file (e.g., Lato)
    """
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import numpy as np
    import ast
    
    # Convert values_order_str to a list
    value_order = [value.strip() for value in values_order_str.split(',')]
    
    # Set default attributes (these should match the order in val_df['Extent'])
    attributes = ['Achievement', 'Independence', 'Recognition', 'Relationships', 'Support', 'Working Conditions']
    
    # Setup font if provided
    custom_font = None
    if font_path:
        try:
            custom_font = fm.FontProperties(fname=font_path)
            fm.fontManager.addfont(font_path)
        except:
            print(f"Warning: Could not load font from {font_path}. Using default font.")
    
    # Extract ratings function
    def extract_ratings(occupation):
        try:
            ratings_str = val_df.loc[val_df['Occupation'] == occupation, 'Extent'].iloc[0]
            
            # Check if ratings is a string representation of a list
            if isinstance(ratings_str, str) and '[' in ratings_str:
                # Use ast.literal_eval to safely convert string representation to a list
                try:
                    return ast.literal_eval(ratings_str)
                except (ValueError, SyntaxError):
                    # If parsing fails, try a simple string split and conversion
                    ratings_str = ratings_str.strip('[]')
                    return [int(x.strip()) for x in ratings_str.split(',')]
            else:
                # If it's already a list or another format, return as is
                return ratings_str
        except (IndexError, KeyError):
            print(f"Warning: Occupation '{occupation}' not found in dataframe. Using zeros.")
            return [0] * len(attributes)
    
    # Get ratings for each job
    focal_ratings = extract_ratings(onet_job)
    target1_ratings = extract_ratings(attainable_job)
    target2_ratings = extract_ratings(dream_job)
    
    # Create a mapping from attribute to ratings
    original_order_dict = {}
    for i, attr in enumerate(attributes):
        original_order_dict[attr] = (focal_ratings[i], target1_ratings[i], target2_ratings[i])
    
    # Reorder the ratings according to value_order
    reordered_focal = []
    reordered_target1 = []
    reordered_target2 = []
    
    for attr in value_order:
        if attr in original_order_dict:
            ratings = original_order_dict[attr]
            reordered_focal.append(ratings[0])
            reordered_target1.append(ratings[1])
            reordered_target2.append(ratings[2])
        else:
            print(f"Warning: Value '{attr}' not found in attributes. Skipping.")
            reordered_focal.append(0)
            reordered_target1.append(0)
            reordered_target2.append(0)
    
    # Define x positions for jobs with greater spacing to accommodate larger circles
    x_focal = [1] * len(value_order)
    x_target1 = [2.5] * len(value_order)  # Increased spacing between columns
    x_target2 = [4] * len(value_order)    # Further increased spacing for last column
    
    # Normalize ratings for circle sizes - KEEPING ORIGINAL LARGE SIZE as requested
    all_ratings = reordered_focal + reordered_target1 + reordered_target2
    max_rating = max(all_ratings) if any(all_ratings) else 1  # Avoid division by zero
    size_scale = 500 * 1.5  # Original large scaling factor
    
    sizes_focal = [s / max_rating * size_scale for s in reordered_focal]
    sizes_target1 = [s / max_rating * size_scale for s in reordered_target1]
    sizes_target2 = [s / max_rating * size_scale for s in reordered_target2]
    
    # Create plot with MUCH more horizontal space to accommodate large circles
    fig, ax = plt.subplots(figsize=(12, 8))  # Increased width and height for better spacing
    
    # Calculate the maximum circle radius in data units for buffer calculation
    max_circle_size = max(max(sizes_focal), max(sizes_target1), max(sizes_target2)) if sizes_focal else 0
    # Convert circle size to estimated radius in data units (approximate conversion)
    max_radius = np.sqrt(max_circle_size / np.pi) * 0.03  # Conversion factor from scatter size to data units
    
    # Set up expanded x-axis range to prevent cutoff
    buffer = max_radius * 2  # Buffer based on largest circle
    ax.set_xlim(min(x_focal) - buffer, max(x_target2) + buffer)
    
    # Increase bottom margin to accommodate both role types and job titles
    plt.subplots_adjust(left=0.25, right=0.85, top=0.95, bottom=0.3)  # Increased bottom margin
    
    # Add padding to y-axis to prevent cutoff
    y_padding = max_radius + 0.2  # Add extra padding based on circle size
    ax.set_ylim(-y_padding, len(value_order) - 1 + y_padding)
    
    # Scatter plot with variable circle sizes
    ax.scatter(x_focal, range(len(value_order)), s=sizes_focal, color="#1f77b4", alpha=0.7, label=onet_job)
    ax.scatter(x_target1, range(len(value_order)), s=sizes_target1, color="#2ca02c", alpha=0.7, label=attainable_job)
    ax.scatter(x_target2, range(len(value_order)), s=sizes_target2, color="#d62728", alpha=0.7, label=dream_job)
    
    # Label y-axis with attributes (in user's order)
    ax.set_yticks(range(len(value_order)))
    if custom_font:
        ax.set_yticklabels(value_order, fontproperties=custom_font, fontsize=11)
    else:
        ax.set_yticklabels(value_order, fontsize=11)
    
    # Function to abbreviate and wrap long job titles
    def format_job_title(title, max_length=15):
        # If title is shorter than max_length, return as is
        if len(title) <= max_length:
            return title
        
        # Otherwise, split into multiple lines
        words = title.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_length:
                current_line += (" " + word if current_line else word)
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
            
        return '\n'.join(lines)
    
    # Format job titles to prevent overlap
    formatted_onet_job = format_job_title(onet_job)
    formatted_attainable_job = format_job_title(attainable_job)
    formatted_dream_job = format_job_title(dream_job)
    
    # ---------- CHANGES BEGIN HERE ----------
    # Use role types as x-tick labels instead of job titles
    roles = ["Current/Most Recent Role", "Attainable Role", "Dream Role"]
    x_positions = [1, 2.5, 4]  # Same as x-ticks
    
    # Set x-tick labels as the role types
    ax.set_xticks(x_positions)
    
    if custom_font:
        ax.set_xticklabels(roles, fontproperties=custom_font, fontsize=11)
    else:
        ax.set_xticklabels(roles, fontsize=9.5)
    
    # Add more padding below x-axis for job titles
    ax.tick_params(axis='x', pad=15)
    
    # Add the actual job titles below the role types
    for i, (job_title, x_pos) in enumerate(zip([formatted_onet_job, formatted_attainable_job, formatted_dream_job], x_positions)):
        if custom_font:
            ax.text(x_pos, -0.15, job_title, 
                   ha='center', 
                   va='top',
                   transform=ax.get_xaxis_transform(),  # Use axis coordinates
                   fontproperties=custom_font, 
                   fontsize=11)  # Slightly bigger font for job titles
        else:
            ax.text(x_pos, -0.15, job_title, 
                   ha='center', 
                   va='top',
                   transform=ax.get_xaxis_transform(),  # Use axis coordinates
                   fontsize=11)  # Slightly bigger font for job titles
    
    # Remove border around the plotting area
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add padding between y-axis labels and plot area
    ax.tick_params(axis='y', pad=20)  # Increased padding for better separation
    
    # Remove tick marks on both axes
    ax.tick_params(axis='both', which='both', length=0)
    
    # Invert y-axis for better readability (highest priority at top)
    plt.gca().invert_yaxis()
    
    # Add grid lines for better readability
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    
    # Save the figure with high DPI
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"✅ Value Graph saved: {output_path}")
    
    # Close the figure to free memory
    plt.close(fig)